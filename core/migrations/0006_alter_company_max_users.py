import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_rename_gstin_company_tin'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='max_users',
            field=models.IntegerField(
                default=25,
                help_text='Maximum number of users allowed (max 25)',
                validators=[django.core.validators.MaxValueValidator(25)],
            ),
        ),
    ]
