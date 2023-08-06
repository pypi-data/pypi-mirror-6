# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import urllib2
import xml.etree.ElementTree as ElementTree
from Logger import *
from conf import *
from utils import *
from theTVDBError import *

logger = logging.getLogger('thetvdb_api')

class theTVDB(object):
  """
  A theTVDB.com Python API
  """
  def __init__(self, series_name, api_key, language=None):
    """
    Constructor of the class
    
    params:
    series_name: string: the name of the series
    language: string: a language accepted by theTVDB
    """
    self.__api_key = api_key
    self.__series_name = str(series_name.encode('utf-8'))
    if language is None:
      language = ALL_LANGUAGES
      self.set_series(language)
    else:
      self.set_language(language)

  def set_language(self, language):
    """
    Set the language to use
    
    params:
    language: string: a language accepted by theTVDB
    """
    if language in AVAILABLE_LANGUAGES:
      self.__language = language
      logger.debug('Language {language} set.'.format(language=language))
      self.set_series(language)
    else:
      raise theTVDBError('This language is not supported by theTVDB. Available languages are: '+str(self.__get_languages()).strip('[]')+'.')
  
  def __get_languages(self):
    """
    Return a list with all available languages
    
    returns:
    list: a list in the format language_code (language_name)
    """
    list=[]
    for lang in AVAILABLE_LANGUAGES:
      list.append(lang.encode('utf-8')+' ('.encode('utf-8')+AVAILABLE_LANGUAGES[lang]['name']+')'.encode('utf-8'))
    return list
  
  def set_series(self, language=None):
    """
    Set the series info
    
    params:
    language: string: a language accepted by theTVDB (optional)
    
    raises:
    theTVDBError if something went wrong
    """
    self.__series_infos = None
    if language is None:
      if self.__language is None:
        language = DEFAULT_LANGUAGE
      else:
        language = self.__language
    
    if language == ALL_LANGUAGES:
      self.__set_simple_series()
    else:
      self.__set_full_series(language)
  
  def __set_simple_series(self):
    """
    Set the series info when no language has been specified
    
    raises:
    theTVDBError if something went wrong
    """
    series_name = urllib2.quote(self.__series_name)
    url = ROOT_URL+'GetSeries.php?seriesname={series_name}&language=all'.format(series_name=series_name.lower())
    
    #Get the TVDB xml file
    try:
      logger.debug('Trying to open the url {url}...'.format(url=url))
      series_tree = get_xml_tree(url).find('Series')
    except theTVDBConnectionError as error:
      raise theTVDBError('Could not connect to theTVDB. {error_text}'.format(error_text=error))
      return
    except theTVDBXMLError as error:
      raise theTVDBError('There was an error with the XML retrieved from thetvdb.com. {error_text}'.format(error_text=error))
      return
    
    if series_tree is None:
      raise theTVDBError('This series does not exists at thetvdb.com.')
    
    #Set the series infos
    logger.debug('Constructing the dictionnary of series infos...')
    series_infos = dict()
    for info in series_tree.iter():
      if info.tag in ['banner'] and info.text is not None:  #add the root url
        series_infos[info.tag] = ROOT_URL_BANNERS + info.text
      else:
        series_infos[info.tag] = info.text
    
    self.__series_id = series_infos['seriesid']
    
    #Create a tag with all the names of the series
    series_names = [series_infos['SeriesName']]
    if 'AliasNames' in series_infos and series_infos['AliasNames'] is not None:
      series_names.extend(series_infos['AliasNames'].split('|'))
    series_infos['SeriesNameList'] = series_names
    
    self.__series_infos = series_infos 
  
  def __set_full_series(self, language):
    """
    Set the series info when no language has been specified
    
    params:
    language: string: a language accepted by theTVDB
    
    raises:
    theTVDBError if something went wrong
    """
    self.__set_simple_series()
  
    series_name = urllib2.quote(self.__series_name)
    url = ROOT_URL+'{tvdb_api_key}/series/{series_id}/{series_language}.xml'.format(tvdb_api_key=self.__api_key, series_id=self.__series_id, series_language=language)
    
    #Get the TVDB xml file
    try:
      logger.debug('Trying to open the url {url}...'.format(url=url))
      series_tree = get_xml_tree(url).find('Series')
    except theTVDBConnectionError as error:
      raise theTVDBError('Could not connect to theTVDB. {error_text}'.format(error_text=error))
      return
    except theTVDBXMLError as error:
      raise theTVDBError('There was an error with the XML retrieved from thetvdb.com. {error_text}'.format(error_text=error))
      return
    
    if series_tree is None:
      raise theTVDBError('This series does not exists at thetvdb.com.')
    
    #Set the series infos
    series_infos = dict()
    for info in series_tree.iter():
      if info.tag in ['Actors', 'Genre'] and info.text is not None: #Make list from piped strings
        series_infos[info.tag+'List'] = filter(bool, info.text.split('|'))
        series_infos[info.tag] = info.text
      elif info.tag in ['banner', 'fanart', 'poster'] and info.text is not None:  #add the root url
        series_infos[info.tag] = ROOT_URL_BANNERS + info.text
      else:
        series_infos[info.tag] = info.text
    
    self.__series_infos.update(series_infos)
  
  def get_series(self):
    """
    Get the series info
    
    returns:
    dictionnary: all the series infos provided by theTVDB
    """
    return self.__series_infos
  
  def get_episode(self, episode_season, episode_number, language=None):
    """
    Retrieve the episode data
    
    params:
    episode_season: string: the number of the season
    episode_number: string: the number of the episode in the season
    language: string: the language to search for in TVDB
    
    returns:
    dictionnary: the episode infos
    
    raises:
    theTVDBError if something went wrong
    """
    if language is None:
      if self.__language is None:
        language = DEFAULT_LANGUAGE
      else:
        language = self.__language
    
    url = ROOT_URL+'{tvdb_api_key}/series/{series_id}/default/{episode_season}/{episode_number}/{series_language}.xml'.format(tvdb_api_key=self.__api_key, series_id=self.__series_id, episode_season=episode_season, episode_number=episode_number, series_language=language)
    
    #Get the TVDB xml file
    try:
      logger.debug('Trying to open the url {url}...'.format(url=url))
      episode_tree = get_xml_tree(url).find('Episode')
    except theTVDBConnectionError as error:
      raise theTVDBError('Could not connect to theTVDB. {error_text}'.format(error_text=error))
      return
    except theTVDBXMLError as error:
      raise theTVDBError('There was an error with the XML retrieved from thetvdb.com. {error_text}'.format(error_text=error))
      return
    
    if episode_tree is None:
      raise theTVDBError('This episode does not exists in the language specified ({language}) at thetvdb.com.'.format(language=language))
      return None
    
    #Search for the right season and episode and set the episode name
    logger.debug('Constructing the dictionnary of episode infos...')
    episode_infos = dict()
    for info in episode_tree.iter():
      if info.tag in ['Director', 'Writer', 'GuestStars'] and info.text is not None:
        episode_infos[info.tag+'List'] = info.text.replace(', ', '|').split('|')
        episode_infos[info.tag] = info.text
      elif info.tag in ['filename'] and info.text is not None:  #add the root url
        episode_infos[info.tag] = ROOT_URL_BANNERS + info.text
      else:
        episode_infos[info.tag] = info.text
    
    #Create a tag with the season number
    episode_infos['EpisodeSeason'] = str(episode_season)
    
    return episode_infos
    
  def get_banners(self):
    """
    Get a dictionnary of all banners
    
    returns:
    dictionnary: all the banners of the series
    
    raises:
    theTVDBError if something went wrong
    """
    url = ROOT_URL+'{tvdb_api_key}/series/{series_id}/banners.xml'.format(tvdb_api_key=self.__api_key, series_id=self.__series_id)
    
    # Get the TVDB xml file
    try:
      logger.debug('Trying to open the url {url}...'.format(url=url))
      banners_tree = get_xml_tree(url)
    except theTVDBConnectionError as error:
      raise theTVDBError('Could not connect to theTVDB. {error_text}'.format(error_text=error))
      return
    except theTVDBXMLError as error:
      raise theTVDBError('There was an error with the XML retrieved from thetvdb.com. {error_text}'.format(error_text=error))
      return
    
    if banners_tree is None:
      raise theTVDBError('This series does not exists at thetvdb.com.')
      return None
      
    # Search for the right season and episode and set the episode name
    logger.debug('Constructing the dictionnary of banners...')
    banners = dict()

    for banner_tree in banners_tree.findall('Banner'):
      banner_id = banner_tree.find('id').text
      banners[banner_id] = dict()
      for banner in banner_tree.iter():
        if banner.tag != 'Banner' and banner.tag != 'id':
          if banner.tag in ['BannerPath', 'ThumbnailPath', 'VignettePath'] and banner.text is not None: #add the root url
            banners[banner_id][banner.tag] = ROOT_URL_BANNERS + banner.text
          else:
            banners[banner_id][banner.tag] = banner.text

    return banners
    
  def get_actors(self):
    """
    Get a dictionnary of all actors
    
    returns:
    dictionnary: all the actors of the series
    
    raises:
    theTVDBError if something went wrong
    """
    url = ROOT_URL+'{tvdb_api_key}/series/{series_id}/actors.xml'.format(tvdb_api_key=self.__api_key, series_id=self.__series_id)
    
    # Get the TVDB xml file
    try:
      logger.debug('Trying to open the url {url}...'.format(url=url))
      actors_tree = get_xml_tree(url)
    except theTVDBConnectionError as error:
      raise theTVDBError('Could not connect to theTVDB. {error_text}'.format(error_text=error))
      return
    except theTVDBXMLError as error:
      raise theTVDBError('There was an error with the XML retrieved from thetvdb.com. {error_text}'.format(error_text=error))
      return
    
    if actors_tree is None:
      raise theTVDBError('This series does not exists at thetvdb.com.')
      return None
      
    # Search for the right season and episode and set the episode name
    logger.debug('Constructing the dictionnary of actors...')
    actors = dict()

    for actor_tree in actors_tree.findall('Actor'):
      actor_id = actor_tree.find('id').text
      actors[actor_id] = dict()
      for actor in actor_tree.iter():
        if actor.tag != 'Actor' and actor.tag != 'id':
          if actor.tag in ['Image'] and actor.text is not None: #add the root url
            actors[actor_id][actor.tag] = ROOT_URL_BANNERS + actor.text
          else:
            actors[actor_id][actor.tag] = actor.text

    return actors