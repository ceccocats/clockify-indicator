#!/usr/bin/env python3
import signal
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3, GObject
import time
from threading import Thread
from clockify import Clockify
import copy
import os

class Indicator():
    def __init__(self):
        self.baseTitle = "Clockify"

        self.cfy = Clockify()

        self.app = 'clockify'
        iconpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "clockify_icon.svg")
        self.indicator = AppIndicator3.Indicator.new(
            self.app, iconpath,
            AppIndicator3.IndicatorCategory.OTHER)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)       
        self.indicator.set_menu(self.create_menu())
        self.indicator.set_label(self.baseTitle, self.app)
        # the thread:
        self.update = Thread(target=self.update)
        # daemonize the thread to make the indicator stopable
        self.update.setDaemon(True)
        self.update.start()

    def create_menu(self):
        menu = Gtk.Menu()

        self.item_quit = Gtk.MenuItem('Quit')
        self.item_quit.connect('activate', self.stop)
        menu.append(self.item_quit)
        menu.show_all()
        return menu

    def update(self):
        self.cfy.connect() 
        all_entries = self.cfy.getAllEntries()

        menu = self.indicator.get_menu()

        menu.remove(self.item_quit)
        item_stop = Gtk.MenuItem('Stop')
        item_stop.connect('activate', self.stopEntry)
        menu.append(item_stop)

        last_projects = []
        for i in all_entries:
            pId = i["projectId"]
            if i["projectId"] is not None and pId not in last_projects:
                last_projects.append(pId)
        for i in range(min(4,len(last_projects))):
            pId = last_projects[i]
            item_prj = Gtk.MenuItem(self.cfy.projects[pId])
            item_prj.connect('activate', lambda source, pId=pId: self.startEntry(source, pId))
            menu.append(item_prj)

        menu_sep = Gtk.SeparatorMenuItem()
        menu.append(menu_sep)

        self.item_quit = Gtk.MenuItem('Quit')
        self.item_quit.connect('activate', self.stop)
        menu.append(self.item_quit)
        menu.show_all()

        while True:
            entries = self.cfy.getActiveEntries()
            # print(entries)

            mention = self.baseTitle
            if len(entries) > 0:
                e = entries[0]
                duration = Clockify.now() - Clockify.ISO2datetime(e["timeInterval"]["start"])
                pId = ""
                try:
                    pId = self.cfy.projects[e["projectId"]]
                except:
                    pass
                mention = "{} {}".format(pId, duration)
            else:
                mention = "Not working"

            if(len(entries) > 1):
                mention += " [...]"

            # apply the interface update using  GObject.idle_add()
            GObject.idle_add(
                self.indicator.set_label,
                mention, self.app,
                priority=GObject.PRIORITY_DEFAULT
                )

            time.sleep(2)

    def stopEntry(self, source):
        self.cfy.stopActiveEntry()

    def startEntry(self, source, id):
        self.cfy.startEntry(id)

    def stop(self, source):
        Gtk.main_quit()

Indicator()
# this is where we call GObject.threads_init()
GObject.threads_init()
signal.signal(signal.SIGINT, signal.SIG_DFL)
Gtk.main()