import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_company_max_users'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='max_assets',
            field=models.IntegerField(
                default=1500,
                help_text='Maximum number of assets allowed (max 1500)',
                validators=[django.core.validators.MaxValueValidator(1500)],
            ),
        ),
    ]
