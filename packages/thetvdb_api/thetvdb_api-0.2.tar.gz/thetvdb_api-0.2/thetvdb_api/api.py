# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from Logger import *
from theTVDB import theTVDB

logger = logging.getLogger('thetvdb_api')

def set_series(series_name, api_key, language=None):
  """
  Constructor of the class

  params:
  series_name: string: the name of the series
  language: string: a language accepted by theTVDB
  """
  return theTVDB(series_name, api_key, language)

def set_language(series, language):
  """
  Set the language to use
  
  params:
  series:theTVDB object: the series created with set_series()
  language: string: a language accepted by theTVDB
  """
  return series.set_language(language)

def get_series(series):
  """
  Get the series info
  
  params:
  series:theTVDB object: the series created with set_series()
  
  returns:
  dictionnary: all the series infos provided by theTVDB
  """
  return series.get_series()
  
def get_episode(series, episode_season, episode_number, language=None):
  """
  Retrieve the episode data
  
  params:
  series:theTVDB object: the series created with set_series()
  episode_season: string: the number of the season
  episode_number: string: the number of the episode in the season
  language: string: the language to search for in TVDB
  
  returns:
  dictionnary: the episode infos
  
  raises:
  theTVDBError if something went wrong
  """
  return series.get_episode(episode_season, episode_number, language)
  
def get_banners(series):
  """
  Get a dictionnary of all banners
  
  params:
  series:theTVDB object: the series created with set_series()
  
  returns:
  dictionnary: all the banners of the series
  
  raises:
  theTVDBError if something went wrong
  """
  return series.get_banners()

def get_actors(series):
  """
  Get a dictionnary of all actors
  
  returns:
  dictionnary: all the actors of the series
  
  raises:
  theTVDBError if something went wrong
  """
  return series.get_actors()