# Generated migration

from django.db import migrations, models
import django.db.models.deletion


def create_default_company(apps, schema_editor):
    """Create a default Softlogic company for existing data"""
    Company = apps.get_model('core', 'Company')
    Company.objects.get_or_create(
        code='SOFTLOGIC',
        defaults={
            'name': 'Softlogic Holdings',
            'email': 'info@softlogic.lk',
            'phone': '+94112345678',
            'city': 'Colombo',
            'state': 'Western Province',
            'country': 'Sri Lanka',
            'is_active': True,
        }
    )


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(db_index=True, default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(max_length=200, unique=True)),
                ('code', models.CharField(help_text='Unique company code', max_length=50, unique=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('website', models.URLField(blank=True, null=True)),
                ('address_line1', models.CharField(blank=True, max_length=255, null=True)),
                ('address_line2', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('state', models.CharField(blank=True, max_length=100, null=True)),
                ('country', models.CharField(default='Sri Lanka', max_length=100)),
                ('postal_code', models.CharField(blank=True, max_length=20, null=True)),
                ('tax_id', models.CharField(blank=True, help_text='Tax ID / Business Registration Number', max_length=50, null=True)),
                ('gstin', models.CharField(blank=True, max_length=20, null=True, verbose_name='GSTIN')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='company_logos/')),
                ('is_active', models.BooleanField(default=True)),
                ('subscription_start_date', models.DateField(blank=True, null=True)),
                ('subscription_end_date', models.DateField(blank=True, null=True)),
                ('max_users', models.IntegerField(default=50, help_text='Maximum number of users allowed')),
                ('max_assets', models.IntegerField(default=1000, help_text='Maximum number of assets allowed')),
                ('notes', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Company',
                'verbose_name_plural': 'Companies',
                'db_table': 'companies',
                'ordering': ['name'],
            },
        ),
        migrations.RunPython(create_default_company, reverse_code=migrations.RunPython.noop),
    ]
