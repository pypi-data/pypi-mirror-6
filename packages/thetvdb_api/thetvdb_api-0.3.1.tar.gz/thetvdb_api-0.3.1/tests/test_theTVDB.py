# -*- coding: utf-8 -*-
from __future__ import unicode_literals  
import unittest
import thetvdb_api

thetvdb_api.set_cache('~/.thetvdb_api/cache')
TVDB_API_KEY = 'A883BE325EBEDAD2'

class theTVDBTestCase(unittest.TestCase):
  """
  thetvdb_api class test case
  """
  def test_episode_easy(self):
    series_name = 'Parks and Recreation'
    series = thetvdb_api.set_series(series_name, TVDB_API_KEY, 'en')
    
    series_infos = thetvdb_api.get_series(series)
    self.assertEqual(series_infos['seriesid'], '84912')
    self.assertEqual(series_infos['language'], 'en')
    self.assertEqual(series_infos['SeriesName'], 'Parks and Recreation')
    self.assertEqual(series_infos['AliasNames'], 'Public Service')
    self.assertEqual(series_infos['Overview'], 'The series follows Leslie Knope, the deputy head of the Parks and Recreation department in the fictional town of Pawnee, Indiana. Knope takes on a project with a nurse named Ann to turn a construction pit into a park, while trying to mentor a bored college-aged intern. However, Leslie must fight through the bureaucrats, problem neighbors, and developers in order to make her dream a reality, all while with a camera crew recording her every gaff and mishap.')
    self.assertEqual(series_infos['FirstAired'], '2009-04-09')
    self.assertEqual(series_infos['Network'], 'NBC')
    self.assertEqual(series_infos['IMDB_ID'], 'tt1266020')
    self.assertEqual(series_infos['zap2it_id'], 'SH01128115')
    self.assertEqual(series_infos['banner'], 'http://thetvdb.com/banners/graphical/84912-g10.jpg')
    self.assertEqual(series_infos['Actors'], '|Amy Poehler|Adam Scott|Nick Offerman|Aziz Ansari|Rashida Jones|Aubrey Plaza|Retta|Jim O\'Heir|Rob Lowe|Paul Schneider|Chris Pratt|')
    self.assertEqual(series_infos['Airs_DayOfWeek'], 'Thursday')
    self.assertEqual(series_infos['Genre'], '|Comedy|')
    self.assertEqual(series_infos['Status'], 'Continuing')
    self.assertEqual(series_infos['ActorsList'], ['Amy Poehler', 'Adam Scott', 'Nick Offerman', 'Aziz Ansari', 'Rashida Jones', 'Aubrey Plaza', 'Retta', 'Jim O\'Heir', 'Rob Lowe', 'Paul Schneider', 'Chris Pratt'])
    self.assertEqual(series_infos['GenreList'], ['Comedy'])
    self.assertEqual(series_infos['fanart'], 'http://thetvdb.com/banners/fanart/original/84912-10.jpg')
    self.assertEqual(series_infos['poster'], 'http://thetvdb.com/banners/posters/84912-5.jpg')
    
    episode_infos = thetvdb_api.get_episode(series, 3, 9)
    self.assertEqual(episode_infos['id'], '3990131')
    self.assertEqual(episode_infos['seasonid'], '356251')
    self.assertEqual(episode_infos['EpisodeNumber'], '9')
    self.assertEqual(episode_infos['EpisodeName'], 'Andy and April\'s Fancy Party')
    self.assertEqual(episode_infos['FirstAired'], '2011-04-14')
    self.assertEqual(episode_infos['GuestStars'], 'John Ellison Conlee|Terri Hoyos|Ben Schwartz')
    self.assertEqual(episode_infos['Director'], 'Michael Trim')
    self.assertEqual(episode_infos['Writer'], 'Katie Dippold')
    self.assertEqual(episode_infos['Overview'], 'April and Andy host a dinner party for the Parks Department. Meanwhile, Ann tries to move on from Chris at a singles\' party.')
    self.assertIsNone(episode_infos['ProductionCode'])
    self.assertEqual(episode_infos['lastupdated'], '1371143228')
    self.assertEqual(episode_infos['flagged'], '0')
    self.assertEqual(episode_infos['seriesid'], '84912')
    self.assertEqual(episode_infos['EpisodeSeason'], '3')
    self.assertEqual(episode_infos['filename'], 'http://thetvdb.com/banners/episodes/84912/3990131.jpg')
    self.assertEqual(episode_infos['GuestStarsList'], ['John Ellison Conlee', 'Terri Hoyos', 'Ben Schwartz'])
    
    banners = thetvdb_api.get_banners(series)
    self.assertEqual(banners['763681']['BannerPath'], 'http://thetvdb.com/banners/fanart/original/84912-10.jpg')
    self.assertEqual(banners['758241']['BannerType2'], '1920x1080')
    self.assertEqual(banners['758241']['SeriesName'], 'false')
    self.assertEqual(banners['970818']['ThumbnailPath'], 'http://thetvdb.com/banners/_cache/fanart/original/84912-13.jpg')
    
  def test_episode_accent(self):
    series_name = 'Les Opérateurs'
    series = thetvdb_api.set_series(series_name, TVDB_API_KEY)
    
    series_infos = thetvdb_api.get_series(series)
    self.assertEqual(series_infos['seriesid'], '262579')
    self.assertEqual(series_infos['language'], 'fr')
    self.assertEqual(series_infos['SeriesName'], 'Les Opérateurs')
    self.assertEqual(series_infos['Overview'], 'Slim est engagé pour son premier job dans une grande entreprise et doit partager son bureau avec Fran. Slim ne sait pas pourquoi il a été engagé et découvre à son grand étonnement que Fran ne sait pas ce qu\'elle fait là non plus. Pour qui travaillent-ils vraiment? Et à quoi servent les données qu\'ils collectent à longueur de journée? Charles, leur énigmatique supérieur, ne les aide pas à en savoir plus.')
    self.assertEqual(series_infos['FirstAired'], '2012-10-13')
    self.assertEqual(series_infos['Network'], 'France 4')
    self.assertEqual(series_infos['banner'], 'http://thetvdb.com/banners/graphical/262579-g.jpg')
    self.assertEqual(series_infos['SeriesNameList'], ['Les Opérateurs'])
    
    thetvdb_api.set_language(series, 'fr')
    series_infos = thetvdb_api.get_series(series)
    self.assertEqual(series_infos['Actors'], '||')
    self.assertEqual(series_infos['ActorsList'], [])
    self.assertEqual(series_infos['Genre'], '|Comedy|')
    self.assertEqual(series_infos['GenreList'], ['Comedy'])
    
    episode_infos = thetvdb_api.get_episode(series, 1, 2)
    self.assertEqual(episode_infos['id'], '4417016')
    self.assertEqual(episode_infos['seasonid'], '501363')
    self.assertEqual(episode_infos['EpisodeNumber'], '2')
    self.assertEqual(episode_infos['EpisodeName'], 'Les petites boîtes')
    self.assertEqual(episode_infos['FirstAired'], '2012-10-15')
    self.assertIsNone(episode_infos['GuestStars'])
    self.assertEqual(episode_infos['Director'], 'François Descraques, Slimane-Baptiste Berhoun')
    self.assertEqual(episode_infos['Writer'], 'François Descraques, Slimane-Baptiste Berhoun')
    self.assertEqual(episode_infos['lastupdated'], '1389278219')
    self.assertEqual(episode_infos['DirectorList'], ['François Descraques', 'Slimane-Baptiste Berhoun'])
    self.assertEqual(episode_infos['WriterList'], ['François Descraques', 'Slimane-Baptiste Berhoun'])
  
  def test_episode_us(self):
    series_name = 'The Office (US)'
    series = thetvdb_api.set_series(series_name, TVDB_API_KEY, 'en')
    
    series_infos = thetvdb_api.get_series(series)
    self.assertEqual(series_infos['seriesid'], '73244')
    self.assertEqual(series_infos['language'], 'en')
    self.assertEqual(series_infos['SeriesName'], 'The Office (US)')
    self.assertEqual(series_infos['AliasNames'], 'The Office US')
    self.assertEqual(series_infos['Overview'], 'A fresh and funny mockumentary-style glimpse into the daily interactions of the eccentric workers at the Dunder Mifflin paper supply company. This fast-paced comedy parodies contemporary American water-cooler culture.')
    self.assertEqual(series_infos['FirstAired'], '2005-03-24')
    self.assertEqual(series_infos['Network'], 'NBC')
    self.assertEqual(series_infos['IMDB_ID'], 'tt0386676')
    self.assertEqual(series_infos['zap2it_id'], 'SH00726133')
    self.assertEqual(series_infos['banner'], 'http://thetvdb.com/banners/graphical/73244-g9.jpg')
    self.assertEqual(series_infos['SeriesNameList'], ['The Office (US)', 'The Office US'])
    
    episode_infos = thetvdb_api.get_episode(series, 6, 17)
    self.assertEqual(episode_infos['id'], '1832421')
    self.assertEqual(episode_infos['seasonid'], '82981')
    self.assertEqual(episode_infos['EpisodeNumber'], '17')
    self.assertEqual(episode_infos['EpisodeName'], 'The Delivery (1)')
    self.assertEqual(episode_infos['FirstAired'], '2010-03-04')
    self.assertIsNone(episode_infos['GuestStars'])
    self.assertEqual(episode_infos['Director'], 'Seth Gordon')
    self.assertEqual(episode_infos['Writer'], 'Daniel Chun')
    self.assertEqual(episode_infos['filename'], 'http://thetvdb.com/banners/episodes/73244/1832421.jpg')
    
    actors = thetvdb_api.get_actors(series)
    self.assertEqual(actors['23734']['Name'], 'Steve Carell')
    self.assertEqual(actors['23734']['Role'], 'Michael Scott')
    self.assertEqual(actors['23734']['Image'], 'http://thetvdb.com/banners/actors/23734.jpg')
    self.assertEqual(actors['77813']['Name'], 'B.J. Novak')
    self.assertEqual(actors['77813']['SortOrder'], '3')
    
  def test_episode_uk(self):
    series_name = 'The Office (UK)'
    series = thetvdb_api.set_series(series_name, TVDB_API_KEY, 'en')
    
    series_infos = thetvdb_api.get_series(series)
    self.assertEqual(series_infos['seriesid'], '78107')
    self.assertEqual(series_infos['language'], 'en')
    self.assertEqual(series_infos['SeriesName'], 'The Office (UK)')
    self.assertEqual(series_infos['Overview'], 'A mockumentary about life in a mid-sized suboffice paper merchants in a bleak British industrial town, where manager David Brent thinks he\'s the coolest, funniest, and most popular boss ever. He isn\'t. That doesn\'t stop him from embarrassing himself in front of the cameras on a regular basis, whether from his political sermonizing, his stand-up \'comedy\', or his incredibly unique dancing. Meanwhile, long-suffering Tim longs after Dawn the engaged receptionist and keeps himself sane by playing childish practical jokes on his insufferable, army-obsessed deskmate Gareth. Will the Slough office be closed? Will the BBC give David a game show? Will Tim and Dawn end up with each other? And more importantly, will Gareth realize what a hopeless prat he is?')
    self.assertEqual(series_infos['FirstAired'], '2001-07-01')
    self.assertEqual(series_infos['Network'], 'BBC Two')
    self.assertEqual(series_infos['IMDB_ID'], 'tt0290978')
    self.assertEqual(series_infos['banner'], 'http://thetvdb.com/banners/graphical/78107-g10.jpg')
    self.assertEqual(series_infos['SeriesNameList'], ['The Office (UK)'])
    self.assertIsNone(series_infos['Airs_DayOfWeek'])
    
    episode_infos = thetvdb_api.get_episode(series, '1', '2')
    self.assertEqual(episode_infos['id'], '272171')
    self.assertEqual(episode_infos['seasonid'], '14296')
    self.assertEqual(episode_infos['EpisodeNumber'], '2')
    self.assertEqual(episode_infos['EpisodeName'], 'Work Experience')
    self.assertEqual(episode_infos['FirstAired'], '2001-07-16')
    self.assertEqual(episode_infos['Director'], 'Ricky Gervais|Stephen Merchant')
    self.assertEqual(episode_infos['Writer'], 'Ricky Gervais|Stephen Merchant')
    self.assertEqual(episode_infos['DirectorList'], ['Ricky Gervais', 'Stephen Merchant'])
    self.assertEqual(episode_infos['WriterList'], ['Ricky Gervais', 'Stephen Merchant'])
    
  def test_episode_multi_aliases(self):
    series_name = 'Shipwrecked'
    series = thetvdb_api.set_series(series_name, TVDB_API_KEY, 'en')
    
    series_infos = thetvdb_api.get_series(series)
    self.assertIn(series_name, series_infos['SeriesNameList'])
    self.assertIn('Shipwrecked: Battle of the Islands', series_infos['SeriesNameList'])
    self.assertIn('Shipwrecked: The Island', series_infos['SeriesNameList'])
     
  def test_non_existing_series(self):
    series_non_existing_name = 'Fake series'
    self.assertRaises(thetvdb_api.theTVDBError, thetvdb_api.set_series, series_non_existing_name, TVDB_API_KEY)
    
  def test_non_existing_episode(self):
    series_name = 'Parks and Recreation'
    series = thetvdb_api.set_series(series_name, TVDB_API_KEY, 'en')
    
    self.assertRaises(thetvdb_api.theTVDBError, thetvdb_api.get_episode, series, '100', '20', 'en')   
  
def suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.TestLoader().loadTestsFromTestCase(theTVDBTestCase))
  return suite

if __name__ == '__main__':
  suite = unittest.TestLoader().loadTestsFromTestCase(theTVDBTestCase)
  unittest.TextTestRunner(verbosity=2).run(suite)