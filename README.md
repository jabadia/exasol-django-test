# Steps
Create a virtual env for this test project. Install:
Django==1.9.2
django_exabackend
pyodbc==3.0.10

1. create a new Django project (using pycharm)
2. configure exasol driver in settings.py
3. create an 'app' inside the project
```
    $ python manage.py startapp main    
```
navigating to http://127.0.0.1/main/ should give you an 'hi there!' message

4. manually create the following table in the testing EXAsol instance

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

and insert some test data

    DELETE FROM TEST.PRODUCTS_PERMISSIONS WHERE 1=1;
    INSERT INTO TEST.PRODUCTS_PERMISSIONS 
    (webshop_id, country_code, permission_group, enabled)
    values
    ('nike', 'us', 'pg1', TRUE),
    ('nike', 'es', 'pg1', TRUE),
    ('adidas', 'us', 'pg1', FALSE),
    ('adidas', 'ru', 'pg1', FALSE),
    ('adidas', 'pt', 'pg1', FALSE),
    ('nike', 'us', 'pg2', TRUE),
    ('nike', 'es', 'pg2', TRUE),
    ('adidas', 'us', 'pg2', FALSE),
    ('adidas', 'ru', 'pg2', FALSE),
    ('adidas', 'pt', 'pg2', FALSE);

5. create a model 'managed=False' so that Django doesn't try to mess with the table definition (main/models.py)

6. check that it is working by navigating to http://127.0.0.1/main/rows/ (main/views.py)

7. use the unit testing capabilities of django (main/test.py)
```
    $ python manage.py test    
```