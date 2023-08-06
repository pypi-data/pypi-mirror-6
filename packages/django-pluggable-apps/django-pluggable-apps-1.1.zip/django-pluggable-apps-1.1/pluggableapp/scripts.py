# -*- coding: utf-8 -*-
import os
import pprint
import logging
from optparse import OptionParser

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from pluggableapp.core import PluggableApp
PluggableApp.setLevel(logging.WARN)

def main():


    parser = OptionParser()
    parser.add_option("-l", "--list-apps", dest="list_apps",
                      action="store_true", default=False)
    parser.add_option("-i", "--installed-apps", dest="installed_apps",
                      action="store_true", default=False)
    parser.add_option("-u", "--print-urls", dest="print_urls",
                      action="store_true", default=False)
    parser.add_option("-p", "--print-settings", dest="print_settings",
                      action="store_true", default=False)

    options, args = parser.parse_args()

    if options.list_apps:
        PluggableApp.load_apps()
        print 'Available apps'
        print '=============='
        for k, v in sorted(PluggableApp.registered_apps.items()):
            sets = dict(INSTALLED_APPS=(), MIDDLEWARE_CLASSES=(),
                        TEMPLATE_CONTEXT_PROCESSORS=(), TEMPLATE_DIRS=())
            PluggableApp.urls = {}
            try:
                app = v(entry_point=k)
            except ImportError:
                # app not installed
                pass
            else:
                print '- %s' % app
                for k in sorted(app.urls, reverse=True):
                    print '   %s: %s' % (k, app.urls[k])
        print ''

    try:
        import settings
    except ImportError:
        return

    PluggableApp.urls = {}
    PluggableApp._initialize()

    if options.installed_apps:
        print 'Installed apps'
        print '=============='
        for k, app in sorted(PluggableApp.apps.items()):
            print '- %s' % app
        print ''
        print 'Generated urls'
        print '=============='
        for k in sorted(PluggableApp.urls, reverse=True):
            print '- %s: %s' % (k, PluggableApp.urls[k])
        print ''

    if options.print_urls:
        print 'urls'
        print '===='
        for k in sorted(PluggableApp.urls, reverse=True):
            print '- %s: %s' % (k, PluggableApp.urls[k])
        print ''

    if options.print_settings:
        print 'Final settings'
        print '=============='
        keys = sorted(settings.__dict__.iterkeys())
        for k in keys:
            if k.isupper():
                v = pprint.pformat(settings.__dict__[k])
                if v.startswith("(("):
                    v = '(\n %s\n)' % v[1:-1]
                if v.startswith("('"):
                    v = '(\n %s\n)' % v[1:-1]
                if v.startswith("['"):
                    v = '[\n %s\n]' % v[1:-1]
                print '%s = %s' % (k, v)

