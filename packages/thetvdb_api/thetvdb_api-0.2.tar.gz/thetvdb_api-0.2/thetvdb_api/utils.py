# -*- coding: utf-8 -*-
from __future__ import unicode_literals  
import os
import urllib2
import xml.etree.ElementTree as ElementTree
from Logger import *
from conf import *
from cache import *
from theTVDBError import *

logger = logging.getLogger('thetvdb_api')
opener = None

def set_cache(path, cache_time=CACHE_TIME):
  """
  Set the cache folder

  params:
  path: string: path to the cache folder
  cache_time: int: the time during which the cache is hold in seconds (default: 21600)
  
  raises:
  theTVDBError if unable to create the cache directory
  """
  global opener
  logger.debug('Setting thetvdb_api cache...')
  
  #make an absolute path
  path = os.path.abspath(os.path.expanduser(path.decode('utf-8')))
  
  #make directories if they don't exist
  if not os.path.isdir(path):
    try:
      os.makedirs(path)
    except OSError as error:
      raise theTVDBError("Error while creating the cache folder : {error}".format(error=error.strerror))
     
  #Build the cache handler
  opener = urllib2.build_opener(CacheHandler(path, cache_time))
  
  logger.debug('thetvdb_api cache folder set.')
  
def get_urllib2_opener():
  """
  Returns a urllib2 opener with cache management
  
  returns:
  OpenerDirector: the urllib2 opener
  """
  global opener
  
  if opener is None:
   opener = urllib2.build_opener()
  return opener
  
def get_xml_tree(url):
  """
  Returns a XML tree from url
  
  returns:
  xml.etree.ElementTree
  
  raises:
  theTVDBConnectionError: if cannot connect to url
  theTVDBXMLError: if the xml file is malformed
  """
  #Get the xml file
  try:
    opener = get_urllib2_opener()
    response = opener.open(url)
  except (IOError, urllib2.URLError) as error:
    raise theTVDBConnectionError(error)
    return
  
  #Make the xml
  try:
    tree = ElementTree.fromstring(bytes(response.read()))
  except SyntaxError as error:
    raise theTVDBXMLError(error)
    
  return tree