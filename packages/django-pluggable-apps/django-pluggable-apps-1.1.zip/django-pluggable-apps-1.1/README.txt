This is a fork of DjangoPluggableApp which seems to be abandoned

django-pluggable-apps is a package to allow:

- django users to install and configure third-party django applications

- developpers to create an distribute django apps.

django-pluggable-apps is **not** intrusive. This mean that:

- end users can use applications without a DjangoPluggableApp entry_point in
  their projects

- an application based on the provided template can be used by end users
  without DjangoPluggableApp installed.

Installation
============

With easy_install::

  $ easy_install -U django-pluggable-apps

With pip::

  $ pip install django-pluggable-apps
