from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auditlog_useractivitysummary'),
    ]

    operations = [
        migrations.RenameField(
            model_name='company',
            old_name='state',
            new_name='province',
        ),
    ]
