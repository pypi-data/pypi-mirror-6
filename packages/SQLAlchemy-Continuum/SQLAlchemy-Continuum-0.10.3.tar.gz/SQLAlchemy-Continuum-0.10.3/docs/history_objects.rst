History objects
===============


Operation types
---------------

When changing entities and committing results into database Continuum saves the used
operations (INSERT, UPDATE or DELETE) into version entities. The operation types are stored
by default to a small integer field named 'operation_type'. Class called 'Operation' holds
convenient constants for these values as shown below:

::


    from sqlalchemy_continuum import Operation

    article = Article(name=u'Some article')
    session.add(article)
    session.commit()

    article.versions[0].operation_type == Operation.INSERT

    article.name = u'Some updated article'
    session.commit()
    article.versions[1].operation_type == Operation.UPDATE

    session.delete(article)
    session.commit()
    article.versions[2].operation_type == Operation.DELETE



Version traversal
-----------------

::

    first_version = article.versions[0]
    first_version.index
    # 0


    second_version = first_version.next
    assert second_version == article.versions[1]

    second_version.previous == first_version
    # True

    second_version.index
    # 1


Changeset
---------

Continuum provides easy way for getting the changeset of given version object. Each version contains a changeset
property which holds a dict of changed fields in that version.

::


    article = Article(name=u'New article', content=u'Some content')
    session.add(article)
    session.commit(article)

    version = article.versions[0]
    version.changeset
    # {
    #   'id': [None, 1],
    #   'name': [None, u'New article'],
    #   'content': [None, u'Some content']
    # }
    article.name = u'Updated article'
    session.commit()

    version = article.versions[1]
    version.changeset
    # {
    #   'name': [u'New article', u'Updated article'],
    # }

    session.delete(article)
    version = article.versions[1]
    version.changeset
    # {
    #   'id': [1, None]
    #   'name': [u'Updated article', None],
    #   'content': [u'Some content', None]
    # }


SQLAlchemy-Continuum also provides a utility function called changeset. With this function
you can easily check the changeset of given object in current transaction.



::


    from sqlalchemy_continuum import changeset


    article = Article(name=u'Some article')
    changeset(article)
    # {'name': [u'Some article', None]}


Version relationships
---------------------

Each version object reflects all parent object relationships. You can think version object relations as 'relations of parent object in given point in time'.

Lets say you have two models: Article and Category. Each Article has one Category. In the following example we first add article and category objects into database.

Continuum saves new ArticleHistory and CategoryHistory records in the background. After that we update the created article entity to use another category. Continuum creates new version objects accordingly.

Lastly we check the category relations of different article versions.


::


    category = Category(name=u'Some category')
    article = Article(
        name=u'Some article',
        category=category
    )
    session.add(article)
    session.commit()

    article.category = Category(name=u'Some other category')
    session.commit()


    article.versions[0].category.name = u'Some category'
    article.versions[1].category.name = u'Some other category'
