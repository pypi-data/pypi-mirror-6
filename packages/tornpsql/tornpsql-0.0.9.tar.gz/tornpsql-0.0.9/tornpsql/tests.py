import unittest
import tornpsql
import os
from decimal import Decimal


class tornpsqlTests(unittest.TestCase):
    def test_one(self):
        user = os.getenv("TORNPSQL_USERNAME")
        host = os.getenv("TORNPSQL_HOST")
        database = os.getenv("TORNPSQL_DATABASE")
        db = tornpsql.Connection(host, database, user)
        # assert database connection
        self.assertEquals(db._db.closed, 0)
        db.execute("DROP TABLE IF EXISTS tornpsql_test;")
        createtable = db.execute("CREATE TABLE tornpsql_test (id int, name varchar);")
        self.assertEquals(createtable, None)

        # single insert
        insert1 = db.execute("INSERT INTO tornpsql_test values (%s, %s) returning id;", 1, 'Steve')
        self.assertListEqual(insert1, [{'id': 1}])
        insert2 = db.execute("INSERT INTO tornpsql_test values (%s, %s) returning id, name;", 2, 'Steve')
        self.assertListEqual(insert2, [{'id': 2, 'name': 'Steve'}])
        insert3 = db.get("INSERT INTO tornpsql_test values (%s, %s) returning id;", 3, 'Steve')
        self.assertDictEqual(insert3, {'id': 3})
        insert4 = db.query("INSERT INTO tornpsql_test values (%s, %s) returning id;", 4, 'Steve')
        self.assertListEqual(insert4, [{'id': 4}])
        db.executemany("insert into tornpsql_test (id, name) values (%s, %s) returning id",
                       (5, 'Joe'),
                       [6, "Eric"],
                       (7, "Shawn"))

        # select
        select1 = db.query("select * from tornpsql_test where id=%s;", 1)
        self.assertListEqual(select1, [{'id': 1, 'name': 'Steve'}])
        select2 = db.query("select distinct name from tornpsql_test;")
        self.assertListEqual(select2, [{'name': 'Shawn'}, {'name': 'Eric'}, {'name': 'Joe'}, {'name': 'Steve'}])

        # drop the database
        droptable = db.execute("DROP TABLE tornpsql_test;")
        self.assertEquals(droptable, None)

        # close
        db.close()
        self.assertEquals(db._db, None)

    def test_two(self):
        user = os.getenv("TORNPSQL_USERNAME")
        host = os.getenv("TORNPSQL_HOST")
        database = os.getenv("TORNPSQL_DATABASE")
        url = "postgres://%s:@%s:5432/%s" % (user, host, database)
        # connect via url method
        db = tornpsql.Connection(url)
        self.assertEquals(db._db.closed, 0)
        del db

    def test_three(self):
        db = tornpsql.Connection(os.getenv("TORNPSQL_HOST"), os.getenv("TORNPSQL_DATABASE"), os.getenv("TORNPSQL_USERNAME"))
        db.execute("create extension if not exists hstore;")
        db.execute("create table if not exists hstore_test (demo hstore);")
        d = dict(value1="1", value2="2", value3="eric da man")
        self.assertEqual(db.hstore(d), '"value3"=>"eric da man","value2"=>"2","value1"=>"1"')
        db.execute("insert into hstore_test values (%s);", db.hstore(d))
        self.assertDictEqual(db.get("SELECT demo from hstore_test limit 1;").demo, d)

    def test_four(self):
        db = tornpsql.Connection(os.getenv("TORNPSQL_HOST"), os.getenv("TORNPSQL_DATABASE"), os.getenv("TORNPSQL_USERNAME"))
        db.execute("create table if not exists test_money (x money);")
        db.execute("insert into test_money values (5.99::money);")
        money = db.get("select x from test_money limit 1;").x
        self.assertEqual(money, Decimal("5.99"))
        self.assertTrue(isinstance(money, Decimal))

if __name__ == '__main__':
    unittest.main()
