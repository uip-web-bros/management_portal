# Generated by Django 3.1.2 on 2020-11-18 17:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('licences', '0002_auto_20201118_1806'),
        ('updates', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='update',
            name='active',
        ),
        migrations.RemoveField(
            model_name='update',
            name='software',
        ),
        migrations.AddField(
            model_name='update',
            name='content',
            field=models.BinaryField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='update',
            name='product',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='updates', related_query_name='update', to='licences.softwareproduct'),
            preserve_default=False,
        ),
    ]