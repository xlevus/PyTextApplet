#!/usr/bin/env python

from datetime import datetime, timedelta

class TextGetter(object):
    def __init__(self, force_update, text):
        self.timeout_val = 1000
        self.force_update = force_update
        self.text = text

    def text(self):
        """
        Can return pango-markup text
        http://library.gnome.org/devel/pango/stable/PangoMarkupFormat.html
        """
        return self.text
        return "<span size='smaller'>The time is:\n%s</span>" % datetime.now()

    def timeout(self):
        """
        The time in milliseconds until the next call to text() and icon().
        """
        return self.timeout_val

    def icon(self):
        """
        Returns the path to an icon or None if not needed.
        """
        return "/home/xin/Projects/PyTextApplet/icon.png"

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
import gconf
import gobject
import gnomeapplet

logging.basicConfig(level=logging.DEBUG)

class DialogWrapper(object):
    def __init__(self, glade_file, dialog_name):
        self.dialog_name = dialog_name
        self.wT = gtk.glade.XML(glade_file)
        self.dialog = self.wT.get_widget(dialog_name)
        self.wT.signal_autoconnect(self)

    def __getattr__(self, name):
        """ DEBUG """
        print "GETATTR: %s" % name
        def func(self, *args, **kwargs):
            logging.debug("Dialog %s called %s with args %s %s" % (self.dialog_name, name, args, kwargs))
        return func
    
    def show(self):
        self.dialog.show()
    
    def destroy(self, *args, **kwargs):
        self.dialog.destroy()

class Config(object):
    def __init__(self, applet):
        self.applet = applet

        self.applet.add_preferences('/schemas/apps/pytextapplet/prefs/')
        print 'Pref key: ', self.applet.get_preferences_key()

class PyTextApplet(object):
    def __init__(self, applet, iid):
        gnome.init('sample', '1.0')
        self.applet = applet
        applet.connect("destroy", self.cleanup)

        self.config = Config(self.applet)

        self.build_applet(applet)
        self.build_menu(applet)
        
        self.tg = TextGetter(self.force_update, self.applet.get_preferences_key())

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
            ('Preferences', self.show_preferences),
            ('About', self.show_about),
        ]
        applet.setup_menu(xml, verbs, None)

    def show_about(self, *args):
        about = DialogWrapper("PyTextApplet.glade", "aboutDialog")
        about.show()

    def show_preferences(self, *args):
        prefs = DialogWrapper("PyTextApplet.glade", "preferencesDialog")
        prefs.show()

    def update(self, forced=False):
        self.label.set_label(self.tg.text())

        icon = self.tg.icon()
        if icon:
            self.icon.set_from_file(icon)
            self.icon.set_pixel_size(gnomeapplet.SIZE_X_SMALL)

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

def PyTextAppletFactory(applet, iid):
    tp = PyTextApplet(applet, iid)
    applet.set_background_widget(applet)
    return gtk.TRUE

if len(sys.argv) > 1 and sys.argv[1] == 'run-in-window':
    main_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    main_window.set_title("Text Applet")
    main_window.connect("destroy", gtk.main_quit) 
    app = gnomeapplet.Applet()
    PyTextAppletFactory(app, None)
    app.reparent(main_window)
    main_window.show_all()
    gtk.main()

if __name__ == '__main__':
    gnomeapplet.bonobo_factory(
            "OAFIID:GNOME_PyTextApplet_Factory",
            gnomeapplet.Applet.__gtype__, 
            "PyTextApplet", "0", PyTextAppletFactory
    )

