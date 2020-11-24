# Generated by Django 3.1.2 on 2020-11-20 11:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0002_contactperson_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='customer',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='locations', related_query_name='location', to='customers.customer'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='location',
            name='adviser',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='locations', related_query_name='location', to='customers.customeradviser'),
        ),
    ]
