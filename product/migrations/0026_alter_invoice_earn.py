# Generated by Django 3.2.8 on 2021-11-02 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0025_auto_20211102_1342'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='earn',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]
