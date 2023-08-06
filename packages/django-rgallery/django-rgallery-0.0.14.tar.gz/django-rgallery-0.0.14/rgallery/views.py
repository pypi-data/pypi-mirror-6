# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.contrib.sites.models import Site
from django.contrib import messages
import models as mymodels
import forms as myforms

from django.conf import settings as conf

from django.views.generic import DetailView, ListView


class Photos(ListView):

    template_name = "rgallery/photos.html"
    context_object_name = "photos"
    paginate_by = 51

    def get_queryset(self):
        return mymodels.Photo.objects.all().filter(status=1, folder__isnull=True).order_by('-capture_date')

    def get_context_data(self, **kwargs):
        context = super(Photos, self).get_context_data(**kwargs)
        folders = mymodels.Folder.objects.filter(status=1)

        context.update({
            'title': _(u'Photos'),
            'folders': folders,
        })
        return context


class PhotosFolder(ListView):

    template_name = "rgallery/photos.html"
    context_object_name = "photos"

    def get_queryset(self):
        folder = mymodels.Folder.objects.get(slug=self.kwargs['folder'])
        return mymodels.Photo.objects.all().filter(status=1, folder=folder).order_by('-capture_date')

    def get_context_data(self, **kwargs):
        context = super(PhotosFolder, self).get_context_data(**kwargs)

        context.update({
            'title': _(u'Photos'),
        })
        return context


class Videos(ListView):

    template_name = "rgallery/videos.html"
    context_object_name = "videos"
    paginate_by = 6

    def get_queryset(self):
        vid = mymodels.Video.objects.all().filter(status=1, folder__isnull=True).order_by('-capture_date')
        print vid
        return vid

    def get_context_data(self, **kwargs):
        context = super(Videos, self).get_context_data(**kwargs)
        context.update({
            'title': _(u'Videos'),
        })
        return context