from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_department_options_alter_location_options_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='location',
            old_name='state',
            new_name='province',
        ),
    ]
