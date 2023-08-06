# -*- coding: utf-8 -*-

from django.contrib import admin
import models as mymodels
import forms as myforms
import socket

from engine import expire_view_cache


class FolderAdminForm(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['title']}


class PhotoAdminForm(admin.ModelAdmin):
    list_display = ('image', 'folder', 'capture_date')
    search_fields = ('image', 'origen', )

    def save_model(self, request, obj, form, change):
        expire_view_cache("app_gallery-gallery")
        folders = mymodels.Folder.objects.all()
        if folders is not None:
            for f in folders:
                expire_view_cache("app_gallery-folder", [f.slug])
        obj.save()


admin.site.register(mymodels.Photo, PhotoAdminForm)
admin.site.register(mymodels.Video)
admin.site.register(mymodels.Folder, FolderAdminForm)
