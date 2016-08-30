from __future__ import unicode_literals

from django.db import models


class ProductsPermissions(models.Model):
    permission_group = models.CharField(max_length=200)                 # VARCHAR(2000) NOT NULL, -- plain (eg 'sonae')
    webshop_id = models.CharField(max_length=50)                        # VARCHAR(50) NOT NULL
    country_code = models.CharField(max_length=5)                       # VARCHAR(2) NOT NULL
    enabled = models.BooleanField()                                     # BOOLEAN NOT NULL

    class Meta:
        unique_together = (('permission_group', 'webshop_id', 'country_code'),)
        db_table = 'test.products_permissions'
        managed = False


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

