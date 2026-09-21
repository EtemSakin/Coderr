from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from auth_app.models import Profile, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Coderr', {'fields': ('type',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Coderr', {'fields': ('type',)}),
    )
    list_display = ('username', 'email', 'type', 'is_staff', 'is_active')
    list_filter = ('type', 'is_staff', 'is_active')
    search_fields = ('username', 'email')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'tel', 'working_hours', 'created_at')
    list_filter = ('user__type',)
    search_fields = ('user__username', 'user__email', 'location', 'tel')
