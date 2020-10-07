# Generated by Django 2.2.4 on 2020-09-24 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0042_auto_20200923_1708'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='cgst_tax_price',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='sgst_tax_price',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='sub_price',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='total_price',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='cgst_tax_price',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='sgst_tax_price',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='total_price',
            field=models.FloatField(null=True),
        ),
    ]
