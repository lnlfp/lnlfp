from django.contrib import admin
from loader.models import Feed, File, Column


class FeedAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,
         {'fields': ['name',
                     'users']}
         )
    ]
    list_display = ('name',)


class FileAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,
         {'fields': ['file_name',
                     'feed',
                     'user']}
         )
    ]

    list_display = ['user', 'upload_date', 'file_name']


class ColumnAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,
         {'fields': ['name',
                     'col_type']}
         )
    ]
    list_display = ('name', 'col_type',)


admin.site.register(Feed, FeedAdmin)
admin.site.register(File, FileAdmin)
admin.site.register(Column, ColumnAdmin)
