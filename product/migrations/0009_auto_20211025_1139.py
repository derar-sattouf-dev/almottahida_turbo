# Generated by Django 3.2.8 on 2021-10-25 08:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0008_alter_product_weight_value'),
    ]

    operations = [
        migrations.RenameField(
            model_name='invoice',
            old_name='date_published',
            new_name='date_added',
        ),
        migrations.RenameField(
            model_name='invoice',
            old_name='dept',
            new_name='remaining',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='paydate',
        ),
    ]