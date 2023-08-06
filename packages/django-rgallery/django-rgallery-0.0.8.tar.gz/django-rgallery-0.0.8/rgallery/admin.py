# -*- coding: utf-8 -*-

from django.contrib import admin
import models as mymodels
import forms as myforms
import socket

class FolderAdminForm(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['title']}


admin.site.register(mymodels.Photo)
admin.site.register(mymodels.Video)
admin.site.register(mymodels.Folder, FolderAdminForm)
