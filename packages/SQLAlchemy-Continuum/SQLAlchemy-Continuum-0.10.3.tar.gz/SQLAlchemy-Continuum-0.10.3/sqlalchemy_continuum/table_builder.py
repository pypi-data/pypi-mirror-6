import sqlalchemy as sa


class TableBuilder(object):
    """
    TableBuilder handles the building of history tables based on parent
    table's structure and versioning configuration options.
    """
    def __init__(
        self,
        versioning_manager,
        parent_table,
        model=None
    ):
        self.manager = versioning_manager
        self.parent_table = parent_table
        self.model = model

    def option(self, name):
        return self.manager.option(self.model, name)

    @property
    def table_name(self):
        """
        Returns the history table name for current parent table.
        """
        return self.option('table_name') % self.parent_table.name

    @property
    def reflected_columns(self):
        """
        Returns reflected parent table columns.

        All columns from parent table are reflected except those that:
        1. Are auto assigned date or datetime columns. Use include option
        parameter if you wish to have these included.
        2. Columns that are part of exclude option parameter.
        """
        columns = []

        transaction_column_name = self.option('transaction_column_name')

        for column in self.parent_table.c:
            if self.manager.is_excluded_column(self.model, column):
                continue

            column_copy = self.reflect_column(column)
            columns.append(column_copy)
            if (
                self.option('track_property_modifications') and
                not column.primary_key
            ):
                columns.append(
                    sa.Column(
                        column_copy.name + self.option('modified_flag_suffix'),
                        sa.Boolean,
                        key=(
                            column_copy.key +
                            self.option('modified_flag_suffix')
                        ),
                        default=False,
                        nullable=False
                    )
                )

        # When using join table inheritance each table should have own
        # transaction column.
        if transaction_column_name not in [c.key for c in columns]:
            columns.append(sa.Column(transaction_column_name, sa.BigInteger))

        return columns

    def reflect_column(self, column):
        """
        Make a copy of parent table column and some alterations to it.

        :param column: SQLAlchemy Column object of parent table
        """
        # Make a copy of the column so that it does not point to wrong
        # table.
        column_copy = column.copy()
        # Remove unique constraints
        column_copy.unique = False
        # Remove onupdate triggers
        column_copy.onupdate = None
        if column_copy.autoincrement:
            column_copy.autoincrement = False
        if column_copy.name == self.option('transaction_column_name'):
            column_copy.nullable = False

        if not column_copy.primary_key:
            column_copy.nullable = True

        # Find the right column key
        if self.model is not None:
            for key, value in sa.inspect(self.model).columns.items():
                if value is column:
                    column_copy.key = key
        return column_copy

    @property
    def operation_type_column(self):
        """
        Return the operation type column. By default the name of this column
        is 'operation_type'.
        """
        return sa.Column(
            self.option('operation_type_column_name'),
            sa.SmallInteger,
            nullable=False
        )

    @property
    def transaction_column(self):
        """
        Returns transaction column. By default the name of this column is
        'transaction_id'.
        """
        return sa.Column(
            self.option('transaction_column_name'),
            sa.BigInteger,
            primary_key=True,
            autoincrement=False  # This is needed for MySQL
        )

    @property
    def end_transaction_column(self):
        """
        Returns end_transaction column. By default the name of this column is
        'end_transaction_id'.
        """
        return sa.Column(
            self.option('end_transaction_column_name'),
            sa.BigInteger
        )

    def __call__(self, extends=None):
        """
        Builds history table.
        """
        items = []
        if extends is None:
            items.extend(self.reflected_columns)
            items.append(self.transaction_column)
            if self.option('strategy') == 'validity':
                items.append(self.end_transaction_column)
            items.append(self.operation_type_column)
        return sa.schema.Table(
            extends.name if extends is not None else self.table_name,
            self.parent_table.metadata,
            *items,
            extend_existing=extends is not None
        )
