from django.db import models
from django.utils.translation import ugettext_lazy as _
from datetime import date

# Create your models here.

class Customer(models.Model):
	name = models.CharField(
		default='',
		max_length=500,
		help_text = _("Name"),
	)
	sfu_email = models.CharField(
		default='',
		max_length=500,
		help_text = _("SFU Email"),
	)

	def __str__(self):
		return f"Customer {self.name}"


class Order(models.Model):
	customer_key = models.ForeignKey(
		Customer,
		on_delete=models.CASCADE,
        default=1
	)
	order_id = models.CharField(
		default='',
		max_length=200,
		primary_key=True,
		help_text = _("Order ID"),
	)
	date = models.DateField(
		default=date.today,
		help_text = _("Date"),
	)
	time = models.TimeField(
		help_text = _("Time"),
	)
	def __str__(self):
		return f"Order: {self.order_id}"

class SourceFile(models.Model):
    json_file = models.FileField(
        default = 'merchandise/default',
        upload_to='merchandise/'
    )

    def __str__(self):
        return f" Source File: {self.json_file}"

class Merchandise(models.Model):
	image_absolute_file_path = models.CharField(
		max_length=1000,
	    help_text = _("Location of File on Server"),
	    verbose_name=('File Path'),
	)
	merchandise_type = models.CharField(
		max_length=100,
		default='',
		help_text = _("Merchandise"),
	)
	price = models.FloatField(
		default=0
	)
	active = models.BooleanField(
		default=True
	)
	def __str__(self):
		return f"Merchandise: {self.merchandise_type}"

class Feature(models.Model):
	merchandise_key = models.ForeignKey(
		Merchandise,
		related_name='feature',
		on_delete=models.CASCADE,
	)
	feature_type = models.CharField(
		max_length=100,
		default='',
		help_text = _("Feature"),
	)
	active = models.BooleanField(
		default=True
	)
	def __str__(self):
		return f" Feature {self.feature_type} for merchandise {self.merchandise_key_id}"

class Specification(models.Model):
	feature_key = models.ForeignKey(
		Feature,
		related_name='spec',
		on_delete=models.CASCADE,
	)
	specification_type = models.CharField(
		max_length=100,
		default='',
		help_text = _("Specification"),
	)
	active = models.BooleanField(
		default=True
	)
	def __str__(self):
		return f" Specification {self.specification_type} for {self.feature_key_id}"

class OrderItem(models.Model):
	order_key = models.ForeignKey(
		Order,
		on_delete=models.CASCADE,
	)
	merchandise_key = models.ForeignKey(
		Merchandise,
		on_delete=models.CASCADE,
	)
	quantity = models.IntegerField(
		default = 0
	)

	def __str__(self):
		return f"OrderItem of {self.merchandise_key_id} with quantity {self.quantity} selected for order {self.order_key.order_id}"

class OrderItemSpecification(models.Model):
    orderItem_key = models.ForeignKey(
        OrderItem,
        on_delete=models.CASCADE,
    )
    feature_key = models.ForeignKey(
        Feature,
        on_delete=models.CASCADE,
    )
    specification_key = models.ForeignKey(
        Specification,
        on_delete=models.CASCADE,
    )

    def get_order_id(self):
        return self.OrderFeatureSpecificationSelected_orderItem_key.order_key.order_id

    def __str__(self):
        return f"Specification {self.OrderFeatureSpecificationSelected_FeatureSpecification_key} selected for feature {self.OrderFeatureSpecificationSelected_Feature_key} for OrderItem {self.OrderFeatureSpecificationSelected_orderItem_key}"
