from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile

# Inline admin for UserProfile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

# Extend the existing UserAdmin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'date_joined', 'is_active')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register UserProfile separately for direct access
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_type', 'phone_number', 'company_name', 'created_at')
    list_filter = ('is_company', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'company_name')
    readonly_fields = ('created_at', 'updated_at')
