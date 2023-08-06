from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Category, Article
from .forms import ArticleAdminForm


class CategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for Category model.
    """
    list_display = ('title', 'slug','order')
    list_editable = ( 'order', )
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
admin.site.register(Category, CategoryAdmin)


class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm
    list_display = ('title', 'slug', 'publish', 'publish_on')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_on', 'updated_on')
    date_hierarchy = 'publish_on'
    fieldsets = (
        (
            _('Article'),
            {
                'fields': ('title', 'slug', 'category', 'content', 'image'),
            }
        ),
        (
            _('Publish'),
            {
                'fields': ('publish', 'publish_on'),
            }
        ),
        (
            _('Record Details'),
            {
                'fields': ('created_on', 'updated_on'),
                'classes': ('collapse',)
            }
        )
    )
admin.site.register(Article, ArticleAdmin)
