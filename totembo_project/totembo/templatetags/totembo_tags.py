from django import template
from totembo.models import Category, Product, FavoriteProduct, Poster

register = template.Library()


@register.simple_tag()
def get_categories():
    return Category.objects.filter(parent=None)


@register.simple_tag()
def get_colors(model_product):
    products = Product.objects.filter(model_product=model_product)
    list_colors = [i.color_code for i in products]
    return list_colors


@register.simple_tag()
def get_normal_price(price):
    return f'{int(price):_}'.replace('_', ' ')


@register.simple_tag()
def get_favorite_products(user):
    fav_products = FavoriteProduct.objects.filter(user=user)
    products = [i.product for i in fav_products]
    return products


@register.simple_tag()
def get_info_poster():
    return Poster.objects.all()



