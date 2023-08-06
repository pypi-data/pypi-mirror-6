# -*- coding: utf-8 -*-

from django.contrib import admin
import rforum.models as mymodels
import forms as myforms
import socket

class AdminForum(admin.ModelAdmin):

    list_display = ('title', 'slug', 'order', 'status', 'visible',)
    # http://www.userlinux.net/django-los-campos-tipo-slug.html
    prepopulated_fields = { 'slug': ['title'] }

    """
    Para agregar TinyMCE en los newforms-admin:
    - http://code.djangoproject.com/wiki/AddWYSIWYGEditor#Withnewforms-admin
    - http://code.djangoproject.com/wiki/AddWYSIWYGEditor
    """

    class Media:
        js = ('js/tiny_mce/tiny_mce.js',
              'js/textareas.js',
              )


class AdminTopic(admin.ModelAdmin):

    list_display = ('title', 'forum', 'status', 'sticky', 'closed',)
    exclude = ('user',)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

    # http://www.userlinux.net/django-los-campos-tipo-slug.html
    prepopulated_fields = { 'slug': ['title'] }



class AdminPost(admin.ModelAdmin):

    list_display = ('body', 'topic', 'user', 'date_created', 'status',)
    #exclude = ('user',)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

    """
    Para agregar TinyMCE en los newforms-admin:
    - http://code.djangoproject.com/wiki/AddWYSIWYGEditor#Withnewforms-admin
    - http://code.djangoproject.com/wiki/AddWYSIWYGEditor
    """

    class Media:
        js = ('js/tiny_mce/tiny_mce.js',
              'js/textareas.js',
              )


class AdminLog(admin.ModelAdmin):

    list_display = ('user', 'action', 'date', 'user_ip',)


admin.site.register(mymodels.Forum, AdminForum)
admin.site.register(mymodels.Topic, AdminTopic)
admin.site.register(mymodels.Post, AdminPost)
admin.site.register(mymodels.Rank)
admin.site.register(mymodels.Log, AdminLog)
