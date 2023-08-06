Data sources
============

*pygrametl* has support for numerous data sources. Data in pygrametl is moved around in rows, so instead of implementing a row class, pygrametl utilizes Python's built in dictionaries. Each of the data sources in this class, are iterable and provide *dicts* with data values. Implementing your own data sources in pygrametl is easy, as the only requirement is that the data source is iterable, i.e. defining the :meth:`__iter__` method. As such, it should be possible to do the following:

.. code-block:: python

   for row in datasource:
       ...

As a default, pygrametl has a number of built-in data types:

SQLSource
---------

The class :class:`.SQLSource` is a data source used to iterate the results of a single SQL query. The data source accepts only a :PEP:`249` connection, and not a :class:`.ConnectionWrapper` object. For illustrative purposes, a PostgreSQL connection is used here, using the Psycopg package. 

.. code-block:: python

    import psycopg2
    import pygrametl
    from pygramet.datasources import SQLSource

    conn = psycopg2.connect(database="test", user="postgres", password="secret")

    resultsSource = SQLSource(conn, "SELECT * FROM table")

In the above example, an SQLSource is created in order to extract all rows from a table.

A tuple of attribute names can also be supplied as a parameter, if preferable, which will be used instead of the attribute names from the table. Naturally, the number of supplied names must match the number of names in the query result from the database:

.. code-block:: python

    ...
    newnames = 'ID', 'Name', 'Price'
    resultsSource = SQLSource(conn, "SELECT * FROM table", names=newnames)

The class also makes it possible to supply an SQL expression that will be executed before the query, through the initsql parameter. The result of the expression will not be returned.

.. code-block:: python

    ...
    resultsSource = SQLSource(conn, "SELECT * FROM newview", 
        initsql="CREATE VIEW newview AS SELECT ID, Name FROM table WHERE Price > 10")

In the previous example a new view is created, which is then used in the query.

CSVSource
---------

The class :class:`.CSVSource` is a data source returning the lines of a delimiter-separated file, turned into dictionaries. The class is fairly simple, and is implemented as a reference to `csv.DictReader <http://docs.python.org/2/library/csv.html#csv.DictReader>`_ in the Python Standard Library. An example of the usage of this class can be seen below, in which a file containing comma-separated values is loaded:

.. code-block:: python

    import pygrametl
    from pygrametl.datasources import CSVSource

    resultsSource = CSVSource(open('ResultsFile.csv', 'r', 16384), delimiter=',')

In the above example, a CSVSource is created from a file delimited by commas, using a buffer size of 16384.

Joins
-----

In addition to the aforementioned data sources, pygrametl also includes a number of ways to join and combine existing data sources.

The class :class:`.MergeJoiningSource` can be used to equijoin rows from two data sources. The rows of the two data sources which are to be merged, must deliver their rows in sorted order. It is also necessary to supply the common attributes on which the join must be performed.

.. code-block:: python

    import pygrametl
    from pygrametl.datasources import CSVSource, MergeJoiningSource

    products = CSVSource(open('products.csv', 'r', 16384), delimiter=',')
    sales = CSVSource(open('sales.txt', 'r', 16384), delimiter='\t')

    data = MergeJoiningSource(products, 'productID',
                              sales, 'productID')

In the above example, the class is used to join two sources on a common attribute *productID*.

The class :class:`.HashJoiningSource` functions similarly to :class:`.MergeJoiningSource`, but performs the join using a hash map instead. As such, it is not necessary for the two input data sources to be sorted.

Unions
------

It is also possible to union different data sources together in pygrametl.
The class :class:`.UnionSource` creates a union of a number of supplied data sources. The data sources do not necessarily have to contain the same types of rows.

.. code-block:: python

    import pygrametl
    from pygrametl.datasources import CSVSource, UnionSource

    salesOne = CSVSource(open('sales1.csv', 'r', 16384), delimiter='\t')
    salesTwo = CSVSource(open('sales2.csv', 'r', 16384), delimiter='\t')
    salesThree = CSVSource(open('sales3.csv', 'r', 16384), delimiter=',')

    combinedSales = UnionSource(salesOne, salesTwo, salesThree)

The data sources are read in their entirety, i.e. every row is read from the first source before rows are read from the second source. It can also be beneficial to interleave rows, and for this purpose :class:`.RoundRobinSource` can be used. 

.. code-block:: python

    import pygrametl
    from pygrametl.datasources import CSVSource, RoundRobinSource

    salesOne = CSVSource(open('sales1.csv', 'r', 16384), delimiter='\t')
    salesTwo = CSVSource(open('sales2.csv', 'r', 16384), delimiter='\t')
    salesThree = CSVSource(open('sales3.csv', 'r', 16384), delimiter=',')

    combinedSales = RoundRobinSource(salesOne, salesTwo, salesThree, batchsize=500)

As can be seen in the above example, the class takes a number of data sources along with an argument *batchsize*, corresponding to the amount of rows read from one source before reading from the next in a round-robin fashion.

.. Other
.. -----

.. CrossTabbingSource
.. ------------------

.. ProcessSource
.. -------------

.. FilteringSource
.. ---------------

.. TransformingSource
.. ------------------

.. DynamicForEachSource
.. --------------------
