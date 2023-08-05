from django.contrib import admin

from nomadblog.models import BlogHub, Blog, Category, BlogUser, Country


class CountryAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')


class BlogHubAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )


class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'description')
    search_fields = ('title', 'slug', 'description')
    prepopulated_fields = {'slug': ('title',)}


class BlogUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'blog', 'name', 'bio')
    search_fields = ('user__username', 'user__email', 'blog__title', 'name', 'bio')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Country, CountryAdmin)
admin.site.register(BlogHub, BlogHubAdmin)
admin.site.register(Blog, BlogAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(BlogUser, BlogUserAdmin)
