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
		return f"{self.name}"


class Order(models.Model):
	order_customer_key = models.ForeignKey(
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
		return f"{self.order_id}"

class Merchandise(models.Model):
    image = models.ImageField(
        upload_to='merchandise_images',
        #null=True,
        blank = True,
        default = None,
    )
    merchandise = models.CharField(
        max_length=100,
        default='',
        help_text = _("Merchandise"),
    )
    price = models.FloatField(
        default=0
    )
    def __str__(self):
        return f"{self.merchandise}"

class Option(models.Model):
	option_merchandise_key = models.ForeignKey(
		Merchandise,
		on_delete=models.CASCADE,
	)
	option = models.CharField(
		max_length=100,
		default='',
		help_text = _("Option"),
	)
	def __str__(self):
		return f"{self.option_merchandise_key} {self.option}"

class OptionChoice(models.Model):
	optionChoice_option_key = models.ForeignKey(
		Option,
		on_delete=models.CASCADE,
	)
	choice = models.CharField(
		max_length=100,
		default='',
		help_text = _("Choice"),
	)
	def __str__(self):
		return f"{self.choice}"

class SelectedOrderMerchandise(models.Model):
	orderItem_order_key = models.ForeignKey(
		Order,
		on_delete=models.CASCADE,
	)
	orderItem_merchandise_key = models.ForeignKey(
		Merchandise,
		on_delete=models.CASCADE,
	)
	quantity = models.IntegerField(
		default = 0
	)

	def __str__(self):
		return f"item {self.orderItem_merchandise_key} with quantity {self.quantity} selected for order{self.orderItem_order_key.order_id}"

class SelectedOrderMerchandiseOptionChoice(models.Model):
    OrderOptionChoiceSelected_orderItem_key = models.ForeignKey(
        SelectedOrderMerchandise,
        on_delete=models.CASCADE,
    )
    OrderOptionChoiceSelected_option_key = models.ForeignKey(
        Option,
        on_delete=models.CASCADE,
    )
    OrderOptionChoiceSelected_optionChoice_key = models.ForeignKey(
        OptionChoice,
        on_delete=models.CASCADE,
    )

    def get_order_id(self):
        return self.OrderOptionChoiceSelected_orderItem_key.orderItem_order_key.order_id

    def __str__(self):
        return f"choice {self.OrderOptionChoiceSelected_optionChoice_key} selected for option {self.OrderOptionChoiceSelected_option_key} for SelectedOrderMerchandise {self.OrderOptionChoiceSelected_orderItem_key}"
