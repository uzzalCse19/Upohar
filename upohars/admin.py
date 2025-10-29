from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Category, UpoharPost, UpoharImage, UpoharRequest

admin.site.register(Category)
admin.site.register(UpoharPost)
admin.site.register(UpoharImage)
admin.site.register(UpoharRequest)
