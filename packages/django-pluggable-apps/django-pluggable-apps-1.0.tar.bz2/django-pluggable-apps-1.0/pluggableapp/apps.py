# -*- coding: utf-8 -*-
from pluggableapp.core import PluggableApp, URLWrapper

class AdminWrapper(URLWrapper):
    def __call__(self):
        from django.contrib import admin as adminui
        return adminui.site.urls
    def __repr__(self):
        return repr('django.contrib.admin.site.urls')


def admin(**kw):
    kw.update(distribution='Django')
    app = PluggableApp('django.contrib.admin', **kw)
    app.append_app()
    app.append_app('django.contrib.auth')
    app.append_app('django.contrib.sessions')
    app.append_app('django.contrib.contenttypes')
    app.append("TEMPLATE_CONTEXT_PROCESSORS", "django.core.context_processors.auth")
    app.append('MIDDLEWARE_CLASSES',
                    'django.middleware.common.CommonMiddleware',
                    'django.contrib.sessions.middleware.SessionMiddleware',
                    'django.contrib.auth.middleware.AuthenticationMiddleware')
    app.register_pattern('', r'^admin/', AdminWrapper())
    return app

def admin_docs(**kw):
    kw.update(distribution='Django')
    app = PluggableApp('django.contrib.admindocs', **kw)
    app.register_pattern('', r'^admin/doc/', 'django.contrib.admindocs.urls'),
    return app

def attachments(**kw):
    kw.update(distribution='django-attachments')
    app = PluggableApp('attachments', **kw)
    app.append_app()
    app.append("TEMPLATE_CONTEXT_PROCESSORS", "django.core.context_processors.media",
                                              "django.core.context_processors.request")
    app.insert_app_templates()
    app.register_pattern('', r'^attachments/', 'attachments.urls')
    return app

def i18n(**kw):
    app = PluggableApp('i18n', **kw)
    app.append("TEMPLATE_CONTEXT_PROCESSORS", "django.core.context_processors.i18n")
    app.append("MIDDLEWARE_CLASSES", 'django.middleware.locale.LocaleMiddleware')
    return app

def messages(**kw):
    kw.update(distribution='django-messages')
    app = PluggableApp('messages', **kw)
    app.append_app()
    app.insert_app_templates()
    app.register_pattern('', r'^messages/', 'messages.urls')
    return app

def reversion(**kw):
    kw.update(distribution='django-reversion')
    app = PluggableApp('reversion', **kw)
    app.append_app()
    app.insert('MIDDLEWARE_CLASSES', 'django.middleware.transaction.TransactionMiddleware',
               before='django.middleware.common.CommonMiddleware')
    app.append('MIDDLEWARE_CLASSES', 'reversion.middleware.RevisionMiddleware',
               after='django.contrib.auth.middleware.AuthenticationMiddleware')
    return app

def pagination(**kw):
    kw.update(distribution='django-pagination')
    app = PluggableApp('pagination', **kw)
    app.append_app()
    app.append("MIDDLEWARE_CLASSES", 'pagination.middleware.PaginationMiddleware')
    app.insert_app_templates()
    return app

def registration(**kw):
    kw.update(distribution='django-registration')
    app = PluggableApp('registration', **kw)
    app.append_app()
    app.insert_app_templates()
    app.register_pattern('', r'^accounts/', 'registration.urls')
    return app

def easy_thumbnails(**kw):
    kw.update(distribution='easy-thumbnails')
    app = PluggableApp('easy_thumbnails', **kw)
    app.append_app()
    return app
