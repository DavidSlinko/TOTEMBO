# Generated by Django 5.0.2 on 2024-02-17 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('totembo', '0007_product_desc_product_full_title_product_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='products/', verbose_name='Картинка к описанию'),
        ),
    ]
