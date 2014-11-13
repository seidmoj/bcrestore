#!/usr/bin/python
#
# livetools.py
# Copyright (C) Mola Pahnadayan 2011 <mola.mp@gmail.com>
# 
# simtrack is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# simtrack is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys

import gobject
#import Gtk
from subprocess import call
import bz2
import dbus
import frontend

UI_FILE = "ui_livetools.ui"


#output=`dmesg | grep hda`
## becomes
#p1 = Popen(["dmesg"], stdout=PIPE)
#p2 = Popen(["grep", "hda"], stdin=p1.stdout, stdout=PIPE)
#p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
#output = p2.communicate()[0]

class  GUI():
    def __init__(self):
        self.builder = gtk.Builder()
        self.builder.add_from_file(UI_FILE)
        self.window = self.builder.get_object("window1")
        self.progress = self.builder.get_object("progressbar1")
        self.logview = self.builder.get_object("textbuffer1")        
        
        self.builder.connect_signals(self)

        bus = dbus.SystemBus()
        getlist= False
        try:
            ud_manager_obj = bus.get_object("org.freedesktop.UDisks", "/org/freedesktop/UDisks")
            ud_manager = dbus.Interface(ud_manager_obj, 'org.freedesktop.UDisks')
        except:
            print "Dbus Error"

        self.filepath = ""
        self.restorepath = ""
        self.backuppath = ""
        
        self.devicelist = []
        if (getlist):
            for dev in ud_manager.EnumerateDevices():
                device_obj = bus.get_object("org.freedesktop.UDisks", dev)
                device_props = dbus.Interface(device_obj, dbus.PROPERTIES_IFACE)
                device = {}
                device["file"] = device_props.Get('org.freedesktop.UDisks.Device', "DeviceFile")
                device["interface"] = device_props.Get('org.freedesktop.UDisks.Device', "DriveConnectionInterface")             
                device["removeable"] = device_props.Get('org.freedesktop.UDisks.Device', "DeviceIsRemovable")
                device["drive"] = device_props.Get('org.freedesktop.UDisks.Device', "DeviceIsDrive")
                if device["drive"] == 1:
                    if device["interface"] == "ata":
                        if device["removeable"] == 0 :
                            self.restorepath = device["file"]
                    if device["interface"] == "usb":
                        if device["removeable"] == 1 :
                            self.backuppath = device["file"]
                                    
        self.logview.insert(self.logview.get_end_iter(), "Backup disk  :: "+ self.backuppath + "\n")
        self.logview.insert(self.logview.get_end_iter(), "Restore disk :: "+ self.restorepath+ "\n")

    def openFile(self, title, type):
        dialog = gtk.FileChooserDialog(title,
                                       None,
                                       type,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        
        files = ""
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        dialog.add_filter(filter)
             
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            files = dialog.get_filename()
        elif response == gtk.RESPONSE_CANCEL:
            print 'Closed, no files selected'
        dialog.destroy()
        return files

    def restore(self, obj = None):
        self.logview.insert(self.logview.get_end_iter(), "restore start ...\n")
        
        restorePath = self.openFile("Select image to restore" ,gtk.FILE_CHOOSER_ACTION_OPEN)
        if (restorePath!=""):
            co = bz2.BZ2File (restorePath ,'r')
        else:
            return
        try:
            hdd = open(self.restorepath,'wb')
        except:
            print "Can not open hard drive !"
            return

        state = os.statvfs(self.restorepath)
        diskspace = (state.f_bavail * state.f_frsize) / 1024
        
        progress = 0
        while True :
            reader = co.read(10240)
            if not reader:
                break
            hdd.write(reader)
            progress = progress+10240
            #self.progress.set_value( progress/diskspace )
            print (progress/1024.0)/diskspace
            self.progress.set_fraction( (progress/1024.0)/diskspace )
            
            while gtk.events_pending():
                gtk.main_iteration()
        
        self.progress.set_fraction( 1.0 )

        hdd.close()
        co.close()
        
        self.logview.insert(self.logview.get_end_iter(), "restore down.\n")
        
    def backup(self, obj = None):
        self.logview.insert(self.logview.get_end_iter(), "Backup start .\n")

        backupPath = self.openFile("Save image as ...", gtk.FILE_CHOOSER_ACTION_SAVE)
        if (backupPath!=""):
            co = bz2.BZ2File (backupPath,'w')
        else:
            return        
        
        try:
            hdd = open(self.restorepath,'rb')
        except:
            print "Can not open hard drive !"
            return

        state = os.statvfs(self.restorepath)
        diskspace = (state.f_bavail * state.f_frsize) / 1024
        
        progress = 0
        while True :
            reader = hdd.read(10240)
            if not reader:
                break
            co.write(reader)
            progress = progress+10240
            #self.progress.set_value( progress/diskspace )
            print (progress/1024.0)/diskspace
            self.progress.set_fraction( (progress/1024.0)/diskspace )
            
            while gtk.events_pending():
                gtk.main_iteration()
        
        self.progress.set_fraction( 1.0 )

        hdd.close()
        co.close()
        self.logview.insert(self.logview.get_end_iter(), "Backup down .\n")
        
    def shutdown(self,obj):
        call(["poweroff"])
    
    def restart(self,obj):
        call(["halt", "--reboot"])

    def quit(self, widget, *event):
    
        gtk.main_quit()    
    
def main():
    app = GUI()
    app.window.show()
    gtk.main()

if __name__ == "__main__":
    rontend = None
    if 'DISPLAY' not in os.environ:
        rontend = frontend.Frontend()
        rontend.set_lang()
        rontend.startx()
        rontend.init_gtk()
        rontend.start_wm()
        rontend.merge_xres()
    try:
        import gtk
    except ImportError:
        sys.exit("pygtk not found.")
                    
    sys.exit(main())
    