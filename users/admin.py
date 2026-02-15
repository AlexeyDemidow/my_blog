from django.contrib import admin
from django.db.models import Count
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import CustomUser, UserFollow


@admin.register(UserFollow)
class UserFollowAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'follower',
        'following',
        'created_at',
    )

    list_select_related = (
        'follower',
        'following',
    )

    list_filter = (
        'created_at',
    )

    ordering = (
        '-created_at',
    )

    readonly_fields = (
        'created_at',
    )

    def save_model(self, request, obj, form, change):
        obj.full_clean()
        super().save_model(request, obj, form, change)


class FollowersInline(admin.TabularInline):
    model = UserFollow
    fk_name = 'following'
    extra = 0
    verbose_name = 'Подписчик'
    verbose_name_plural = 'Подписчики'


class FollowingInline(admin.TabularInline):
    model = UserFollow
    fk_name = 'follower'
    extra = 0
    verbose_name = 'Подписка'
    verbose_name_plural = 'Подписки'


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('avatar_preview', 'email', 'username', 'is_staff', 'id', 'followers_count', 'following_count',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('username', 'bio', 'avatar')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    inlines = (
        FollowersInline,
        FollowingInline,
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            followers_cnt=Count('followers'),
            following_cnt=Count('following'),
        )

    def followers_count(self, obj):
        return obj.followers_cnt
    followers_count.short_description = 'Подписчики'

    def following_count(self, obj):
        return obj.following_cnt
    following_count.short_description = 'Подписки'

    def avatar_preview(self, obj):
        if obj.avatar:
            return mark_safe(f'<img src="{obj.avatar.url}" width="40" />')
        return "-"
    avatar_preview.short_description = "Аватар"
