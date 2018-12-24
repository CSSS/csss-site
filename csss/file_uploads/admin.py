from django.contrib import admin

from .models import Example, ExampleFile ,  Example2


class ExampleFileInline(admin.TabularInline):
    model = ExampleFile


class Example2Admin(admin.ModelAdmin):
    inlines = [ExampleFileInline]


admin.site.register(Example)
admin.site.register(Example2, Example2Admin)