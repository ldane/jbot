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

class Juicer(JabberBot):
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
		return server.get_upload_rate()
	
	def bot_setup( self, mess, args):
		"""Set upload rate"""
		server.set_upload_rate(args+"K")
		return server.get_upload_rate()

	def bot_getdown( self, mess, args):
		"""Get download rate"""
		return server.get_download_rate()

	def bot_setdown( self, mess, args):
		"""Set download rate"""
		server.set_download_rate(args+"K")
		return server.get_download_rate()

	def bot_torrentinfo( self, mess, args):
		"""Return rtorrent information"""
		return "[Down:"+`server.get_down_rate()/1024`+"|Up:"+`server.get_up_rate()/1024`+"]"

	def bot_list( self, mess, args):
		"""Return torrent list"""
		list=server.download_list("main")
		mess="Main list\n"
		for torr in list:
			perc=(100*server.d.get_completed_chunks(torr))/server.d.get_size_chunks(torr);
			mess+=server.d.get_name(torr)+"% "+`perc`+"\n"
		return mess

	def bot_stopall( self, mess, args):
		"""Stop all started torrents"""
		list=server.download_list("main")
		for torr in list:
			server.d.stop(torr)
		return "Stopped"

	def bot_startall( self, mess, args):
		"""Stop all started torrents"""
		list=server.download_list("main")
		for torr in list:
			server.d.start(torr)
		return "Started"

	def bot_getlink( self, mess, args):
		"""download link"""
		url_start = time()
		urllib.urlretrieve(args,"/shares/torrent/queue/"+base64.b64encode("limon"+str(random()))+".torrent")
		url_end = time()
		return "Downloaded %s" % (url_end - url_start)
	def idle_proc(self):
		global last_command,recheck_time
		if ( time() - last_command > recheck_time ):
			last_command = time()
			infohashes = server.download_list('incomplete')
			if (len(infohashes) < max_downloads):
				download = []
				for file in glob.glob(queue + '/*.torrent'):
					download.append((os.stat(file)[stat.ST_MTIME], file))
				if len(download) > 0:
					download.sort()
					if os.path.exists(watch + '/' + str(download[0][1]).split('/')[-1]):
						self.send("leventdane@gmail.com","%s already exists, deleting from queue folder" % (download[0][1]))
						os.remove(download[0][1])
					else:
						self.send("leventdane@gmail.com","%s -> %s" % (download[0][1], watch))
						shutil.move(download[0][1], watch)
		pass

# scgi host and port
rtorrent_host="scgi://localhost:5000"
# watch and queue folders
watch = "/shares/torrent/watch"
queue = "/shares/torrent/queue"
# total number of downloads allowed
max_downloads = 2
# download rate in kbp/s
#max_download_rate = 50000
# how often to recheck to add more (in seconds)
recheck_time = 60


username = 'wadsox@jabber.org'
password = 'signomix'
last_command = time();
server=xs.RTorrentXMLRPCClient(rtorrent_host)

bot = Juicer(username,password)
bot.serve_forever()
