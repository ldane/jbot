#!/usr/bin/python

import re
import xmlrpc2scgi as xs
import datetime
import sys

def main():
	rtorrent_host="scgi://localhost:5000"
	server=xs.RTorrentXMLRPCClient(rtorrent_host)
	list=server.download_list("main")
	mess="Main list\n"
	for torr in list:
		perc=(100*server.d.get_completed_chunks(torr))/server.d.get_size_chunks(torr);
		mess+=server.d.get_name(torr)+"% "+`perc`+"\n"
	print mess
	
if __name__ == "__main__":
	sys.exit(main())
