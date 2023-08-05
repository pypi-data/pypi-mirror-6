#!/usr/bin/env python
"""Simple messaging server to receieve queueing requests
from distributed clients, and save them in a pre-defined textual
format in order to be picked up by spiders (which will push
responses back via. HTTP)."""

from daemon import AbstractDaemon
from handler import Handler
import json
import logging
import logging.handlers
import os
import SocketServer
import sys
import traceback
import warnings


class Server(AbstractDaemon):
    """A messaging server daemon."""
    
    # -------------------------------------------------------------------------
    # -- these are the most common/likely things for a subclass to want      --
    # -- to override; you really must* override service_name if you run more --
    # -- than one distinct one of these on a machine at a time               --
    # -------------------------------------------------------------------------
    
    # default interface to bind to, and default port
    # override these in a subclass if desired, or send them explicitly to __init__
    bind_interface = '127.0.0.1'
    port = 5766
    
    # used for the name of the logger as well as some default paths:
    # override this in subclasses
    service_name = 'messaging'
    
    # the handler class for requests made to this daemon
    # the default Handler class only has a ping method, so this must be overridden
    # for the messaging server to actually do anything important
    handler = Handler
    
    # ---------------------------------------------------
    # -- these are probably fine as is for most people --
    # ---------------------------------------------------
    
    # logging options
    # note: if you override the path in a subclass, retain the trailing slash
    request_log_level = logging.INFO
    error_log_level = logging.ERROR
    max_log_file_size = 10 ** 7
    rotating_log_file_max = 5
    log_file_path = property(lambda self: '/var/log/%s/' % self.service_name)
    
    # set a default pid file name
    pid_file = property(lambda self: '/tmp/%s.pid' % self.service_name)
    
    # version number: defaults to the version number for the
    # messaging package, but can be freely overridden
    version = '1.0'
    
    # --------------------------------------------------------------------
    # -- instance methods; these can be overridden as necessary, but    --
    # -- make sure their return signatures stay the same. For __init__, --
    # -- you should be sure and call the base class' __init__.          --
    # --------------------------------------------------------------------
    
    def __init__(self, bind_interface=None, port=None, handler=None, output_to_screen=False, **kwargs):
        """Daemon constructor."""
        
        # call the superclass constructor
        super(Server, self).__init__(pidfile=kwargs.get('pid_file', self.pid_file))
        
        # set the bind interface to the class default
        # unless it's explicitly set
        self.address = (
            bind_interface or self.bind_interface,
            int(port) if port else self.port,
        )
        
        # set the instance handler to the class handler,
        # or to the keyword argument if excplitly set
        self.instance_handler = handler or self.handler
        
        # save the output_to_screen variable
        self.output_to_screen = output_to_screen
        
        # save any additional keyword arguments, and make them
        # available on the server object
        self.kw_options = kwargs
                        
    def setup_request_log(self, **kwargs):
        """Create and return a logging object to function as the request log for this daemon."""
        
        # get my log file path; make sure it has a trailing slash
        log_file_path = kwargs.get('log_file_path', self.log_file_path)
        if log_file_path[-1] != '/':
            log_file_path += '/'
        
        # set up the request log
        try:
            request_log_file = log_file_path + self.service_name + '.request.log'
            request_log = logging.getLogger(self.service_name)
            request_log.setLevel(kwargs.get('request_log_level', self.request_log_level))
            request_log.addHandler(logging.handlers.RotatingFileHandler(request_log_file,
                backupCount=kwargs.get('rotating_log_file_max', self.rotating_log_file_max),
                maxBytes=kwargs.get('max_log_file_size', self.max_log_file_size),
            ))
        except:
            warnings.warn('Something went wrong with the request logger.\nDoes the executing user have write permission to your request log file (%s)?' % request_log_file, Warning)
        
        # done, return back the request_log    
        return request_log
    
    def setup_error_log(self, **kwargs):
        """Create and return a logging object to function as the error log for this daemon."""
        
        # get my log file path; make sure it has a trailing slash
        log_file_path = kwargs.get('log_file_path', self.log_file_path)
        if log_file_path[-1] != '/':
            log_file_path += '/'
        
        # set up the error log
        try:
            error_log_file = log_file_path + self.service_name + '.error.log'
            error_log = logging.getLogger(self.service_name + '.errors')
            error_log.setLevel(kwargs.get('error_log_level', self.error_log_level))
            error_log.addHandler(logging.handlers.RotatingFileHandler(error_log_file,
                backupCount=kwargs.get('rotating_log_file_max', self.rotating_log_file_max),
                maxBytes=kwargs.get('max_log_file_size', self.max_log_file_size),
            ))
        except:
            warnings.warn('Something went wrong with the error logger.\nDoes the executing user have write permission to your error log file (%s)?' % error_log_file, Warning)
            
        # done, return back the error log
        return error_log
    
    def run(self):
        """Actually run the daemon."""
        
        # attach a few things to the handler class
        # so methods there have easy access to them
        self.handler.request_log = self.setup_request_log(**self.kw_options)
        self.handler.error_log = self.setup_error_log(**self.kw_options)
        self.handler.output_to_screen = self.output_to_screen
        self.handler.version = self.version
        
        # if any additional options were sent in __init__,
        # set them to the handler also
        for key, value in self.kw_options.iteritems():
            setattr(self.handler, key, value)
        
        # get my server address as a tuple
        server = SocketServer.ThreadingTCPServer(self.address, self.handler)
        
        try:
            # make megavolt ready for commands
            server.serve_forever()
        except KeyboardInterrupt:
            self.pre_shutdown()

            # get the hell outta dodge...
            sys.exit(0)
            
    def pre_shutdown(self):
        """Code to run when the server is being shut down."""
        print '\n'