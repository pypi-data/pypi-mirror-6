from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.db import connections, router, transaction
from django.db.utils import DEFAULT_DB_ALIAS, IntegrityError
from django.test.testcases import TestCase
from south.db import dbs as south_dbs

from ..models.model import ModelDefinition


class DDLTestCase(TestCase):
    """
    A class that behaves like `TestCase` if all connections support DDL
    transactions or like `TransactionTestCase` if it's not the case.
    """
    manual_transaction = False

    def connections_have_ddl_transactions(self):
        """
        Returns True if all implied connections have DDL transactions support.
        """
        db_names = connections if getattr(self, 'multi_db', False) else [DEFAULT_DB_ALIAS]
        return all(south_dbs[name].has_ddl_transactions for name in db_names)

    def _fixture_setup(self):
        if (not self.manual_transaction and
            self.connections_have_ddl_transactions()):
            return super(DDLTestCase, self)._fixture_setup()
        else:
            return super(TestCase, self)._fixture_setup()

    def _fixture_teardown(self):
        if (not self.manual_transaction and
            self.connections_have_ddl_transactions()):
            return super(DDLTestCase, self)._fixture_teardown()
        else:
            return super(TestCase, self)._fixture_teardown()


class ModelDefinitionDDLTestCase(DDLTestCase):
    def tearDown(self):
        if (self.manual_transaction or
            not self.connections_have_ddl_transactions()):
            # Remove all the extra tables since `TransactionTestCase` only
            # truncate data on teardown.
            ModelDefinition.objects.all().delete()
        ContentType.objects.clear_cache()


class FieldDefinitionTestMixin(object):
    field_definition_init_kwargs = {}
    field_values = ()

    def setUp(self):
        super(FieldDefinitionTestMixin, self).setUp()
        with self.assertChecksumChange():
            self.field = self.field_definition_cls._default_manager.create(
                model_def=self.model_def, name='field',
                **self.field_definition_init_kwargs
            )

    def get_field_value(self, instance, name='field'):
        return getattr(instance, name)

    def prepare_default_value(self, value):
        return value

    def test_field_default(self):
        default = self.prepare_default_value(self.field_values[0])
        field = self.field
        # Default value should be valid
        with self.assertChecksumChange():
            field.default = default
            field.full_clean()
            field.save()
        # Default value should be assigned correctly
        model_class = self.model_def.model_class()
        instance = model_class.objects.create()
        field_value = self.get_field_value(instance)
        created_default = self.prepare_default_value(field_value)
        self.assertEqual(created_default, default)

    def test_create_with_default(self):
        """Makes sure a field definition manager is attached to the model and
        `create_with_default` works correctly."""
        model_class = self.model_def.model_class()
        field_value = self.field_values[0]
        instance = model_class.objects.create(field=field_value)
        # Add the field with a default.
        create_default = self.prepare_default_value(field_value)
        options = dict(**self.field_definition_init_kwargs)
        options['default'] = create_default
        with self.assertChecksumChange():
            self.field_definition_cls._default_manager.create_with_default(
                model_def=self.model_def, name='field_created_with_default',
                **options
            )
        created_value = self.prepare_default_value(
            model_class.objects.get(pk=instance.pk).field_created_with_default
        )
        self.assertEqual(created_value, create_default)

    def test_model_save(self):
        first_value, second_value = self.field_values
        # Assigning a value should work
        model_class = self.model_def.model_class()
        instance = model_class.objects.create(field=first_value)
        self.assertEqual(self.get_field_value(instance), first_value)
        # Assigning a new one should also work
        instance.field = second_value
        instance.save()
        instance = model_class.objects.get()
        self.assertEqual(self.get_field_value(instance), second_value)

    def test_field_renaming(self):
        value = self.field_values[0]
        model_class = self.model_def.model_class()
        # Renaming a field should update its column name
        model_class.objects.create(field=value)
        opts = model_class._meta
        original_column_name = opts.get_field('field').get_attname_column()[1]
        with self.assertChecksumChange():
            self.field.name = 'renamed_field'
            self.field.save()
        opts = model_class._meta
        new_column_name = opts.get_field('renamed_field').get_attname_column()[1]
        self.assertModelTablesColumnDoesntExists(
            model_class, original_column_name
        )
        self.assertModelTablesColumnExists(
            model_class, new_column_name
        )
        # Old data should be accessible by the new field name
        instance = model_class.objects.get()
        self.assertEqual(self.get_field_value(instance, 'renamed_field'), value)
        # The old field shouldn't be accessible anymore
        msg = "'field' is an invalid keyword argument for this function"
        self.assertRaisesMessage(TypeError, msg, model_class, field=value)
        # It should be possible to create objects using the new field name
        model_class.objects.create(renamed_field=value)

    def test_field_deletion(self):
        value = self.field_values[0]
        model_class = self.model_def.model_class()
        model_class.objects.create(field=value)
        # Deleting a field should delete the associated column
        opts = model_class._meta
        field_column_name = opts.get_field('field').get_attname_column()[1]
        with self.assertChecksumChange():
            self.field.delete()
        self.assertModelTablesColumnDoesntExists(model_class, field_column_name)
        # The deleted field shouldn't be accessible anymore
        msg = "'field' is an invalid keyword argument for this function"
        self.assertRaisesMessage(TypeError, msg, model_class, field=value)

    def test_field_unique(self):
        value = self.field_values[0]
        model_class = self.model_def.model_class()
        with self.assertChecksumChange():
            self.field.unique = True
            self.field.save()
        model_class.objects.create(field=value)
        write_db = router.db_for_write(model_class)
        connection = connections[write_db]
        # TODO: Convert this to `atomic` once support for Django < 1.6 is dropped
        sid = transaction.savepoint(using=write_db)
        try:
            model_class.objects.create(field=value)
        except IntegrityError:
            pass
        else:
            self.fail("One shouldn't be able to save duplicate entries in a unique field")
        finally:
            connection.needs_rollback = False
            transaction.savepoint_rollback(sid, using=write_db)

    def test_field_cloning(self):
        with self.assertChecksumChange():
            clone = self.field.clone()
            clone.name = 'field_clone'
            clone.model_def = self.model_def
            clone.save(force_insert=True)

    def test_field_definition_category(self):
        self.assertEqual(
            self.field_definition_cls.get_field_category(),
            self.field_definition_category
        )
