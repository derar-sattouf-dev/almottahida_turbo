# Generated by Django 3.2.8 on 2021-10-25 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0005_invoice_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailyboxoperation',
            name='operation',
            field=models.CharField(choices=[('Add', 'Add'), ('Take', 'Take')], default='Add', max_length=5),
        ),
    ]
