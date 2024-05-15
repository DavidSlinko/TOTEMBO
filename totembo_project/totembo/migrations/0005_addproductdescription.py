# Generated by Django 5.0.2 on 2024-02-17 16:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('totembo', '0004_rename_strap_watch_product_type_watch'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddProductDescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=250, null=True, verbose_name='Название описания')),
                ('full_title', models.TextField(blank=True, null=True, verbose_name='Полное описание')),
                ('image', models.ImageField(blank=True, null=True, upload_to='add_product_description/', verbose_name='Картинка к описанию')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='add_parameters', to='totembo.product', verbose_name='Товар')),
            ],
            options={
                'verbose_name': 'Дополнительный параметер',
                'verbose_name_plural': 'Дополнительные параметеры',
            },
        ),
    ]
