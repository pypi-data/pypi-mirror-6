# -*- coding: utf-8 -*-
 
import os
from . import settings
import gettext
 
# Change this variable to your app name!
#  The translation files will be under
#  @LOCALE_DIR@/@LANGUAGE@/LC_MESSAGES/@APP_NAME@.mo
APP_NAME = "simpleValidator"
 
LOCALE_DIR = path = os.path.join(os.path.dirname(__file__), 'lang') # .mo files will then be located in APP_Dir/i18n/LANGUAGECODE/LC_MESSAGES/
 
DEFAULT_LANGUAGE = settings.LOCALE

 
#lc, encoding = locale.getdefaultlocale()
#if lc:
#    languages = [lc]
 
defaultlang = gettext.translation(APP_NAME, LOCALE_DIR, languages=DEFAULT_LANGUAGE, fallback=True)

def switch_language(lang):
    global defaultlang
    defaultlang = gettext.translation(APP_NAME, LOCALE_DIR, languages=[lang], fallback=True)
