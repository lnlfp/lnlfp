from django.contrib import admin
from loader.models import Feed, File, Column, Procedure


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

    list_display = ['user', 'upload_date', 'data']


class ColumnAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,
         {'fields': ['name',
                     'col_type']}
         )
    ]
    list_display = ('name', 'col_type',)


class ProcedureAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,
         {'fields': ['name',
                     'language',
                     'comments',
                     'procedure']}
         )
    ]
    list_display = ('name', 'language', 'comments')

admin.site.register(Feed, FeedAdmin)
admin.site.register(File, FileAdmin)
admin.site.register(Column, ColumnAdmin)
admin.site.register(Procedure, ProcedureAdmin)
