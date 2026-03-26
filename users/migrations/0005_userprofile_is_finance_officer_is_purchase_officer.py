from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_location_postal_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_finance_officer',
            field=models.BooleanField(default=False, help_text='Can view assets and financial reports'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='is_purchase_officer',
            field=models.BooleanField(default=False, help_text='Can view assets, vendors and procurement reports'),
        ),
    ]
