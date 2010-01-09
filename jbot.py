#!/usr/bin/python
"""
    Jabber bot for rtorrent
"""
import jabberbot
from time import time
import datetime
import xmlrpc2scgi as xs
import os
import subprocess
import glob
import stat
import shutil
import sys

BOTCMD = jabberbot.botcmd

class Juicer(jabberbot.JabberBot):
    """Main Class"""
    def __init__(self, jid, password, res=None):
        super( Juicer, self).__init__( jid, password, res, True)

        # scgi host and port
        self.rtorrent_host = "scgi://localhost:5000"
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
        self.server = xs.RTorrentXMLRPCClient(self.rtorrent_host)

    @BOTCMD
    def serverinfo(self , mess, args):
        """Displays information about the server"""
        version = open('/proc/version').read().strip()
        loadavg = open('/proc/loadavg').read().strip()
        return '%s\n\n%s' % ( version, loadavg, )

    @BOTCMD
    def time(self, mess, args):
        """Displays current server time"""
        return str(datetime.datetime.now())

    @BOTCMD
    def getup(self, mess, args):
        """Get upload rate"""
        return self.server.get_upload_rate()

    @BOTCMD
    def setup(self, mess, args):
        """Set upload rate"""
        self.server.set_upload_rate(args+"K")
        return self.server.get_upload_rate()

    @BOTCMD
    def getdown(self, mess, args):
        """Get download rate"""
        return self.server.get_download_rate()

    @BOTCMD
    def setdown(self, mess, args):
        """Set download rate"""
        self.server.set_download_rate(args+"K")
        return self.server.get_download_rate()

    @BOTCMD
    def torrentinfo(self, mess, args):
        """Return rtorrent information"""
        mess = "[Down: %s | Up: %s" % (
                self.server.get_down_rate()/1024,
                self.server.get_up_rate()/1024
                )
        return mess 
    
    @BOTCMD
    def list(self, mess, args):
        """Return torrent list"""
        torr_list = self.server.download_list("main")
        mess = "Main list\n"
        cnt = 1
        for torr in torr_list:
            (comp, full) = self.get_compl_rate(torr) 
            perc = (100 * comp) / full
            mess += "%d: %s %%%d \n" % (cnt, self.server.d.get_name(torr), perc)
            cnt += 1
        return mess

    @BOTCMD
    def remove(self, mess, args):
        """Erase Torrent"""
        torr_list = self.server.download_list("main")
        cnt = 1
        target = int(args)
        mess = "Not Found"
        for torr in torr_list:
            if cnt == target:
                mess = self.server.d.get_name(torr)
                if self.server.d.erase(torr) == 0:
                    mess += " deleted."
                else:
                    mess += " can't deleted."
            cnt += 1
        return mess

    @BOTCMD
    def rm_comp(self, mess, args):
        """Remove Completed"""
        torr_list = self.server.download_list("main")
        cnt = 0
        for torr in torr_list:
            (comp, full) = self.get_compl_rate(torr)
            if comp == full:
                if self.server.d.erase(torr) == 0:
                    cnt += 1
        return "%d torrent removed." % (cnt)

    @BOTCMD
    def stopall(self, mess, args):
        """Stop all started torrents"""
        torr_list = self.server.download_list("main")
        for torr in torr_list:
            self.server.d.stop(torr)
        return "Stopped"

    @BOTCMD
    def startall(self, mess, args):
        """Stop all started torrents"""
        torr_list = self.server.download_list("main")
        for torr in torr_list:
            self.server.d.start(torr)
        return "Started"

    @BOTCMD
    def getlink(self, mess, args):
        """download link"""
        url_start = time()
        subprocess.call(["wget", "-P", self.queue, args])
        url_end = time()
        return "Downloaded %s" % (url_end - url_start)

    @BOTCMD
    def lsque(self, mess, args):
        """list queue"""
        cnt = 0
        mess = ""
        for root, dirs, files in os.walk(self.queue):
            for name in files:
                filename = os.path.join(root, name)
                cnt += 1
                mess += "%d: %s\n" % (cnt, filename)
        if cnt == 0:
            return "Not found any torrent in queue directory."
        return mess

    @BOTCMD
    def force_move(self, mess, args):
        """force move forrent from queue"""
        self.last_command = 0
        return "Resetted last command time."

    def idle_proc(self):
        """queueing stuffs"""
        if  time() - self.last_command > self.recheck_time :
            self.update_time()
            if self.reached_max_count() or self.reached_max_down() :
                download = []
                for torr_file in glob.glob(self.queue + '/*.torrent'):
                    download.append((os.stat(torr_file)[stat.ST_MTIME], file))
                if len(download) > 0:
                    download.sort()
                path = self.watch + '/' + str(download[0][1]).split('/')[-1]
                if os.path.exists(path):
                    os.remove(download[0][1])
                else:
                    shutil.move(download[0][1], self.watch)
    
    def get_compl_rate(self, torr):
        """Returning complate rate of given torrent"""
        compl = self.server.d.get_completed_chunks(torr)
        torr = self.server.d.get_size_chunks(torr)
        return (compl, torr)
    
    def reached_max_down(self):
        """Are we reached or passed our torrent rate?"""
        if self.server.get_down_rate() > self.max_download_rate:
            return True
        return False
    
    def reached_max_count(self):
        """Are we reached or passed our torrent count?"""
        infohashes = self.server.download_list('incomplete')
        if len(infohashes) > self.max_downloads :
            return True
        return False

    def update_time(self):
        """Update last command time with now """
        self.last_command = time()

def main():
    """main"""
    bot = Juicer("wadsox@koli.be", "signomix", "WD MyBook World Edition")
    bot.serve_forever()

if __name__ == "__main__":
    sys.exit(main())
