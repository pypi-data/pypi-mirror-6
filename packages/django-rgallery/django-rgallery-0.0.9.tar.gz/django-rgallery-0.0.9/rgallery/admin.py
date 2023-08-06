# -*- coding: utf-8 -*-

from django.contrib import admin
import models as mymodels
import forms as myforms
import socket

from engine import expire_view_cache


class FolderAdminForm(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['title']}


class PhotoAdminForm(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        expire_view_cache("app_gallery-gallery")
        obj.save()


admin.site.register(mymodels.Photo, PhotoAdminForm)
admin.site.register(mymodels.Video)
admin.site.register(mymodels.Folder, FolderAdminForm)
