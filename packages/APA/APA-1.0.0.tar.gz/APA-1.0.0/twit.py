#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tweepy
import datetime
import MySQLdb as mdb
import location as loc
from threading import Thread, BoundedSemaphore
import urllib
from xml.dom import minidom

################# TWITTER AUTHENTIFICATION KEYS #################
CONSUMER_KEY = 'g5xQx67GQgzJCs4aNam1Q'
CONSUMER_SECRET = '4T5y74q6MATeiA13pktZJiyvSSCAu4cjLUesnJLg'
ACCESS_TOKEN = '1440443094-X7g4mB05cCU5KT5gaaHkj3sqaWkbcJRDHbs0tKZ'
ACCESS_SECRET = 'LBAIA50pmrahav4grydp7r2ylvRgy2Pa5y6xgNK0zrdzC'
############ DO NOT REVEAL ABOVE KEYS TO OTHER PERSON ###########

########## Setting OAuth Handler ##########
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

########## ETC global variables ###########
today = datetime.date.today()
con = mdb.connect('localhost', 'root', 'dhepd','test')
sema = BoundedSemaphore(value=1)

class finder(Thread):
	def __init__(self, keyword):
		Thread.__init__(self)
		self.keyword = keyword
		
	def run(self):
		sema.acquire()
		########## START CRITICAL SECTION ##########
		for tweet in tweepy.Cursor(api.search, q=self.keyword, rpp=100, lang='ko').items():
			with con:
				if (tweet.created_at.day+2 < today.day):
					break
				else:
					cur = con.cursor()
					tid = tweet.user.id

					tname = tweet.user.name.encode('utf-8')
					text = tweet.text.encode('utf-8')
					location = self.GetLocation(text)					
					tp = ''
					if (self.keyword=='교통사고 poltra -RT'):
						tp = '교통사고'
					if (self.keyword=='화재 발생 -RT'):
						tp = '화재'
					if (location!=False):
						geo = self.GetGeo(location)
						lat = geo[0]
						lng = geo[1]
						cur.execute("INSERT INTO test VALUES(%s, %s, %s, %s, %s, %s, %s, %s)", (tid, tname, location, lat, lng, tp, text, tweet.created_at))
		########## END CRITICAL SECTION ###########
		sema.release()
		
	def GetLocation(self, text):
		for i in range(0, 25):
			for j in range (0, len(loc.gu[i])):
				if (text.count(loc.gu[i][j])>=1):
					return loc.gu[i][j]
		return False
	
	def GetGeo(self, location):
		url = 'http://apis.daum.net/local/geo/addr2coord?apikey=6acc30183ab818fa90193ab6154616892a68508f&q='+location+'&output=xml'
		dom = minidom.parse(urllib.urlopen(url))
		items = dom.getElementsByTagName("item")
		lat = items[0].getElementsByTagName("lat")
		lng = items[0].getElementsByTagName('lng')
		return (lat[0].firstChild.data,lng[0].firstChild.data)
		 
							
find = finder('교통사고 poltra -RT')
find2 = finder('화재 발생 -RT')
find.start()
find2.start()
