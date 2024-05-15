from random import randint

from django.shortcuts import render, redirect
from .models import *
from django.views.generic import ListView, DetailView
from .forms import LoginForm, RegisterForm, CustomerForm, ShippingForm
from django.contrib.auth import login, logout
from django.contrib import messages
from .utils import CartForAuthenticatedUser, get_cart_data
from django.contrib.auth.mixins import LoginRequiredMixin
#import stripe
from totembo_project import settings


# from .utils import CartForAuthenticatedUser, get_cart_data

# Главная страница
class ProductList(ListView):
    model = Product
    context_object_name = 'categories'
    template_name = 'pages/index.html'
    extra_context = {
        'title': 'TOTEMBO'
    }

    def get_queryset(self):
        categories = Category.objects.filter(parent=None)
        return categories


# Страница категорий
class CategoryView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'pages/category.html'
    

    def get_queryset(self):

        color_field = self.request.GET.get('color')

        price_field = self.request.GET.get('price')
        type_watch_field = self.request.GET.get('type_watch')

        category = Category.objects.get(slug=self.kwargs['slug'])
        products = category.products.all()

        if color_field:
            products = products.filter(color=color_field)

        if price_field:
            products = products.filter(price=price_field)

        if type_watch_field:
            products = products.filter(type_watch=type_watch_field)

        return products

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        category = Category.objects.get(slug=self.kwargs['slug'])
        products = category.products.all()

        colors = list(set([i.color for i in products]))
        prices = list(set([int(i.price) for i in products]))
        types_watches = list(set([i.type_watch for i in products]))

        context['colors'] = colors
        context['prices'] = prices
        context['types_watches'] = types_watches

        context['title'] = f'Товары категории: {category.title}'
        context['category'] = category

        return context


# Вход выход
def user_login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        if request.method == 'POST':
            form = LoginForm(data=request.POST)
            if form.is_valid():
                user = form.get_user()
                if user:
                    login(request, user)
                    messages.success(request, 'Вы вошли в аккаунт')
                    return redirect('index')
                else:
                    messages.error(request, 'Не верный логин или пароль')
                    return redirect('login')
            else:
                messages.error(request, 'Не верный логин или пароль')
                return redirect('login')

        else:
            form = LoginForm()

        context = {
            'title': 'Вход в Аккаунт',
            'form': form
        }
        return render(request, 'pages/login.html', context)


def user_logout_view(request):
    logout(request)
    messages.warning(request, 'Ждем вас снова)')
    return redirect('index')


# Регистрация
def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        if request.method == 'POST':
            form = RegisterForm(data=request.POST)
            if form.is_valid():
                user = form.save()
                messages.success(request, 'Вы прошли регистрацию. Авторизуйтесь')
                return redirect('login')
            else:
                for field in form.errors:
                    messages.error(request, form.errors[field].as_text())
                    return redirect('register')
        else:
            form = RegisterForm()

        context = {
            'title': 'Регистрация пользователя',
            'form': form
        }
        return render(request, 'pages/register.html', context)


# Продукт
class ProductDetail(DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'pages/product_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        product = Product.objects.get(slug=self.kwargs['slug'])
        context['title'] = f'Товар {product.title}'

        products = Product.objects.filter(category=product.category)
        data = []
        for i in range(3):
            random_index = randint(0, len(products) - 1)  # Получакем рандомный индекс
            p = products[random_index]  # По рандомному индексу получаем товар из списка
            if p not in data and product != p:
                data.append(p)

        context['products'] = data

        return context


# Избранное
def save_favorite_product(request, slug):
    if request.user.is_authenticated:
        user = request.user
        product = Product.objects.get(slug=slug)
        favorite_products = FavoriteProduct.objects.filter(user=user)
        if user:
            if product not in [i.product for i in favorite_products]:
                messages.success(request, 'Товар добавлен в Избранное')
                FavoriteProduct.objects.create(user=user, product=product)
            else:
                fav_product = FavoriteProduct.objects.get(user=user, product=product)
                messages.warning(request, 'Вы удалили товар из избранного')
                fav_product.delete()

            page = request.META.get('HTTP_REFERER', 'index')
            return redirect(page)
    else:
        messages.warning(request, 'Нужно авторизоваться')
        return redirect('login')


# Страница избранного
class FavoriteProductView(LoginRequiredMixin, ListView):
    model = FavoriteProduct
    context_object_name = 'products'
    template_name = 'pages/favorite.html'
    login_url = 'login'

    def get_queryset(self):
        user = self.request.user
        favorite_products = FavoriteProduct.objects.filter(user=user)
        products = [i.product for i in favorite_products]
        return products


# добавления товара в корзину
def to_cart_view(request, slug, action):
    if request.user.is_authenticated:
        user_cart = CartForAuthenticatedUser(request, slug, action)
        page = request.META.get('HTTP_REFERER', 'index')
        return redirect(page)

    else:
        messages.warning(request, 'Авторизуйтесь')
        return redirect('login')


# страница корзины
def my_cart_view(request):
    if request.user.is_authenticated:
        cart_info = get_cart_data(request)

        context = {
            'title': 'Моя корзина',
            'order': cart_info['order'],
            'products': cart_info['products']
        }

        return render(request, 'pages/my_cart.html', context)

    else:
        messages.warning(request, 'Авторизуйтесь')
        return redirect('login')


# очищение корзины
def clear_cart(request):
    user_cart = CartForAuthenticatedUser(request)
    order = user_cart.get_cart_info()['order']
    order_products = order.orderproduct_set.all()
    for order_product in order_products:
        quantity = order_product.quantity
        product = order_product.product
        order_product.delete()
        product.quantity += quantity
        product.save()
    messages.warning(request, 'Корзину очищена')
    return redirect('my_cart')


# Оформление заказа
def checkout_view(request):
    if request.user.is_authenticated:
        cart_info = get_cart_data(request)

        context = {
            'title': 'Оформление заказа',
            'order': cart_info['order'],
            'items': cart_info['products'],

            'customer_form': CustomerForm(),
            'shipping_form': ShippingForm()
        }
        return render(request, 'pages/checkout.html', context)
    else:
        return redirect('login')


# Оплата
def create_checkout_session(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if request.method == 'POST':
        user_cart = CartForAuthenticatedUser(request)
        cart_info = user_cart.get_cart_info()

        customer_form = CustomerForm(data=request.POST)
        if customer_form.is_valid():
            customer = Customer.objects.get(user=request.user)
            customer.first_name = customer_form.cleaned_data['first_name']
            customer.last_name = customer_form.cleaned_data['last_name']
            customer.email = customer_form.cleaned_data['email']
            customer.save()

        shipping_form = ShippingForm(data=request.POST)
        if shipping_form.is_valid():
            address = shipping_form.save(commit=False)
            address.customer = Customer.objects.get(user=request.user)
            address.order = user_cart.get_cart_info()['order']
            address.save()
        else:
            for field in shipping_form.errors:
                messages.error(request, shipping_form.errors[field].as_text())

        total_price = cart_info['cart_total_price']
        session = stripe.checkout.Session.create(
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'TOTEMBO'
                    },
                    'unit_amount': int(total_price)
                },
                'quantity': 1
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('success')),
            cancel_url=request.build_absolute_uri(reverse('checkout'))
        )
        return redirect(session.url, 303)


# Страница оплаты
def success_payment(request):
    if request.user.is_authenticated:
        user_cart = CartForAuthenticatedUser(request)
        cart_info = user_cart.get_cart_info()

        user_cart.clear()
        messages.success(request, 'Оплата прошла успешно')
        return render(request, 'pages/success.html')
    else:
        return redirect('index')


