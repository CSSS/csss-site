# Register your models here.
from django.contrib import admin
from shopping.models import Order, Merchandise, Option, OptionChoice, OrderItem
from django.utils.translation import ugettext_lazy as _
# Register your models here.


def create_default_choices(mailbox_admin, request, queryset):
	for merch in queryset.all():
		print(f"digesting {merch.merchandise}")
		opt1 = Option(
			option_merchandise_key = merch,
			option = 'Size'
		)
		opt1.save()
		ch1x1 = OptionChoice(
			optionChoice_option_key = opt1,
			choice = 'X-Small'
		)
		ch1x1.save()
		ch1x2 = OptionChoice(
			optionChoice_option_key = opt1,
			choice = 'Small'
		)
		ch1x2.save()
		ch1x3 = OptionChoice(
			optionChoice_option_key = opt1,
			choice = 'Medium'
		)
		ch1x3.save()
		ch1x4 = OptionChoice(
			optionChoice_option_key = opt1,
			choice = 'Large'
		)
		ch1x4.save()
		ch1x5 = OptionChoice(
			optionChoice_option_key = opt1,
			choice = 'X-Large'
		)
		ch1x5.save()
		ch1x6 = OptionChoice(
			optionChoice_option_key = opt1,
			choice = 'X-Large'
		)
		ch1x6.save()
		opt2 = Option(
			option_merchandise_key = merch,
			option = 'Color'
		)
		opt2.save()
		ch2x1 = OptionChoice(
			optionChoice_option_key = opt2,
			choice = 'Navy Blue'
		)
		ch2x1.save()
		ch2x2 = OptionChoice(
			optionChoice_option_key = opt2,
			choice = 'Black'
		)
		ch2x2.save()
		ch2x3 = OptionChoice(
			optionChoice_option_key = opt2,
			choice = 'Grey'
		)
		ch2x3.save()
		ch2x4 = OptionChoice(
			optionChoice_option_key = opt2,
			choice = 'Red'
		)
		ch2x4.save()

create_default_choices.short_description = _('Create Default Choices')

class OrderAdmin(admin.ModelAdmin):
	list_display = (
		'order_id',
		'name',
		'date',
		'time',
	)

class MerchandiseAdmin(admin.ModelAdmin):
	list_display = (
	'id',
	'merchandise',
	'image',
    'price'
	)
	actions = [create_default_choices]

class OptionAdmin(admin.ModelAdmin):
	list_display = (
	'id',
	'option_merchandise_key',
	'option',
	)

class OptionChoiceAdmin(admin.ModelAdmin):
	list_display = (
	'id',
	'optionChoice_option_key',
	'choice',
	)

class OrderItemAdmin(admin.ModelAdmin):
	list_display = (
	'orderItem_order_key',
    'orderItem_merchandise_key',
	)

admin.site.register(Order, OrderAdmin)
admin.site.register(Merchandise, MerchandiseAdmin)
admin.site.register(Option, OptionAdmin)
admin.site.register(OptionChoice, OptionChoiceAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
