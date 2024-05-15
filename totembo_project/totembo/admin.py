from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import *


class GalleryInline(admin.TabularInline):
    fk_name = 'product'
    model = Gallery
    extra = 1


class ParameterInline(admin.TabularInline):
    fk_name = 'product'
    model = ProductDescription
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'get_count_products')
    prepopulated_fields = {'slug': ['title']}

    # Метод для получения количества товара категории
    def get_count_products(self, obj):
        if obj.products:
            return str(len(obj.products.all()))
        else:
            return '0'

    get_count_products.short_description = 'Количество товара'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'category', 'price', 'quantity', 'created_at', 'get_image_product')
    list_display_links = ('pk', 'title')
    prepopulated_fields = {'slug': ['title']}
    inlines = [GalleryInline, ParameterInline]
    list_editable = ('price', 'quantity')

    def get_image_product(self, obj):
        if obj.images:
            try:
                return mark_safe(f'<img src="{obj.images.all()[0].image.url}" width="75" > ')
            except:
                return '-'
        else:
            return '-'

    get_image_product.short_description = 'Картинка'


@admin.register(Poster)
class PosterAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'get_image_poster')
    list_display_links = ('pk', 'title')

    def get_image_poster(self, obj):
        if obj.image:
            try:
                return mark_safe(f'<img src="{obj.image.url}" width="50" > ')
            except:
                return '-'
        else:
            return '-'

    get_image_poster.short_description = 'Картинка'

admin.site.register(Gallery)
admin.site.register(ProductDescription)
admin.site.register(FavoriteProduct)

admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderProduct)
admin.site.register(ShippingAddress)
admin.site.register(City)
