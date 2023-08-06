""" Module providing a single class (QualysConnectConfig) that parses a config
file and provides the information required to build QualysGuard sessions.
"""
import os
import stat
import sys
import getpass
import logging

from ConfigParser import *

import qualysconnect.settings as qcs

__author__ = "Colin Bell <colin.bell@uwaterloo.ca>"
__copyright__ = "Copyright 2011-2013, University of Waterloo"
__license__ = "BSD-new"

class QualysConnectConfig:
    """ Class to create a ConfigParser and read user/password details
    from an ini file.
    """
    def __init__(self, filename=qcs.default_filename):

        self._cfgfile = None
        
        if os.path.exists(filename):
            self._cfgfile = filename
        elif os.path.exists(os.path.join(os.getenv("HOME"),filename)):
            self._cfgfile = os.path.join(os.getenv("HOME"),filename)
        
        # create ConfigParser to combine defaults and input from config file.
        self._cfgparse = ConfigParser(qcs.defaults)

        if self._cfgfile:
            self._cfgfile = os.path.realpath(self._cfgfile)
            
            mode = stat.S_IMODE(os.stat(self._cfgfile)[stat.ST_MODE])
            
            # apply bitmask to current mode to check ONLY user access permissions.
            if (mode & ( stat.S_IRWXG | stat.S_IRWXO )) != 0:
                logging.warning("%s permissions allows more than user access."%(filename,))

            self._cfgparse.read(self._cfgfile)

        # if 'info' doesn't exist, create the section.
        if not self._cfgparse.has_section("info"):
            self._cfgparse.add_section("info")

        # use default hostname (if one isn't provided)
        if not self._cfgparse.has_option("info","hostname"):
            if self._cfgparse.has_option("DEFAULT","hostname"):
                hostname = self._cfgparse.get("DEFAULT","hostname")
                self._cfgparse.set('info', 'hostname', hostname)
            else:
                raise Exception("No 'hostname' set. QualysConnect does not know who to connect to.")
        
        # ask username (if one doesn't exist)
        if not self._cfgparse.has_option("info","username"):
            username = raw_input('QualysGuard Username: ')
            self._cfgparse.set('info', 'username', username)
        
        # ask password (if one doesn't exist)
        if not self._cfgparse.has_option("info", "password"):
            password = getpass.getpass('QualysGuard Password: ')
            self._cfgparse.set('info', 'password', password)
        
        logging.debug(self._cfgparse.items('info'))
            
    def get_config_filename(self):
        return self._cfgfile
    
    def get_config(self):
        return self._cfgparse
        
    def get_username(self):
        ''' Returns username from the configfile. '''
        return self._cfgparse.get("info", "username")
        
    def get_password(self):
        ''' Returns password from the configfile OR as provided. '''
        return self._cfgparse.get("info", "password")

    def get_hostname(self):
        ''' Returns username from the hostname. '''
        return self._cfgparse.get("info", "hostname")