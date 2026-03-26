from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_rename_tax_id_company_ipa_registration'),
    ]

    operations = [
        migrations.RenameField(
            model_name='company',
            old_name='gstin',
            new_name='tin',
        ),
    ]
