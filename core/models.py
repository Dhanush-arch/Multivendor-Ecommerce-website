from django.conf import settings
from django.db import models
from django.db.models import Sum,Avg,Count
from django.shortcuts import reverse
from django_countries.fields import CountryField
from django.forms import ModelForm
from tinymce.models import HTMLField
from .validators import validate_file_size
from django.contrib.auth.models import User
# Create your models here.


LABEL_CHOICES = (
    ('New', 'New'),
    ('Sale', 'Sale'),
    ('Promotion', 'Promotion'),
)

TAX_VALUE_TYPES = (
    ('In Rupees', 'Rs'),
    ('In Percentage' , 'Percent')
)

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)

class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phoneNo = models.CharField(max_length=100)

    def __str__(self):
        return str(self.user)


class Slide(models.Model):
    caption1 = models.CharField(max_length=100)
    caption2 = models.CharField(max_length=100)
    link = models.CharField(max_length=100)
    image = models.ImageField(help_text="Size: 1920x570")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "{} - {}".format(self.caption1, self.caption2)


class Category(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:category", kwargs={
            'slug': self.slug
        })

class Collection(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    label = models.CharField(choices=LABEL_CHOICES, max_length=50)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, null=True, blank=True)
    slug = models.SlugField()
    stock_no = models.CharField(max_length=10)
    description_short =  HTMLField(blank=True)
    # description_long = models.TextField()
    description_long = HTMLField(blank=True)
    image = models.ImageField()
    is_active = models.BooleanField(default=True)
    has_variations = models.BooleanField(default=True) #This needs to be changed to False before deploying
    # attachments = models.ManyToManyField(Attachment, blank=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:product", kwargs={
            'slug': self.slug
        })

    def get_id(self):
        return reverse('core:product', kwargs={
            'slug': self.slug,
            'id' : self.id
        })
    def avaregereview(self):
        reviews = Comment.objects.filter(product=self, status='True').aggregate(avarage=Avg('rate'))
        avg=0
        if reviews["avarage"] is not None:
            avg=float(reviews["avarage"])
        return avg

    def countreview(self):
        reviews = Comment.objects.filter(product=self, status='True').aggregate(count=Count('id'))
        cnt=0
        if reviews["count"] is not None:
            cnt = int(reviews["count"])
        return cnt


    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            'slug': self.slug,
            'qt': 1
        })

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'slug': self.slug
        })

    def get_add_to_wish_url(self):
        return reverse("core:add-to-wish", kwargs={
            'slug': self.slug,
            'qt' : 1
        })

    def get_remove_from_wish_url(self):
        return reverse("core:remove-from-wish", kwargs={
            'slug': self.slug
        })

    def get_attachments(self):
        attachments = Attachment.objects.filter(productId=self.id)
        print(attachments)
        return attachments


class Attachment(models.Model):
    #productId = models.ForeignKey(Item, on_delete=models.CASCADE)
    #thumbnail = models.ImageField(blank=True, null=True)
    #is_video = models.BooleanField(default= False, help_text="Check If you need to upload a video")
    #media_attach = models.FileField(blank=True, null=True,  validators=[validate_file_size])
    productId = models.ForeignKey(Item, on_delete=models.CASCADE)
    #thumbnail = models.ImageField(blank=True, null=True)
    #is_video = models.BooleanField(default= False, help_text="Check If you need to upload a video")
    media_attach = models.FileField(blank=True, null=True,  validators=[validate_file_size])


    def __str__(self):
        return str(self.productId) + " " + str(self.media_attach)

class Tax(models.Model):
    # productId = models.ForeignKey(Item, on_delete=models.CASCADE)
    TaxName = models.CharField(max_length=50)
    ValueType = models.CharField(choices=TAX_VALUE_TYPES, max_length=50)
    TaxValue = models.FloatField()

