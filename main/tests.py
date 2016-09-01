from django.test import TestCase
from django.db import models, connections
from django.db.models import Max
from django.db.utils import DatabaseError

"""
CREATE OR REPLACE TABLE PERMISSIONS.products_permissions
-- one entry for each permission_group/webshop/country
(
       id INTEGER,
       permission_group VARCHAR(2000) NOT NULL, -- plain (eg 'sonae')
       webshop_id VARCHAR(50) NOT NULL,
       country_code VARCHAR(2) NOT NULL,
       enabled BOOLEAN NOT NULL,

       -- ensure uniqueness of permission_group/webshop/country
       PRIMARY KEY (permission_group, webshop_id, country_code)
);
"""


# model for testing db writes
class TestProductsPermissions(models.Model):
    permission_group = models.CharField(max_length=200)                 # VARCHAR(2000) NOT NULL, -- plain (eg 'sonae')
    webshop_id = models.CharField(max_length=50)                        # VARCHAR(50) NOT NULL
    country_code = models.CharField(max_length=5)                       # VARCHAR(2) NOT NULL
    enabled = models.BooleanField()                                     # BOOLEAN NOT NULL

    class Meta:
        unique_together = (('permission_group', 'webshop_id', 'country_code'),)
        db_table = 'test.products_permissions'
        managed = False


# router for testing db writes


class DbWriteTest(TestCase):

    connection = 'exasol_db'

    create_table = """
        CREATE OR REPLACE TABLE "TEST"."PRODUCTS_PERMISSIONS"
        -- one entry for each permission_group/webshop/country
        (
               ID INTEGER IDENTITY,
               PERMISSION_GROUP VARCHAR(2000) NOT NULL, -- plain (eg 'sonae')
               WEBSHOP_ID VARCHAR(50) NOT NULL,
               COUNTRY_CODE VARCHAR(2) NOT NULL,
               ENABLED BOOLEAN NOT NULL,

               -- ensure uniqueness of permission_group/webshop/country
               PRIMARY KEY (PERMISSION_GROUP, WEBSHOP_ID, COUNTRY_CODE)
        );
    """

    drop_table = """
        DROP TABLE IF EXISTS "TEST"."PRODUCTS_PERMISSIONS"
    """

    def setUp(self):
        print "connecting to", connections[self.connection].get_connection_params()
        print "creating table"
        super(DbWriteTest, self).setUp()
        cursor = connections[self.connection].cursor()
        cursor.execute(self.__class__.create_table)


    def tearDown(self):
        print "dropping table"
        super(DbWriteTest, self).tearDown()
        cursor = connections[self.connection].cursor()
        cursor.execute(self.__class__.drop_table)

    def _insert_element(self, webshop_id, country_code, permission_group, enabled):
        print "inserting element (", webshop_id, country_code, permission_group, enabled,")"
        p = TestProductsPermissions()
        p.webshop_id = webshop_id
        p.country_code = country_code
        p.permission_group = permission_group
        p.enabled = enabled
        p.save()
        print "inserted with id", p.id
        return p.id

    def _insert_some_data(self):
        sample_data = [
            ['nike', 'us', 'pg1', True],
            ['nike', 'es', 'pg1', True],
            ['adidas', 'us', 'pg1', False],
            ['adidas', 'ru', 'pg1', False],
            ['adidas', 'pt', 'pg1', False],
            ['nike', 'us', 'pg2', True],
            ['nike', 'es', 'pg2', True],
            ['adidas', 'us', 'pg2', False],
            ['adidas', 'ru', 'pg2', False],
            ['adidas', 'pt', 'pg2', False],
        ]

        row_ids = set()
        for d in sample_data:
            row_id = self._insert_element(*d)
            self.assertNotIn(row_id, row_ids, "repeated id %d" % row_id)
            row_ids.add(row_id)

        return len(sample_data)

    def test_write_read_simple(self):
        permissions = TestProductsPermissions.objects.all()
        items = list(permissions)
        self.assertEqual(len(items), 0)

        inserted_count = self._insert_some_data()

        permissions = TestProductsPermissions.objects.all()
        self.assertEqual(inserted_count, permissions.count())

        self._insert_element('elcorteingles','es','pg3',True)
        self.assertEqual(inserted_count+1, TestProductsPermissions.objects.all().count())

    def test_write_and_return_identity(self):

        # insert some data
        TestProductsPermissions(webshop_id='w1', country_code='c1',permission_group='pg1', enabled=True).save()
        TestProductsPermissions(webshop_id='w2', country_code='c2',permission_group='pg2', enabled=True).save()
        TestProductsPermissions(webshop_id='w3', country_code='c3',permission_group='pg3', enabled=True).save()

        max_id = TestProductsPermissions.objects.aggregate(max_id=Max('id'))['max_id']

        p = TestProductsPermissions()
        p.webshop_id = 'lululemon'
        p.country_code = 'ch'
        p.permission_group = 'pg100'
        p.enabled = True
        p.save()

        self.assertGreater(p.id, max_id)

    def test_write_integrity_error(self):
        inserted_count = self._insert_some_data()

        p1 = TestProductsPermissions()
        p1.webshop_id = 'lululemon'
        p1.country_code = 'ch'
        p1.permission_group = 'pg100'
        p1.enabled = True
        p1.save()

        self.assertEqual(TestProductsPermissions.objects.all().count(), 1 + inserted_count)

        try:
            with self.assertRaisesRegexp(DatabaseError, "constraint violation - primary key"):
                p2 = TestProductsPermissions()
                p2.webshop_id = 'lululemon'
                p2.country_code = 'ch'
                p2.permission_group = 'pg100'
                p2.enabled = False
                p2.save()
        except DatabaseError:
            print "database error"

        self.assertEqual(TestProductsPermissions.objects.all().count(), 1 + inserted_count)

    def test_delete_all(self):
        inserted_count = self._insert_some_data()
        permissions = TestProductsPermissions.objects.all()
        self.assertEqual(inserted_count, permissions.count())

        TestProductsPermissions.objects.all().delete()
        self.assertEqual(TestProductsPermissions.objects.all().count(), 0)

