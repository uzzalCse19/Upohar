from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "email", "role", "status", "total_donations"]
    search_fields = ["name", "email", "role"]
    list_filter = ["role", "status"]
    ordering = ["-date_joined"]
