from django import template
from core.models import Order, OrdeItem, OrderItem, Item, Category

register = template.Library()


@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = Order.objects.filter(user=user, ordered=False)
        if qs.exists():
            return qs[0].items.count()
    return 0


@register.filter
def wish_item_count(user):
    if user.is_authenticated:
        qs = OrdeItem.objects.filter(user=user, ordeed=False)
        if qs.exists():
            return qs.count()

    return 0

@register.filter
def admin_item_count(user):
    if user.is_staff:
        qs = Order.objects.filter(user=user, ordered=True,order_rejected=False, order_placed=False)
        if qs.exists():
            return qs.count()

    return 0

@register.filter
def category_count(id):
    category = Category.objects.get(id=id)
    qs = Item.objects.filter(category=category)
    if qs.exists():
        return qs.count()
    return 0

@register.filter
def isImage(media):
    if str(media).split('.')[-1] in ['jpeg' ,'jpg', 'png', 'eps', 'raw']:
        print("Image")
        return media
    return 0

@register.filter
def isVideo(media):
    if str(media).split('.')[-1] in ['mp4', 'webm', 'mpg', 'mp2', 'mpeg', 'mpe', 'mpv', 'ogg', 'm4p', 'm4v', 'avi', 'wmv', 'mov', 'wmv']:
        print("video")
        return media
    return 0
