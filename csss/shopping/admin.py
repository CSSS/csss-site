# Register your models here.
from django.contrib import admin
from shopping.models import Order, Merchandise, Feature, Specification, OrderItem, OrderItemSpecification, Customer, SourceFile
from django.utils.translation import ugettext_lazy as _
# Register your models here.

import json

def create_default_Specifications(mailbox_admin, request, queryset):
	for merch in queryset.all():
		print(f"digesting {merch.merchandise_type}")
		opt1 = Feature(
			merchandise_key = merch,
			feature_type = 'Size'
		)
		opt1.save()
		ch1x1 = Specification(
			feature_key = opt1,
			Specification = 'X-Small'
		)
		ch1x1.save()
		ch1x2 = Specification(
			feature_key = opt1,
			Specification = 'Small'
		)
		ch1x2.save()
		ch1x3 = Specification(
			feature_key = opt1,
			Specification = 'Medium'
		)
		ch1x3.save()
		ch1x4 = Specification(
			feature_key = opt1,
			Specification = 'Large'
		)
		ch1x4.save()
		ch1x5 = Specification(
			feature_key = opt1,
			Specification = 'X-Large'
		)
		ch1x5.save()
		ch1x6 = Specification(
			feature_key = opt1,
			Specification = 'X-Large'
		)
		ch1x6.save()
		opt2 = Feature(
			merchandise_key = merch,
			feature_type = 'Color'
		)
		opt2.save()
		ch2x1 = Specification(
			feature_key = opt2,
			Specification = 'Navy Blue'
		)
		ch2x1.save()
		ch2x2 = Specification(
			feature_key = opt2,
			Specification = 'Black'
		)
		ch2x2.save()
		ch2x3 = Specification(
			feature_key = opt2,
			Specification = 'Grey'
		)
		ch2x3.save()
		ch2x4 = Specification(
			feature_key = opt2,
			Specification = 'Red'
		)
		ch2x4.save()

create_default_Specifications.short_description = _('Create Default Specifications')

class CustomerAdmin(admin.ModelAdmin):
    list_display = (
    'name',
    'get_sfu_email'
    )
    def get_sfu_email(self, obj):
        return obj.sfu_email
    get_sfu_email.short_description = "SFU Email"
    get_sfu_email.admin_order_field = "sfu_email"

admin.site.register(Customer, CustomerAdmin)

class OrderAdmin(admin.ModelAdmin):
    list_display = (
    'get_order_id',
    'get_customer_name',
    'date',
    'time'
    )
    def get_order_id(self, obj):
        return obj.order_id
    get_order_id.short_description = 'Order ID'
    get_order_id.admin_order_field = 'order_id'

    def get_customer_name(self, obj):
        return obj.customer_key.name
    get_customer_name.short_description = 'Customer Name'
    get_customer_name.admin_order_field = 'customer_name'

admin.site.register(Order, OrderAdmin)

class MerchandiseAdmin(admin.ModelAdmin):
	list_display = (
	'id',
	'merchandise_type',
	'image_absolute_file_path',
    'price',
	'active'
	)
	actions = [create_default_Specifications]

admin.site.register(Merchandise, MerchandiseAdmin)


class FeatureAdmin(admin.ModelAdmin):
	list_display = (
	'id',
	'merchandise_key',
	'feature_type',
	'active'
	)

admin.site.register(Feature, FeatureAdmin)


class FeatureSpecificationAdmin(admin.ModelAdmin):
	list_display = (
	'id',
	'feature_key',
	'specification_type',
	'active'
	)

admin.site.register(Specification, FeatureSpecificationAdmin)


class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
    'get_order_id',
    'get_order_merchandises',
	'quantity'
    )
    def get_order_id(self, obj):
        return obj.order_key.order_id
    get_order_id.short_description = 'Order ID'
    get_order_id.admin_order_field = 'order_id'

    def get_order_merchandises(self, obj):
        return obj.orderItem_merchandise_key.merchandise_type
    get_order_merchandises.short_description = 'Merchandise'
    get_order_merchandises.admin_order_field = 'Merchandise'

