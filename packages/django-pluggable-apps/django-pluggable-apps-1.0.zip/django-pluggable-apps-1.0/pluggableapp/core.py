# -*- coding: utf-8 -*-
from django.conf import global_settings
import pkg_resources
import logging
import pickle
import stat
import sys
import os

log = logging.getLogger('pluggableapp')

class URLWrapper(object):
    def __call__(self):
        return None
    def __repr__(self):
        return '<URLWrapper %r>' % repr(self())

class PluggableApp(object):

    apps = {}
    urls = {}
    medias = {}
    settings = {}
    registered_apps = {}

    def __init__(self, name, **kw):
        self.app_name = name
        kw.update(name=name)
        self.kw = kw
        PluggableApp.apps[name] = self

    @classmethod
    def append(self, setting_key, *values, **kwargs):
        """Append ``values`` to ``setting_key``"""
        after = kwargs.get('after', None)
        if setting_key not in self.settings:
            self.settings[setting_key] = getattr(global_settings, setting_key, ())
        values = [v for v in values if v not in self.settings[setting_key]]
        if values:
            attr_value = list(self.settings[setting_key])
            if after and after in attr_value:
                index = attr_value.index(after) + 1
                attr_value[index:index] = values
            else:
                attr_value = attr_value + values
            self.settings[setting_key] = tuple(attr_value)

    @classmethod
    def insert(self, setting_key, *values, **kwargs):
        """Insert ``values`` to ``setting_key``"""
        before = kwargs.get('before', None)
        if setting_key not in self.settings:
            self.settings[setting_key] = getattr(global_settings, setting_key, ())
        values = [v for v in values if v not in self.settings[setting_key]]
        if values:
            attr_value = list(self.settings[setting_key])
            if before and before in attr_value:
                index = attr_value.index(before)
                attr_value[index:index] = values
            else:
                attr_value = values + attr_value
            self.settings[setting_key] = tuple(attr_value)

    def append_app(self, app_name=None):
        """Append ``app_name`` to ``INSTALLED_APPS``"""
        app_name = app_name or self.app_name
        self.append('INSTALLED_APPS', app_name)

    def insert_templates(self, template_dir):
        """Insert ``template_dir`` to ``TEMPLATE_DIRS``"""
        if not os.path.isdir(template_dir) and '.py' in template_dir[-4:]:
            dirname = os.path.dirname(template_dir)
            template_dir = os.path.join(dirname, 'templates')
        if os.path.isdir(template_dir):
            self.append('TEMPLATE_DIRS', template_dir)

    def insert_app_templates(self):
        """Insert ``app_dir/templates`` to ``TEMPLATE_DIRS``"""
        if self.is_installed():
            app = self.get_app()
            self.insert_templates(app.__file__)

    def initialize_settings(self, **kwargs):
        """Initialize some settings values if not already defined"""
        if kwargs:
            for k, v in kwargs.items():
                if k.isupper() and k not in self.settings:
                    self.settings[k] = v

    def is_installed(self):
        distribution = self.kw.get('distribution', None)
        if distribution:
            try:
                distribution = pkg_resources.get_distribution(distribution)
            except pkg_resources.DistributionNotFound:
                return False
            else:
                return distribution
        else:
            try:
                mod = self.get_app()
            except ImportError:
                return False
            return mod

    def get_module(self, module_name):
        try:
            app = __import__(module_name, {}, {}, [''])
        except ImportError, e:
            log.error('Unable to load app %s: %s', module_name, e)
            raise
        else:
            return app

    def get_app(self):
        return self.get_module(self.app_name)

    def register_logger(self, key, config):
        self.settings.setdefault(
            'LOGGING', {}
        ).setdefault(
            'loggers', {}
        )[key] = config

    def register_pattern(self, app_prefix, prefix, module=None):
        """Register an url pattern"""
        prefix = self.kw.get('url_prefix', prefix)
        if prefix:
            if module is None:
                try:
                    mod = self.get_module(self.app_name)
                except ImportError:
                    return
                else:
                    dirname = os.path.dirname(mod.__file__)
                    if not os.path.isfile(os.path.join(dirname, 'urls.py')):
                        return
                    module = '%s.urls' % self.app_name
            self.urls[prefix] = (app_prefix, prefix, module)

    def register_media(self, media_dir=None):
        """Register a media directory. PluggableApp while create a symlink in
        ``MEDIA_ROOT`` for each subdirectory found"""

        if 'MEDIA_ROOT' in self.settings:
            project_media_root = self.settings['MEDIA_ROOT']
            assert os.path.isdir(project_media_root)
        else:
            return

        if media_dir is None:
            try:
                mod = self.get_module(self.app_name)
            except ImportError:
                return
            else:
                media_dir = os.path.dirname(mod.__file__)

        if not os.path.isdir(media_dir) and '.py' in media_dir[-4:]:
            media_dir = os.path.dirname(media_dir)

        subdir = os.path.basename(media_dir)
        if subdir not in ('media', 'medias'):
            for name in ('media', 'medias'):
                dirname = os.path.join(media_dir, name)
                if os.path.isdir(dirname):
                    media_dir = dirname
                    break

        if os.path.isdir(media_dir):
            dirnames = os.listdir(media_dir)
            for subdir in dirnames:
                self.medias[subdir] = os.path.join(media_dir, subdir)
                new_dir = os.path.join(project_media_root, subdir)
                if not os.path.isdir(new_dir):
                    os.symlink(self.medias[subdir], new_dir)
        else:
            raise OSError(media_dir)

    @classmethod
    def load(cls, app_name, **kw):
        if app_name in cls.registered_apps:
            log.info('loading %s from entry_point', app_name)
            entry_point = cls.registered_apps[app_name]
            kw['entry_point'] = app_name
            app = entry_point(**kw)
        else:
            log.info('loading %s from module', app_name)
            app = cls(app_name, **kw)
            app.append_app()
            app.insert_app_templates()
            app.register_pattern('', r'^/%s/' % app_name)
            app.initialize_settings(**kw)
        return app

    @classmethod
    def _initialize(cls):
        # load apps
        pluggable_apps = cls.settings.get('PLUGGABLE_APPS', [])
        cls.load_apps()
        apps = {}
        for kw in pluggable_apps:
            if isinstance(kw, basestring):
                kw = dict(name=kw)
            kw = kw.copy()
            name = kw.pop('name')
            app = cls.load(name, **kw)
            apps[name] = app

    @classmethod
    def initialize(cls, settings, urls=None, dumpfile=None):

        cls.settings = settings

        if 'DJANGO_SETTINGS_DUMP' in settings:
            dumpfile = settings['DJANGO_SETTINGS_DUMP']
        else:
            dumpfile = os.environ.get('DJANGO_SETTINGS_DUMP', dumpfile)

        # unpickle
        if dumpfile and os.path.isfile(dumpfile):
            filename, ext = os.path.splitext(settings['__file__'])
            filename = '%s.py' % filename
            # check if settings.py is more recent than dumpfile
            if os.stat(dumpfile)[stat.ST_MTIME] >= os.stat(filename)[stat.ST_MTIME]:
                fd = open(dumpfile, 'rb')
                conf = pickle.load(fd)
                for k, v in conf.items():
                    setattr(cls, k, v)
                return
            else:
                log.warn('settings have changed. Re-pickling...')

        cls._initialize()

        # pickle
        if dumpfile:
            fd = open(dumpfile, 'wb')
            pickable_settings = dict([(k, v) for k, v in cls.settings.items() if k.isupper()])
            conf = dict(urls=cls.urls, settings=pickable_settings)
            pickle.dump(conf, fd)
            fd.close()

    @classmethod
    def patterns(cls):
        from django.conf.urls.defaults import patterns as django_patterns
        from django.conf.urls.defaults import include
        urls = cls.urls
        urlpatterns = django_patterns('')
        for k in sorted(urls, reverse=True):
            app_prefix, prefix, module = urls[k]
            if isinstance(module, URLWrapper):
                module = module()
            if isinstance(module, basestring):
                module = include(module)
            log.info('Bounding %r:%r', app_prefix, prefix)
            log.debug('%r:%r -> %s', app_prefix, prefix, module)
            urlpatterns += django_patterns(app_prefix, (prefix, module),)
        return urlpatterns

    @classmethod
    def load_apps(cls):
        if not PluggableApp.registered_apps:
            for entry_point in pkg_resources.iter_entry_points('django.pluggable_app'):
                log.debug('Found %s', entry_point.name)
                cls.registered_apps[entry_point.name] = entry_point.load()

    @classmethod
    def setLevel(cls, level=None):
        if level is not None:
            log.setLevel(level)

    def __repr__(self):
        return '<PluggableApp %s>' % self

    def __str__(self):
        kw = self.kw.copy()
        kw.update(distribution=self.is_installed() or '%(distribution)s (not installed)' % self.kw)
        if 'entry_point' in self.kw:
            return '%(entry_point)s: %(name)s from %(distribution)s' % kw
        else:
            return '%(name)s - %(distribution)s' % kw
