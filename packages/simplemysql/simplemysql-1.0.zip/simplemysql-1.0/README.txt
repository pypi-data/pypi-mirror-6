===========
SimpleMysql
===========

An ultra simplistic wrapper for Python MySQLdb with very basic functionality

http://nadh.in/code/simplemysql

License: GPL v2

Installation
------------
``pip install simplemysql``

Usage
-----

::

	from simplemysql import SimpleMysql

	db = SimpleMysql(
			host="localhost",
			db="mydatabase",
			user="username",
			passwd="password"
	)

	# insert a record to the *books* table
	db.insert("books", {"type": "paperback", "name": "Time Machine", "price": 5.55, year: "1997"})

	book = db.getOne("books", ["name"], ["year = 1997"])

	print "The book's name is " + book.name

Query methods
-------------

insert(), update(), delete(), getOne(), getAll(), query()

insert(table, record{})
^^^^^^^^^^^^^^^^^^^^^^^
Inserts a single record into a table.

::

  db.insert("food", {"type": "fruit", "name": "Apple", "color": "red"})
  db.insert("books", {"type": "paperback", "name": "Time Machine", "price": 5.55})


update(table, row{}, condition[])
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Update one more or rows based on a condition (or no condition).

::

  # update all rows
  db.update("books", {"discount": 0})

  # update rows based on a simple hardcoded condition
  db.update("books",
          {"discount": 10},
          ["id=1"]
  )

  # update rows based on a parametrized condition
  db.update("books",
          {"discount": 10},
          ("id=%s AND year=%s", [id, year])
  )

insertOrUpdate(table, row{}, key)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Insert a new row, or update if there is a primary key conflict.

::

  # insert a book with id 123. if it already exists, update values
  db.insert("books",
                  {"id": 123, type": "paperback", "name": "Time Machine", "price": 5.55},
                  "id"
  )

getOne(table, fields[], condition[], order[], limit[])
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
getAll(table, fields[], condition[], order[], limit[])
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Get a single record or multiple records from a table given a condition (or no condition). The resultant rows are returned as namedtuples. getOne() returns a single namedtuple, and getAll() returns a list of namedtuples.

::

  book = db.getOne("books", ["id", "name"])

  # get a row based on a simple hardcoded condition
  book = db.getOne("books", ["name", "year"], ("id=1"))

  # get a row based on a simple hardcoded condition
  book = db.getOne("books", ["name", "year"], ("id=1"))

  # get multiple rows based on a parametrized condition
  books = db.getAll("books",
          ["id", "name"],
          ("year > %s and price < 15", [year, 12.99])
  )

  # get multiple rows based on a parametrized condition with an order and limit specified
  books = db.getAll("books",
          ["id", "name", "year"],
          ("year > %s and price < 15", [year, 12.99]),
          ["year", "DESC"],       # ORDER BY year DESC
          [0, 10]                 # LIMIT 0, 10
  )

delete(table, fields[], condition[], order[], limit[])
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Delete one or more records based on a condition (or no condition)

::

  # delete all rows
  db.delete("books")

  # delete rows based on a condition
  db.delete("books", ("price > %s AND year < %s", [25, 1999]))

query(table)
^^^^^^^^^^^^
Run a raw SQL query. The MySQLdb cursor is returned.

::

  db.query("DELETE FROM books WHERE year > 2005")
