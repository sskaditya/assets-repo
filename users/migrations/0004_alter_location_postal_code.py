from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_rename_state_location_province'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='postal_code',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
