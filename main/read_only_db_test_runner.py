from collections import OrderedDict

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import connections
from django.test.runner import get_unique_databases_and_mirrors, DiscoverRunner


def overriden_setup_databases(verbosity, interactive, keepdb=False, debug_sql=False, parallel=0, read_only_databases=[], **kwargs):
    """
    Creates the test databases.
    This function has been copied and pasted :-( from django.test.runner.setup_databases() and modified only to
    remove from the list of test_databases those found in the READ_ONLY_DATABASES setting passed as parameter
    Had setup_databases() and get_unique_databases_and_mirrors() functions been methods of DiscoverRunner class
    we could have overridden them instead of having copy-and-pasted the code
    """
    test_databases, mirrored_aliases = get_unique_databases_and_mirrors()

    # BEGIN - THIS IS ADDED WITH RESPECT TO THE ORIGINAL CODE #
    # remove read_only_databases from test_databases
    test_databases = OrderedDict([
        (signature, (db_name, aliases))
        for (signature, (db_name, aliases)) in test_databases.items()
        if not aliases.intersection(read_only_databases)])
    # END - THIS IS ADDED WITH RESPECT TO THE ORIGINAL CODE #

    old_names = []

    for signature, (db_name, aliases) in test_databases.items():
        first_alias = None
        for alias in aliases:
            connection = connections[alias]
            old_names.append((connection, db_name, first_alias is None))

            # Actually create the database for the first connection
            if first_alias is None:
                first_alias = alias
                connection.creation.create_test_db(
                    verbosity=verbosity,
                    autoclobber=not interactive,
                    keepdb=keepdb,
                    # JAMI: TODO: For some reason our app database can't be serialized. Passing True in the following
                    # parameter causes an exception to be raised because model dependencies can't be resolved
                    # (don't know exactly what does it mean)
                    serialize=False,  # connection.settings_dict.get("TEST", {}).get("SERIALIZE", True),
                )
                if parallel > 1:
                    for index in range(parallel):
                        connection.creation.clone_test_db(
                            number=index + 1,
                            verbosity=verbosity,
                            keepdb=keepdb,
                        )
            # Configure all other connections as mirrors of the first one
            else:
                connections[alias].creation.set_as_test_mirror(
                    connections[first_alias].settings_dict)

    # Configure the test mirrors.
    for alias, mirror_alias in mirrored_aliases.items():
        connections[alias].creation.set_as_test_mirror(
            connections[mirror_alias].settings_dict)

    if debug_sql:
        for alias in connections:
            connections[alias].force_debug_cursor = True

    return old_names


class ReadOnlyDatabasesTestRunner(DiscoverRunner):
    """
    Test Runner that supports read-only databases. No TEST database will be created for those read-only dbs.
    They can be accessed from test cases using the usual models.
    """
    def setup_databases(self, **kwargs):
        print "Setting up databases"
        try:
            read_only_databases = settings.READ_ONLY_DATABASES
            print "Read only databases (no TEST db will be created):", ', '.join(read_only_databases)
            return overriden_setup_databases(
                self.verbosity, self.interactive, self.keepdb, self.debug_sql,
                self.parallel, read_only_databases, **kwargs
            )

        except AttributeError:
            raise ImproperlyConfigured("Should configure a list of READ_ONLY_DATABASES in settings")

    def teardown_databases(self, old_config, **kwargs):
        print "Tearing down databases"
        super(ReadOnlyDatabasesTestRunner, self).teardown_databases(old_config, **kwargs)
