# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from utils import set_urllib_cache
from conf import CACHE_PERIOD
from Logger import *
from theTVDB import theTVDB

logger = logging.getLogger(__name__)

def set_cache(path, period=CACHE_PERIOD):
  """
  Set the cache directory.

  :param str path: path to the cache directory
  :param int period: the period (in seconds) during which the cache is hold
  :raises: :mod:`thetvdb_api.theTVDBError` if unable to create the cache directory
  """
  return set_urllib_cache(path, period)

def set_series(series_name, api_key, language=None):
  """
  Search the series in theTVDB.com database.

  :param str series_name: the name of the series
  :param str api_key: the api key
  :param language: a language accepted by theTVDB.com (see :doc:`languages`) or None
  :type language: str or None
  :returns: a :mod:`thetvdb_api.theTVDB` object to pass as argument to the other api functions
  :rtype: :mod:`thetvdb_api.theTVDB` object
  :raises: :mod:`thetvdb_api.theTVDBError` if something went wrong
  """
  return theTVDB(series_name, api_key, language)

def set_language(series, language):
  """
  Set the language to use.
  
  :param series: the series created with :func:`~thetvdb_api.api.set_series`
  :type series: :mod:`thetvdb_api.theTVDB` object
  :param str language: a language accepted by theTVDB.com (see :doc:`languages`)
  """
  return series.set_language(language)

def get_series(series):
  """
  Get the series informations.
  
  :param series: the series created with :func:`~thetvdb_api.api.set_series`
  :returns: a dictionary of all the series informations provided by theTVDB.com.
  :rtype: dict
  :raises: :mod:`thetvdb_api.theTVDBError` if something went wrong
  """
  return series.get_series()
  
def get_episode(series, episode_season, episode_number, language=None):
  """
  Get an episode informations.
  
  :param series: the series created with :func:`~thetvdb_api.api.set_series`
  :param episode_season: the number of the season
  :type episode_season: int or str
  :param episode_number: the number of the episode in the season
  :type episode_number: int or str
  :param language: a language accepted by theTVDB.com (see :doc:`languages`)
  :type language: str or None
  :returns: a dictionary of all the episode informations provided by theTVDB.com.
  :rtype: dict
  :raises: :mod:`thetvdb_api.theTVDBError` if something went wrong
  """
  return series.get_episode(episode_season, episode_number, language)
  
def get_banners(series):
  """
  Get all the banners of the series.
  
  :param series: the series created with :func:`~thetvdb_api.api.set_series`
  :returns: a dictionary of all the banners of the series provided by theTVDB.com.
  :rtype: dict
  :raises: :mod:`thetvdb_api.theTVDBError` if something went wrong
  """
  return series.get_banners()

def get_actors(series):
  """
  Get all the actors of the series.
  
  :param series: the series created with :func:`~thetvdb_api.api.set_series`
  :returns: a dictionary of all the actors of the series provided by theTVDB.com.
  :rtype: dict
  :raises: :mod:`thetvdb_api.theTVDBError` if something went wrong
  """
  return series.get_actors()