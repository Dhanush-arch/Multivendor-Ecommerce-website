# Generated by Django 2.2.4 on 2020-08-19 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_auto_20200819_1443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='media_attach',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
    ]
