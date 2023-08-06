#!/usr/bin/env python
#-*- conding: utf-8 -*-
import ConfigParser
import sys

class Config( object ):

    def __init__( self, configfile ):
        self.configfile = configfile
        self.config     = ConfigParser.ConfigParser()
        self.config.read( configfile )

    def get_servers( self ):
        servers = list()

        try:
            for section in self.config.sections():
                if section != "ssher":
                    servers.append( { 'hostname': self.config.get( section, 'hostname' ),
                                      'username': self.config.get( section, 'username' ),
                                      'ip'      : self.config.get( section, 'ip' ),
                                      'tunnel'  : self.config.get( section, 'tunnel'),
                                      'port'    : self.config.get( section, 'port'),
                                      'formal'  : self.config.get( section, 'formal'),
                                      'group'   : self.config.get( section, 'group'),
                                   }
                                  )
        except Exception, msg:
            print "The following error have been encountered in the configuration file: %s" % msg

            sys.exit(-1)

        return servers

    def get_internal_config( self ):
        values = {'color': self.config.getboolean('ssher', 'color')}
        return values

