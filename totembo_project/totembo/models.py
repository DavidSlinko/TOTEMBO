from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


# Категории
class Category(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название категории')
    slug = models.SlugField(unique=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='subcategories',
                               verbose_name='Категория')

    # Умная ссылка
    def get_absolute_url(self):
        return reverse('category', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class TypeWatch(models.Model):
    title = models.CharField(max_length=100, verbose_name='Тип часов')


# Продукт
class Product(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название товара')
    price = models.FloatField(verbose_name='Цена товара')
    color = models.CharField(max_length=100, verbose_name='Цвет')
    delivery = models.CharField(max_length=200, verbose_name='Информация о доставке')
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Категория')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    quantity = models.IntegerField(verbose_name='Количество товара', blank=True, null=True)
    type_watch = models.CharField(max_length=50, blank=True, null=True, verbose_name='Тип часов')

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})

    def get_image_product(self):
        if self.images:
            try:
                return self.images.first().image.url
            except:
                return '-'
        else:
            return '-'

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


# Галерея
class Gallery(models.Model):
    image = models.ImageField(upload_to='products/', verbose_name='Фото товара')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name='Товар')

    class Meta:
        verbose_name = 'Картинка товара'
        verbose_name_plural = 'Картинки товара'


# Детали товара
class ProductDescription(models.Model):
    parameter = models.CharField(max_length=150, verbose_name='Название параметра')
    parameter_info = models.TextField(max_length=400, blank=True, null=True, verbose_name='Описание параметра')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='parameters', verbose_name='Товар')

    def __str__(self):
        return f'{self.parameter}: {self.parameter_info}'

    class Meta:
        verbose_name = 'Параметер'
        verbose_name_plural = 'Параметеры'


# Избранное
class FavoriteProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')

    def __str__(self):
        return f'Товар: {self.product} пользователя: {self.user.username}'

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные товары'


# ------------------------------------------------------------------------------------
# Покупатель
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, blank=True, null=True)
    first_name = models.CharField(max_length=255, default='', verbose_name='Имя покупателя')
    last_name = models.CharField(max_length=255, default='', verbose_name='Фамилия покупателя')
    email = models.EmailField(verbose_name='Почта покупателя', blank=True, null=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'


# Заказ
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')
    is_completed = models.BooleanField(default=False, verbose_name='Выполнен ли заказ')
    shipping = models.BooleanField(default=True, verbose_name='Доставка')

    def __str__(self):
        return f'Заказ №:{self.pk}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    # Здесь реализуем методы подсчёта суммы заказа и кол-ва товара
    @property  # Метод дял получения суммы заказа
    def get_cart_total_price(self):
        order_products = self.orderproduct_set.all()
        total_price = sum([product.get_total_price for product in order_products])
        return total_price

    @property  # Метод дял получения суммы заказа
    def get_cart_total_quantity(self):
        order_products = self.orderproduct_set.all()
        total_quantity = sum([product.quantity for product in order_products])
        return total_quantity

    # Модель заказаных товаров


class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, verbose_name='Номер заказа')
    quantity = models.IntegerField(default=0, null=True, blank=True, verbose_name='Количество')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления в корзину')

    def __str__(self):
        return f'Продукт {self.product.title} {self.order}'

    class Meta:
        verbose_name = 'Заказанный товар'
        verbose_name_plural = 'Заказанные товары'

    # Метод дял получения стоимости товара в его кол-ве
    @property
    def get_total_price(self):
        total_price = self.product.price * self.quantity
        return total_price

    # Модель Доставки


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, verbose_name='Покупатель')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, verbose_name='Заказ')
    address = models.CharField(max_length=200, verbose_name='Адрес удица/дом/кв')
    city = models.ForeignKey('City', on_delete=models.CASCADE, verbose_name='Город доставки')
    region = models.CharField(max_length=200, verbose_name='Регион/Область')
    phone = models.CharField(max_length=200, verbose_name='Номер получаетля')
    comment = models.CharField(max_length=300, verbose_name='Комментарий к заказу')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата доставки')

    def __str__(self):
        return f'Получатель {self.customer} по адресу:{self.address}'

    class Meta:
        verbose_name = 'Адрес доставки'
        verbose_name_plural = 'Адреса доставок'


class City(models.Model):
    city_name = models.CharField(max_length=100, verbose_name='Название города')

    def __str__(self):
        return self.city_name

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'


class Poster(models.Model):
    title = models.CharField(max_length=400, verbose_name='Краткоео описание')
    image = models.ImageField(upload_to='images_slider/', verbose_name='Картинка для слайдера', blank=True, null=True)

    def __str__(self):
        return self.title

    def get_image_poster(self):
        if self.image:
            try:
                return self.image.url
            except:
                return '-'
        else:
            return '-'

    class Meta:
        verbose_name = 'Постер'
        verbose_name_plural = 'Постеры'