admin.site.register(OrderItem, OrderItemAdmin)

class OrderItemSpecificationAdmin(admin.ModelAdmin):
    list_display = (
        'get_order_id',
        'get_merchandise',
        'get_merchandise_Feature',
        'get_merchandise_Feature_Specification'
    )
    def get_order_id(self, obj):
        return obj.OrderFeatureSpecificationSelected_orderItem_key.order_key.order_id
    get_order_id.short_description = 'Order ID'
    get_order_id.admin_order_field = 'order_id'

    def get_merchandise(self, obj):
        return obj.OrderFeatureSpecificationSelected_orderItem_key.orderItem_merchandise_key.merchandise_type
    get_merchandise.short_description = 'Merchandise'
    get_merchandise.admin_order_field = 'Merchandise'

    def get_merchandise_Feature(self, obj):
        return obj.OrderFeatureSpecificationSelected_Feature_key.Feature
    get_merchandise_Feature.short_description = 'feature'
    get_merchandise_Feature.admin_order_field = 'feature'

    def get_merchandise_Feature_Specification(self, obj):
        return obj.OrderFeatureSpecificationSelected_FeatureSpecification_key.Specification
    get_merchandise_Feature_Specification.short_description = 'Specification'
    get_merchandise_Feature_Specification.admin_order_field = 'Specification'

admin.site.register(OrderItemSpecification, OrderItemSpecificationAdmin)

def getMerch(image, merchandise_type, price):
	retrievedObjects = Merchandise.objects.all().filter(
		merchandise_type = merchandise_type,
		image_absolute_file_path = image,
		price = price
	)
	if len(retrievedObjects) == 0:
		merch = Merchandise(
			merchandise_type = merchandise_type,
			image_absolute_file_path = image,
			price = price,
			active = True
		)
		merch.save()
		return merch
	retrievedObjects[0].active = True
	return retrievedObjects[0]

def getFeature(merchandise_key, feature_type):
	retrievedObjects = Feature.objects.all().filter(
		merchandise_key = merchandise_key,
		feature_type = feature_type
	)
	if len(retrievedObjects) == 0:
		feature = Feature(
			merchandise_key = merchandise_key,
			feature_type = feature_type,
			active = True
		)
		feature.save()
		return feature
	retrievedObjects[0].active = True
	return retrievedObjects[0]

def saveMerchandise(merch):
	savedMerch = getMerch(merch['image'] , merch['merchandise_type'], merch['price'])
	for feature in merch['Feature']:
		print(f"feature={feature}")
		savedFeature = getFeature(savedMerch, merch['Feature'][feature]['feature_type'])
		for spec in merch['Feature'][feature]['specification']:
			print(f"spec={spec}")
			retrievedObjects = Specification.objects.all().filter(
				feature_key = savedFeature,
				specification_type = spec
			)
			if len(retrievedObjects) == 0:
				savedSpec = Specification(
					feature_key = savedFeature,
					specification_type = spec,
					active = True
				)
				savedSpec.save()
			else:
				retrievedObjects[0].active = True

def import_merchandise(file):
	print(f"[import_merchandise] will now try and read file {file}")
	with open(file) as f:
		merchs = json.load(f)
		print(f"merches={merchs}")
		for merch in merchs:
			print(f"merch={merch}")
			saveMerchandise(merch)

def import_specific_merchandise(mailbox_admin, request, queryset):
    for file in queryset.all():
        import_merchandise(str(file.json_file.file))

import_specific_merchandise.short_description = _('Save Mercandise Specified in File')

class SourceFileAdmin(admin.ModelAdmin):
    list_display = (
		'json_file',
	)

    actions = [import_specific_merchandise]


admin.site.register(SourceFile, SourceFileAdmin)
