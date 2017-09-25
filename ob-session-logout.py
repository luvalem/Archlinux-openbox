#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <daevid.preis@gmail.com> wrote this file. As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return Daevid Preis
# ----------------------------------------------------------------------------
import argparse
import configparser
import os
import subprocess
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


class MainWindow:
    def __init__(self, config_file):
        self.config = Config(config_file)
        self.window = Gtk.Window()
        self.grid = Gtk.Grid()
        self.logo = Gtk.Image()

        self.window.connect("destroy", lambda q: Gtk.main_quit())
        self.window.connect('key-press-event', self.window_onkeypress)
        self.window.set_name("ob-session-logout")
        self.window.set_decorated(0)
        self.window.set_skip_pager_hint(0)
        self.window.set_skip_taskbar_hint(1)
        self.window.set_urgency_hint(1)
        self.window.set_accept_focus(1)
        self.window.set_type_hint(1)
        self.window.set_keep_above(1)
        self.window.stick()
        self.window.set_focus()
        self.window.add(self.grid)

        self.grid.set_halign(Gtk.Align.CENTER)
        self.grid.set_valign(Gtk.Align.START)
        self.grid.set_row_spacing(10)
        self.grid.set_margin_left(20)
        self.grid.set_margin_right(20)
        self.grid.set_margin_top(20)
        self.grid.set_margin_bottom(40)

        if os.path.isfile(self.config.banner):
            self.logo.set_from_file(self.config.banner)
            self.logo.set_margin_bottom(20)
            self.logo.set_valign(Gtk.Align.CENTER)
            self.logo.set_halign(Gtk.Align.FILL)
            self.grid.attach(self.logo, 0, 0, 3, 1)
        else:
            self.grid.set_margin_top(20)

        self.btnLogout = Gtk.Button.new_with_mnemonic(label="_Logout")
        self.btnLogout.connect("clicked", lambda x: self.call_logout())
        self.btnLogout.set_size_request(200, 30)
        self.btnLogout.set_can_focus(True)
        self.grid.attach(self.btnLogout, 1, 1, 1, 1)

        self.btnSuspend = Gtk.Button.new_with_mnemonic(label="_Suspend")
        self.btnSuspend.connect("clicked", lambda x: self.call_suspend())
        self.btnSuspend.set_size_request(200, 30)
        self.grid.attach(self.btnSuspend, 1, 2, 1, 1)

        self.btnRestart = Gtk.Button.new_with_mnemonic(label="_Redemarrer")
        self.btnRestart.connect("clicked", lambda x: self.call_restart())
        self.btnRestart.set_size_request(200, 30)
        self.grid.attach(self.btnRestart, 1, 3, 1, 1)

        self.btnShutdown = Gtk.Button.new_with_mnemonic(label="Arreter")
        self.btnShutdown.connect("clicked", lambda x: self.call_shutdown())
        self.btnShutdown.set_size_request(200, 30)
        self.grid.attach(self.btnShutdown, 1, 4, 1, 1)

        self.btnCancel = Gtk.Button.new_with_mnemonic(label="_Annuler")
        self.btnCancel.connect("clicked", lambda x: self.window.close())
        self.btnCancel.set_size_request(200, 30)
        self.grid.attach(self.btnCancel, 1, 5, 1, 1)

        self.grid.set_column_homogeneous(False)
        self.grid.set_row_homogeneous(False)

    def show(self):
        self.window.show_all()
        self.btnLogout.grab_focus()

    def close(self):
        self.window.close()

    @staticmethod
    def window_onkeypress(widget, event):
        if event.keyval == Gdk.KEY_Escape:
            widget.close()

    @staticmethod
    def call_command(command):
        subprocess.Popen(command.split())

    def call_logout(self):
        self.call_command(self.config.logout_cmd)
        self.close()

    def call_suspend(self):
        self.call_command(self.config.suspend_cmd)
        self.close()

    def call_restart(self):
        self.call_command(self.config.restart_cmd)
        self.close()

    def call_shutdown(self):
        self.call_command(self.config.shutdown_cmd)
        self.close()


class Config:
    def __init__(self, config_file):
        self.files = [
            '/etc/ob-session-logout/ob-session-logout.conf',
            '~/.config/ob-session-logout/ob-session-logout.conf'
        ]
        self.banner = '/usr/share/ob-session-logout/archlinux-logo-dark.png'
        self.logout_cmd = 'openbox --exit'
        self.suspend_cmd = 'systemctl suspend'
        self.restart_cmd = 'systemctl reboot'
        self.shutdown_cmd = 'systemctl poweroff'
        for i in self.files:
            if os.path.isfile(os.path.expanduser(i)):
                self.read_config_file(os.path.expanduser(i))
        if config_file is not None:
            if os.path.isfile(os.path.expanduser(config_file)):
                self.read_config_file(os.path.expanduser(config_file))

    def read_config_file(self, path):
        if os.path.isfile(path):
            parser = configparser.ConfigParser({
                'banner': '/usr/share/ob-session-logout/archlinux-logo-dark.png',
                'logout': 'openbox --exit',
                'suspend': 'systemctl suspend',
                'restart': 'systemctl reboot',
                'shutdown': 'systemctl poweroff'
            })
            parser.read(path)
            if parser.has_section('Display'):
                self.banner = parser.get('Display', 'banner')
            if parser.has_section('Commands'):
                self.logout_cmd = parser.get('Commands', 'logout')
                self.suspend_cmd = parser.get('Commands', 'suspend')
                self.restart_cmd = parser.get('Commands', 'restart')
                self.shutdown_cmd = parser.get('Commands', 'shutdown')

    def create_default_config(self, path):
        parser = configparser.ConfigParser()
        parser.add_section('Display')
        parser.add_section('Commands')
        parser.set('Display', 'banner', self.banner)
        parser.set('Commands', 'logout', self.logout_cmd)
        parser.set('Commands', 'suspend', self.suspend_cmd)
        parser.set('Commands', 'restart', self.restart_cmd)
        parser.set('Commands', 'shutdown', self.shutdown_cmd)
        with open(os.path.expanduser(path), 'w+') as configfile:
            parser.write(configfile)


class ArgParser:
    def __init__(self):
        self.argparser = argparse.ArgumentParser()
        self.argparser.add_argument('--create-config',
                                    help='creates a config file with default values',
                                    dest='CONFIG_FILE')
        self.argparser.add_argument('-c', '--config',
                                    help='use specified config file',
                                    dest='FILE')
        self.args = self.argparser.parse_args()


argparser = ArgParser()
if argparser.args.CONFIG_FILE is not None:
    cfg = Config(argparser.args.FILE)
    cfg.create_default_config(argparser.args.CONFIG_FILE)
else:
    win = MainWindow(argparser.args.FILE)
    win.show()
    Gtk.main()