class Comment(models.Model):
    STATUS = (
        ('New', 'New'),
        ('True', 'True'),
        ('False', 'False'),
    )
    product=models.ForeignKey(Item,on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    subject = models.CharField(max_length=50, blank=True)
    comment = models.CharField(max_length=250,blank=True)
    rate = models.IntegerField(default=1)
    ip = models.CharField(max_length=20, blank=True)
    status=models.CharField(max_length=10,choices=STATUS, default='True')
    create_at=models.DateTimeField(auto_now_add=True)
    update_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['subject', 'comment', 'rate']

class Contact(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, null=True)
    fname = models.CharField(max_length=50)
    lname = models.CharField(max_length=50)
    mobileno = models.IntegerField()
    emailId = models.EmailField(max_length=50)
    subject = models.CharField(max_length=500)
    create_at = models.DateTimeField(auto_now_add=True)
    ip = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return  self.fname + " " + self.lname + " " + self.emailId

class ContactForm(ModelForm):
    class Meta:
        model = Contact
        fields = ['fname', 'lname', 'mobileno', 'emailId', 'subject']

#intern-code
class MiddleVariation(models.Model): # Variation Model Ex:Size, Color...
    productId = models.ForeignKey(Item, on_delete=models.CASCADE, help_text="Select your Product")
    variationCategory = models.CharField(max_length=100, help_text="Ex: Color, Size", default="Size")
    variationValue = models.CharField(max_length=100, help_text="Ex: Red, XL")

    def __str__(self):
        return str(self.productId) + "-" + str(self.variationCategory) + "-" + str(self.variationValue)

class FinalVariation(models.Model):
    productId = models.ForeignKey(Item, on_delete=models.CASCADE)
    variationName = models.CharField(max_length=100, help_text="Enter the variation name in the following manner\nProductName-vartions\n\tEx: Car-Red-SUV")
    variations = models.ManyToManyField(MiddleVariation, blank=True, help_text="Select the required options. Add variations category by clicking \"+\" sign")
    price = models.FloatField(null=True, help_text="Including discount if available")
    def __str__(self):
        return str(self.variationName) + "/"+str(self.price)+"/"

    def get_add_to_cart_url(self, qt):
        return reverse("core:add-to-cart", kwargs={
            'slug'  : self.variationName,
            'qt'    : qt
        })

    def get_absolute_url(self):
        return reverse("core:product", kwargs={
            'slug':  self.variationName
        })

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'slug': self.variationName
        })

    def get_add_to_wish_url(self):
        return reverse("core:add-to-wish", kwargs={
            'slug': self.variationName
        })

    def get_remove_from_wish_url(self):
        return reverse("core:remove-from-wish", kwargs={
            'slug': self.variationName
        })

    def get_price(self):
        return self.price
#*****************************************
#Naming Convention for FinalVariation model:
#   VariationName field must be filled in the following convention:
#       "ProductName"-"Variation1"-"Variation2"... Ex:"Aaa-Red-S"
#*****************************************

class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(FinalVariation, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.FloatField(null=True, blank=True) #Variation

    def __str__(self):
        return f"{self.quantity} of {self.item.variationName}"

    def get_total_item_price(self):
        if self.price:
            return self.quantity * self.price
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        if self.price:
            return self.quantity * self.price
        return self.quantity * self.item.productId.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.productId.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()

class OrdeItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordeed = models.BooleanField(default=False)
    item = models.ForeignKey(FinalVariation, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.variationName}"

    def get_total_item_price(self):
        return int(self.quantity) * int(self.item.price)

    def get_total_discount_item_price(self):
        return self.quantity * self.item.productId.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.productId.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()
    #intern-code
    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            'slug': self.item.variationName
        })

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20)

    items = models.ManyToManyField(OrderItem)
    wishitem= models.ManyToManyField(OrdeItem)
    tax = models.FloatField(null=True, blank=True, default=0)
    totalPrice = models.FloatField(null=True, blank=True, default=0)

    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        'BillingAddress', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        'BillingAddress', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    order_rejected = models.BooleanField(default=False)
    order_placed = models.BooleanField(default=False)
    special_instructions = models.CharField(max_length=500,null=True)

    '''
    1. Item added to cart
    2. Adding a BillingAddress
    (Failed Checkout)
    3. Payment
    4. Being delivered
    5. Received
    6. Refunds
    '''

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total

    def get_tax_include(self):
        total = 0
        taxdb = Tax.objects.all()
        for i in taxdb:
            if i.ValueType == TAX_VALUE_TYPES[0][0]:
                total += self.get_total() + i.TaxValue
            elif i.ValueType == TAX_VALUE_TYPES[1][0]:
                total += self.get_total() * (i.TaxValue/100.0)
        return total

    def get_tax_amount(self):
        tax = 0
        taxdb = Tax.objects.all()
        for i in taxdb:
            if i.ValueType == TAX_VALUE_TYPES[0][0]:
                tax += i.TaxValue
            elif i.ValueType == TAX_VALUE_TYPES[1][0]:
                tax += self.get_total() * (i.TaxValue/100.0)
        return tax

class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    fname = models.CharField(max_length=100,null=True)
    lname = models.CharField(max_length=100,null=True)
    email = models.CharField(max_length=50,null=True)
    number = models.CharField(max_length=20, null=True)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100,  null=True)
    state = models.CharField(max_length=100,  null=True)
    zip = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)
    country = models.CharField(max_length=1, null=True, blank=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'BillingAddresses'



class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"
