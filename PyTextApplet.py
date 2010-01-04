#!/usr/bin/env python

from datetime import datetime, timedelta

class TextGetter(object):
    def __init__(self, force_update):
        self.timeout_val = 1000
        self.force_update = force_update

    def text(self):
        """
        Can return pango-markup text
        http://library.gnome.org/devel/pango/stable/PangoMarkupFormat.html
        """
        return "<span size='smaller'>The time is:\n%s</span>" % datetime.now()

    def timeout(self):
        return self.timeout_val

    def icon(self):
        return "/home/xin/Dropbox/Projects/TextPanel/icon.png"

    def on_click(self):
        logging.debug("Forcing update")
        self.timeout_val = self.timeout_val/2
        self.force_update()

import sys
import logging

import pygtk
pygtk.require('2.0')

import gtk
import gtk.glade

import gnome
import gobject
import gnomeapplet

logging.basicConfig(level=logging.DEBUG)

class TextPanel(object):
    def __init__(self, applet, iid):
        gnome.init('sample', '1.0')
        self.applet = applet
        applet.connect("destroy", self.cleanup)

        self.build_applet(applet)
        self.build_menu(applet)
        
        self.tg = TextGetter(self.force_update)

        self.applet.connect("button-press-event", self.on_click)

        self.timeout = None
        self.update()
    
        applet.show_all()

    def build_applet(self, applet):
        self.label = gtk.Label("")
        self.label.set_use_markup(True)

        self.icon = gtk.Image()
        
        self.hbox = gtk.HBox(False, 2)
        self.hbox.add(self.icon)
        self.hbox.add(self.label)

        applet.add(self.hbox)
        applet.resize_children()
        print 'bg', applet.get_background()
        #applet.add(self.label)


    def build_menu(self, applet):
        xml = """
            <popup name="button3">
                <menuitem name="ItemPreferences" 
                          verb="Preferences"
                          label="_Preferences"
                          pixtype="stock"
                          pixname="gtk-preferences" />
                <separator/>
                <menuitem name="ItemAbout"
                          verb="About"
                          label="_About"
                          pixtype="stock"
                          pixname="gtk-about" />
            </popup>
        """
        verbs = [
            ('About', self.show_about),
        ]
        applet.setup_menu(xml, verbs, None)

    def show_about(self, *args):
        wT = gtk.glade.XML("TextPanel.glade")
        dialog = wT.get_widget("aboutDialog")
        dialog.show()
        wT.signal_autoconnect(self)

    def update(self, forced=False):
        self.label.set_label(self.tg.text())

        icon = self.tg.icon()
        if icon:
            self.icon.set_from_file(icon)

        new_timeout = self.tg.timeout()
        if not forced and self.timeout != new_timeout:
            logging.debug("Timeout changed to %s" % new_timeout)
            self.timeout = new_timeout
            gobject.timeout_add(self.timeout, self.update)
            return False
        else:
            return True

    def force_update(self):
        return self.update(forced=True)

    def on_click(self, widget, event):
        if event.button == 1:
            self.tg.on_click()
        else:
            logging.debug("Button press %s" % event.button)
            print self.label.get_attributes()

    def cleanup(self):
        del self.applet

def TextPanelFactory(applet, iid):
    tp = TextPanel(applet, iid)
    applet.set_background_widget(applet)
    return gtk.TRUE

if len(sys.argv) > 1 and sys.argv[1] == 'run-in-window':
    main_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    main_window.set_title("Text Applet")
    main_window.connect("destroy", gtk.mainquit) 
    app = gnomeapplet.Applet()
    TextPanelFactory(app, None)
    app.reparent(main_window)
    main_window.show_all()
    gtk.main()

if __name__ == '__main__':
    gnomeapplet.bonobo_factory(
            "OAFIID:GNOME_PyTextPanel_Factory",
            gnomeapplet.Applet.__gtype__, 
            "PyTextPanel", "0", TextPanelFactory
    )

