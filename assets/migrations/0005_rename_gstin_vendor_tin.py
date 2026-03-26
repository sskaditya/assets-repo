from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0004_rename_state_vendor_province'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vendor',
            old_name='gstin',
            new_name='tin',
        ),
    ]
