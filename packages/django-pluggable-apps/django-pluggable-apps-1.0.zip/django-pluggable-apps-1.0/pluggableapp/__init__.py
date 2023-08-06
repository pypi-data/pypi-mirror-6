# -*- coding: utf-8 -*-
import logging
from pluggableapp.core import PluggableApp

PluggableApp.setLevel(logging.ERROR)

setLevel = PluggableApp.setLevel
initialize = PluggableApp.initialize
patterns = PluggableApp.patterns
app_dict = PluggableApp.apps
