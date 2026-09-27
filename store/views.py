from django.shortcuts import render
from.models import Product, Slider, Category, Cart
from django.core.paginator import Paginator
from django.utils.translation import gettext as __
from django.http import JsonResponse
from django.contrib.sessions.models import Session
# Create your views here.

def index(request):
    models = Product.objects.select_related('author').filter(featured=True)
    slides = Slider.objects.order_by('order')
    return render(request,'index.html', {'products': models, 'slides': slides})

def product(request, pid):
    model = Product.objects.get(pk=pid)
    return render(request,'product.html', {'product': model})
def category(request, cid=None):
    cat = None
    cid = request.GET.get('cid')
    query = request.GET.get('query')

    where = {}

    if cid:
        cat = Category.objects.get(pk=cid)
        where['category_id'] = cid

    if query:
        where['name__icontains'] = query


    models = Product.objects.filter(**where)
    paginator = Paginator(models, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,'category.html', {'page_obj': page_obj, 'cat': cat})
def cart(request):
    return render(request,'cart.html')
def checkout(request):
    return render(request,'checkout.html')
def checkout_complete(request):
    Card.objects.filter(session_id=request.session.session_key).delete()
    return render(request,'checkout_complete.html')

def cart_add(request, pid):
    if not request.session.session_key:
        request.session.create()

    session_id = request.session.session_key
    cart_model = Cart.objects.filter(session=request.session.session_key).last()

    if cart_model is None:
        cart_model = Cart.objects.create(session=session_id, items=[pid])
    elif pid not in cart_model.items:
        cart_model.items.append(pid)
        cart_model.save()
    return JsonResponse({
        'message': __('The product has been added to your cart'),
        'items_count': len(cart_model.items),
    })

def cart_remove(request, pid):
    session = request.session.session_key
    if not session:
        return JsonResponse({})

    cart_model = Cart.objects.filter(session=request.session.session_key).last()
    if not cart_model:
        return JsonResponse({})
    cart_model.items.remove(pid)
    cart_model.save()
    return JsonResponse({
        'message': __('The product has been removed from your cart'),
    })


