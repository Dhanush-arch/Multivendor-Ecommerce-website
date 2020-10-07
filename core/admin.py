from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from .models import Item, OrderItem,OrdeItem, Order, Payment, Coupon, Refund, BillingAddress, Category, Slide, MiddleVariation, FinalVariation, Comment, Contact, Attachment, Tax, Collection


# Register your models here.


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',
                    'being_delivered',
                    'received',
                    'refund_requested',
                    'refund_granted',
                    'shipping_address',
                    'billing_address',
                    'payment',
                    'coupon'
                    ]
    list_display_links = [
        'user',
        'shipping_address',
        'billing_address',
        'payment',
        'coupon'
    ]
    list_filter = ['user',
                   'ordered',
                   'being_delivered',
                   'received',
                   'refund_requested',
                   'refund_granted']
    search_fields = [
        'user__username',
        'ref_code'
    ]
    actions = [make_refund_accepted]

class CommentAdmin(admin.ModelAdmin):
    list_display = ['subject','comment', 'status','create_at']
    list_filter = ['status']
    readonly_fields = ('subject','comment','ip','user','product','rate','id')

class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'apartment_address',
        'country',
        'zip',
        'address_type',
        'default'
    ]
    list_filter = ['default', 'address_type', 'country']
    search_fields = ['user', 'street_address', 'apartment_address', 'zip']


def copy_items(modeladmin, request, queryset):
    for object in queryset:
        object.id = None
        object.save()


copy_items.short_description = 'Copy Items'

class FinalVariationInline(admin.TabularInline):
    model = FinalVariation
    extra = 0
class MiddleVariationInline(admin.TabularInline):
    model = MiddleVariation
    extra = 0
    show_change_link = True
class AttachmentInline(admin.StackedInline):
    model = Attachment
    extra = 0
    max_num = 5
class TaxInline(admin.StackedInline):
    model = Tax
    extra = 0
    max_num = 5

class ItemAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'category',
    ]
    list_filter = ['title', 'category']
    search_fields = ['title', 'category']
    prepopulated_fields = {"slug": ("title",)}
    actions = [copy_items]
    inlines = [ AttachmentInline, MiddleVariationInline, FinalVariationInline]
    help_texts = {'title':'title is displayed here'}
    def response_add(self, request, obj, post_url_continue=None):
       # print("in response " , obj)
        url = request.META.get('HTTP_REFERER')
       # print(url)
       # print(obj.has_variations)
        if obj.has_variations:
            return redirect(url[:-4] + str(obj.id)+"/change/")
        else:
            # print("in redit", request, post_url_continue)
            return redirect(url[:-4])

    def save_related(self, request, form, formsets, change):
        url = request.META.get('HTTP_REFERER')
        super(ItemAdmin, self).save_related(request, form, formsets, change)
        myform = form.instance

       # for i in formsets[1]:
        #    print(i.instance)
        #    var = i.instance
         #   middle
         #   print(i.)

        item = Item.objects.get(
            title=myform.title,
            price=myform.price,
            slug=myform.slug,
            category=myform.category,
            label=myform.label
        )

        #print("varitaions ", formsets)
        if item.has_variations == False:
           # print("has variations")
            productvarition = FinalVariation.objects.filter(productId=item, variationName=item.title)
            #print(productvarition)
            #print(productvarition.exists())
            if productvarition.exists() == False:
                #print("in variation")
                productVarition = FinalVariation.objects.create(productId = item)
                productVarition.variationName = item.title
                # productVarition.variations.set(None)
                if item.discount_price:
                    productVarition.price = item.discount_price
                else:
                    productVarition.price = item.price
                productVarition.save()
                #print(productVarition)
        else:
           # print(url)
           # print(item.id)
            url = url[:-4]+str(item.id)+"/change/"
            #return  redirect(url)
            def response_change(self, request, obj, post_url_continue=None):
                """This makes the response go to the newly created model's change page
                without using reverse"""
                return HttpResponseRedirect("../%s" % obj.id)

    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            # hide MyInline in the add view
            #print(inline)
            if not isinstance(inline, FinalVariationInline) or obj is not None:
                yield inline.get_formset(request, obj), inline

class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'is_active'
    ]
    list_filter = ['title', 'is_active']
    search_fields = ['title', 'is_active']
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Item, ItemAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment,CommentAdmin)
admin.site.register(Attachment)
admin.site.register(Contact)
admin.site.register(MiddleVariation)
admin.site.register(FinalVariation)
admin.site.register(Slide)
admin.site.register(OrderItem)
admin.site.register(OrdeItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(BillingAddress, AddressAdmin)
admin.site.register(Tax)
admin.site.register(Collection)