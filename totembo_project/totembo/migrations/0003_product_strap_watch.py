# Generated by Django 5.0.2 on 2024-02-17 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('totembo', '0002_product_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='strap_watch',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Тип часов'),
        ),
    ]