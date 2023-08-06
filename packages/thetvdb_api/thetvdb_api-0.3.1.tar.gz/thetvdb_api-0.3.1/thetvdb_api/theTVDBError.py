# -*- coding: utf-8 -*-

class theTVDBError(Exception):
  pass

class theTVDBConnectionError(theTVDBError):
  pass
  
class theTVDBXMLError(theTVDBError):
  pass