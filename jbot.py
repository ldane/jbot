#!/usr/bin/python

from jabberbot import JabberBot
import datetime
import re
import xmlrpclib

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
		return server.get_upload_rate();
	
	def bot_setup( self, mess, args):
		"""Set upload rate"""
		server.set_upload_rate(args+"K");
		return server.get_upload_rate();

	def bot_getdown( self, mess, args):
		"""Get download rate"""
		return server.get_download_rate();

	def bot_setdown( self, mess, args):
		"""Set download rate"""
		server.set_downloa_rate(args+"K");
		return server.get_download_rate();

username = 'wadsox@jabber.org'
password = 'signomix'

server=xmlrpclib.Server("http://jrtorrent:boxoftorr@localhost/RPC2")

bot = Juicer(username,password)
bot.serve_forever()
