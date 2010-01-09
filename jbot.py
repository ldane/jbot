#!/usr/bin/python

import jabberbot
from time import time
from random import random
import base64
import datetime
import re
import xmlrpc2scgi as xs
import urllib
import os
import subprocess
import glob
import stat
import shutil
import sys

botcmd = jabberbot.botcmd

class Juicer(jabberbot.JabberBot):
    def __init__( self, jid, password, res=None):
        super( Juicer, self).__init__(jid,password,res,True)

        # scgi host and port
        self.rtorrent_host="scgi://localhost:5000"
        # watch and queue folders
        self.watch = "/shares/torrent/.rtorrent/watch"
        self.queue = "/shares/torrent/Watch"
        # total number of downloads allowed
        self.max_downloads = 1
        # download rate in kbp/s
        self.max_download_rate = 50000
        # how often to recheck to add more (in seconds)
        self.recheck_time = 600
        self.last_command = time()
        # connect XMLRPC
        self.server=xs.RTorrentXMLRPCClient(self.rtorrent_host)

    @botcmd
    def serverinfo( self, mess, args):
        """Displays information about the server"""
        version = open('/proc/version').read().strip()
        loadavg = open('/proc/loadavg').read().strip()
        return '%s\n\n%s' % ( version, loadavg, )

    @botcmd
    def time( self, mess, args):
        """Displays current server time"""
        return str(datetime.datetime.now())

    @botcmd
    def getup( self, mess, args):
        """Get upload rate"""
        return self.server.get_upload_rate()

    @botcmd
    def setup( self, mess, args):
        """Set upload rate"""
        self.server.set_upload_rate(args+"K")
        return self.server.get_upload_rate()

    @botcmd
    def getdown( self, mess, args):
        """Get download rate"""
        return self.server.get_download_rate()

    @botcmd
    def setdown( self, mess, args):
        """Set download rate"""
        self.server.set_download_rate(args+"K")
        return self.server.get_download_rate()

    @botcmd
    def torrentinfo( self, mess, args):
        """Return rtorrent information"""
        return "[Down:"+`self.server.get_down_rate()/1024`+"|Up:"+`self.server.get_up_rate()/1024`+"]"

    @botcmd
    def list( self, mess, args):
        """Return torrent list"""
        list=self.server.download_list("main")
        mess="Main list\n"
        cnt=1
        for torr in list:
            perc=(100*self.server.d.get_completed_chunks(torr))/self.server.d.get_size_chunks(torr)
            mess+=`cnt`+": "+self.server.d.get_name(torr)+" %"+`perc`+"\n"
            cnt+=1
        return mess

    @botcmd
    def rm( self, mess, args):
        """Erase Torrent"""
        list=self.server.download_list("main")
        cnt=1
        target = int(args)
        mess="Not Found"
        for torr in list:
            if(cnt == target):
                mess = self.server.d.get_name(torr)
                if( self.server.d.erase(torr) == 0 ):
                    mess += " deleted."
                else:
                    mess += " can't deleted."
            cnt+=1
        return mess

    @botcmd
    def rm_comp( self, mess, args):
        """Remove Completed"""
        list=self.server.download_list("main")
        cnt=0
        for torr in list:
            if( self.server.d.get_completed_chunks(torr)==self.server.d.get_size_chunks(torr) ):
                #mess = self.server.d.get_name(torr)
                if( self.server.d.erase(torr) == 0 ):
                    #mess += " deleted."
                    cnt+=1
        return "%d torrent removed." %(cnt)

    @botcmd
    def stopall( self, mess, args):
        """Stop all started torrents"""
        list=self.server.download_list("main")
        for torr in list:
            self.server.d.stop(torr)
        return "Stopped"

    @botcmd
    def startall( self, mess, args):
        """Stop all started torrents"""
        list=self.server.download_list("main")
        for torr in list:
            self.server.d.start(torr)
        return "Started"

    @botcmd
    def getlink( self, mess, args):
        """download link"""
        url_start = time()
        subprocess.call(["wget", "-P", self.queue, args])
        url_end = time()
        return "Downloaded %s" % (url_end - url_start)

    @botcmd
    def lsque( self, mess, args):
        """list queue"""
        cnt=0
        mess=""
        for root, dirs, files in os.walk(self.queue):
            for name in files:
                filename = os.path.join(root, name)
                        cnt+=1
                        mess+="%d: %s\n" %(cnt,name)
        if cnt==0:
            return "Not found any torrent in queue directory."
        return mess

    @botcmd
    def quit( self, mess, args):
        """quit bot"""
        sys.exit(0)

    @botcmd
    def force_move( self, mess, args):
        """force move forrent from queue"""
        self.last_command = 0
        return "Resetted last command time."

    def idle_proc(self):
        if ( time() - self.last_command > self.recheck_time ):
            self.last_command = time()
            infohashes = self.server.download_list('incomplete')
            if (len(infohashes) < self.max_downloads) or (self.server.get_down_rate() < self.max_download_rate) :
                download = []
                for file in glob.glob(self.queue + '/*.torrent'):
                    download.append((os.stat(file)[stat.ST_MTIME], file))
                if len(download) > 0:
                    download.sort()
                if os.path.exists(self.watch + '/' + str(download[0][1]).split('/')[-1]):
                    #self.send("limon@koli.be","%s already exists, deleting from queue folder" % (download[0][1]))
                    os.remove(download[0][1])
                else:
                    #self.send("limon@koli.be","%s -> %s" % (download[0][1], self.watch))
                    shutil.move(download[0][1], self.watch)
        pass


def main():
    bot = Juicer("wadsox@koli.be", "signomix", "WD MyBook World Edition")
    bot.serve_forever()

if __name__ == "__main__":
    sys.exit(main())
