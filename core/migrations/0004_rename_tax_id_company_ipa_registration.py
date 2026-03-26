from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_rename_state_company_province'),
    ]

    operations = [
        migrations.RenameField(
            model_name='company',
            old_name='tax_id',
            new_name='ipa_registration',
        ),
    ]
