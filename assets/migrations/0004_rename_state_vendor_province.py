from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0003_remove_category_type_field'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vendor',
            old_name='state',
            new_name='province',
        ),
    ]
