# -*- coding: utf-8 -*-
CACHE_PERIOD = 21600      #How long the pages get cached (in seconds)
DEFAULT_LANGUAGE = 'en' #Default language if none has been specified
ALL_LANGUAGES = 'all'   #Code of the 'all' language
ROOT_URL = 'http://thetvdb.com/api/'  #Root url for the XML api
ROOT_URL_BANNERS = 'http://thetvdb.com/banners/' #Root url for medias
#List of available languages
AVAILABLE_LANGUAGES = {'en':
                        {'name':'English', 'code':'7'},
                      'sv':
                        {'name':'Svenska', 'code':'8'},
                      'no':
                        {'name':'Norsk', 'code':'9'},
                      'da':
                        {'name':'Dansk', 'code':'10'},
                      'fi':
                        {'name':'Suomeksi', 'code':'11'},
                      'nl':
                        {'name':'Nederlands', 'code':'13'},
                      'de':
                        {'name':'Deutsch', 'code':'14'},
                      'it':
                        {'name':'Italiano', 'code':'15'},
                      'es':
                        {'name':'Español', 'code':'16'},
                      'fr':
                        {'name':'Français', 'code':'17'},
                      'pl':
                        {'name':'Polski', 'code':'18'},
                      'hu':
                        {'name':'Magyar', 'code':'19'},
                      'el':
                        {'name':'Greek', 'code':'20'},
                      'tr':
                        {'name':'Turkish', 'code':'21'},
                      'ru':
                        {'name':'Russian', 'code':'22'},
                      'he':
                        {'name':'Hebrew', 'code':'24'},
                      'ja':
                        {'name':'Japanese', 'code':'25'},
                      'pt':
                        {'name':'Portuguese', 'code':'26'},
                      'zh':
                        {'name':'Chinese', 'code':'27'},
                      'cs':
                        {'name':'Czech', 'code':'28'},
                      'sl':
                        {'name':'Slovenian', 'code':'30'},
                      'hr':
                        {'name':'Croatian', 'code':'31'},
                      'ko':
                        {'name':'Korean', 'code':'32'},
                      }