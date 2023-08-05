#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Create a new Tor client, a new hidden service, and connect it to an
nginx server (which is also launched).

There are two arguments that can be passed via the commandline:
    -p\tThe internet-facing port the hidden service should listen on
    -d\tThe directory to serve via http

Example:
    ./nginx.py -p 8080 -d /opt/files/
'''

import functools
import getopt
import sys
import tempfile

from twisted.internet import reactor, protocol, error

import txtorcon


def print_help():
    print __doc__


def print_tor_updates(prog, tag, summary):
    # Prints some status messages while booting tor
    print 'Tor booting [%d%%]: %s' % (prog, summary)


class NginxProcessProtocol(protocol.ProcessProtocol):

    def __init__(self, config):
        """
        """

        self.config = config
        self.stderr = []
        self.stdout = []
        self.to_delete = []

    def outReceived(self, data):
        """
        :api:`twisted.internet.protocol.ProcessProtocol <ProcessProtocol>` API
        """

        self.stdout.append(data)

    def errReceived(self, data):
        """
        :api:`twisted.internet.protocol.ProcessProtocol <ProcessProtocol>` API
        """

        self.stderr.append(data)
        self.transport.loseConnection()
        raise RuntimeError("Received stderr output from nginx process: " + data)

    def cleanup(self):
        """
        Clean up my temporary files.
        """

        [txtorcon.delete_file_or_tree(f) for f in self.to_delete]
        self.to_delete = []

    def processEnded(self, status):
        """
        :api:`twisted.internet.protocol.ProcessProtocol <ProcessProtocol>` API
        """

        self.cleanup()

        if isinstance(status.value, error.ProcessDone):
            return

        raise RuntimeError('\n'.join(self.stdout) + "\n\nnginx exited with error-code %d" % status.value.exitCode)


def setup_complete(config, port, proto):
    # Callback from twisted when tor has booted.
    # We create a reference to this function via functools.partial that
    # provides us with a reference to 'config' and 'port', twisted then adds
    # the 'proto' argument
    print '\nTor is now running. The hidden service is available at'
    print '\n\thttp://%s:%i\n' % (config.HiddenServices[0].hostname, port)
    # This is probably more secure than any other httpd...
    print '### DO NOT RELY ON THIS SERVER TO TRANSFER FILES IN A SECURE WAY ###'


def setup_failed(arg):
    # Callback from twisted if tor could not boot. Nothing to see here, move
    # along.
    print 'Failed to launch tor', arg
    reactor.stop()


def main():
    # Parse the commandline-options
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hd:p:')
    except getopt.GetoptError as excp:
        print str(excp)
        print_help()
        return 1

    serve_directory = '.'               # The default directory to serve files from
    hs_public_port = 8011               # The default port the hidden service is available on
    web_port = 4711                     # The real server's local port
    web_host = '127.0.0.1'              # The real server is bound to localhost
    for o, a in opts:
        if o == '-d':
            serve_directory = a

        elif o == '-p':
            hs_public_port = int(a)

        elif o == '-h':
            print_help()
            return

        else:
            print 'Unknown option "%s"' % (o, )
            return 1

    config = '''
http {
  error_log /tmp/nginxfoo;
  index index.html;

  server {
    listen %d;
    server_name %s;
    root %s;
  }
}
''' % (web_port, web_host, serve_directory)

    config_file = '/tmp/foo'
    open(config_file, 'w').write(config)
    proto = NginxProcessProtocol(config)
    reactor.spawnProcess(proto, '/usr/sbin/nginx',
                         args=('/usr/sbin/nginx', '-c', config_file))

    if False:
        # Create a directory to hold our hidden service. Twisted will unlink it
        # when we exit.
        hs_temp = tempfile.mkdtemp(prefix='torhiddenservice')
        reactor.addSystemEventTrigger('before', 'shutdown',
                                      functools.partial(txtorcon.util.delete_file_or_tree, hs_temp))

        # Add the hidden service to a blank configuration
        config = txtorcon.TorConfig()
        config.SocksPort = 0
        config.HiddenServices = [txtorcon.HiddenService(config, hs_temp,
                                                        ['%i %s:%i' % (hs_public_port,
                                                                       web_host,
                                                                       web_port)])]
        config.save()

        # Now launch tor
        # Notice that we use a partial function as a callback so we have a
        # reference to the config object when tor is fully running.
        tordeferred = txtorcon.launch_tor(config, reactor,
                                          progress_updates=print_tor_updates)
        tordeferred.addCallback(functools.partial(setup_complete, config,
                                                  hs_public_port))
        tordeferred.addErrback(setup_failed)

    reactor.run()


if __name__ == '__main__':
    sys.exit(main())
