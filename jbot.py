#!/usr/bin/python

from jabberbot import JabberBot
from time import time
from random import random
import base64
import datetime
import re
import xmlrpc2scgi as xs
import urllib
import os
import glob
import stat
import shutil
import sys

class Juicer(JabberBot):

	# scgi host and port
	rtorrent_host="scgi://localhost:5000"
	# watch and queue folders
	watch = "/shares/torrent/watch"
	queue = "/shares/torrent/queue"
	# total number of downloads allowed
	max_downloads = 2
	# download rate in kbp/s
	max_download_rate = 50000
	# how often to recheck to add more (in seconds)
	recheck_time = 600

	last_command = 0;

	def bot_serverinfo( self, mess, args):
		"""Displays information about the server"""
		version = open('/proc/version').read().strip()
		loadavg = open('/proc/loadavg').read().strip()
		return '%s\n\n%s' % ( version, loadavg, )

	def bot_time( self, mess, args):
		"""Displays current server time"""
		return str(datetime.datetime.now())
	
	def bot_rot13( self, mess, args):
		"""Returns passed arguments rot13'ed"""
		return args.encode('rot13')
	
	def bot_whoami( self, mess, args):
		"""Tells you your username"""
		return mess.getFrom()
	
	def bot_hello( self, mess, args):
		"""Hello World"""
		return 'Hello World!'

	def bot_getup( self, mess, args):
		"""Get upload rate"""
		return self.server.get_upload_rate()
	
	def bot_setup( self, mess, args):
		"""Set upload rate"""
		self.server.set_upload_rate(args+"K")
		return self.server.get_upload_rate()

	def bot_getdown( self, mess, args):
		"""Get download rate"""
		return self.server.get_download_rate()

	def bot_setdown( self, mess, args):
		"""Set download rate"""
		self.server.set_download_rate(args+"K")
		return self.server.get_download_rate()

	def bot_torrentinfo( self, mess, args):
		"""Return rtorrent information"""
		return "[Down:"+`self.server.get_down_rate()/1024`+"|Up:"+`self.server.get_up_rate()/1024`+"]"

	def bot_list( self, mess, args):
		"""Return torrent list"""
		list=self.server.download_list("main")
		mess="Main list\n"
		for torr in list:
			perc=(100*self.server.d.get_completed_chunks(torr))/self.server.d.get_size_chunks(torr);
			mess+=self.server.d.get_name(torr)+"% "+`perc`+"\n"
		return mess

	def bot_stopall( self, mess, args):
		"""Stop all started torrents"""
		list=self.server.download_list("main")
		for torr in list:
			self.server.d.stop(torr)
		return "Stopped"

	def bot_startall( self, mess, args):
		"""Stop all started torrents"""
		list=self.server.download_list("main")
		for torr in list:
			self.server.d.start(torr)
		return "Started"

	def bot_getlink( self, mess, args):
		"""download link"""
		url_start = time()
		urllib.urlretrieve(args,"/shares/torrent/queue/"+base64.b64encode("limon"+str(random()))+".torrent")
		url_end = time()
		return "Downloaded %s" % (url_end - url_start)

	def bot_lsque( self, mess, args):
		"""list queue"""
		cnt=0
		mess=""
		for root, dirs, files in os.walk('/shares/torrent/queue'):
			for name in files:
				filename = os.path.join(root, name)
				cnt+=1
				mess+="%d: %s\n" %(cnt,name)
		if cnt==0:
			return "Not found any torrent in queue directory."
		return mess
	
	def bot_quit( self, mess, args):
		"""quit bot"""
		sys.exit(0)

	def idle_proc(self):
		if ( time() - self.last_command > self.recheck_time ):
			self.last_command = time()
			infohashes = server.download_list('incomplete')
			if (len(infohashes) < self.max_downloads) or (rtc.get_down_rate() < self.max_download_rate):
				download = []
				for file in glob.glob(queue + '/*.torrent'):
					download.append((os.stat(file)[stat.ST_MTIME], file))
				if len(download) > 0:
					download.sort()
					if os.path.exists(self.watch + '/' + str(download[0][1]).split('/')[-1]):
						self.send("leventdane@gmail.com","%s already exists, deleting from queue folder" % (download[0][1]))
						os.remove(download[0][1])
					else:
						self.send("leventdane@gmail.com","%s -> %s" % (download[0][1], self.watch))
						shutil.move(download[0][1], self.watch)
		pass

def main():
	bot = Juicer("wadsox@jabber.org", "signomix")	
	bot.last_command = time()
	bot.server=xs.RTorrentXMLRPCClient(bot.rtorrent_host)
	bot.serve_forever()

if __name__ == "__main__":
	sys.exit(main())
