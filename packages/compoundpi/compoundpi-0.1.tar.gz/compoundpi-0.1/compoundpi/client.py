# vim: set et sw=4 sts=4 fileencoding=utf-8:

# Copyright 2014 Dave Hughes <dave@waveform.org.uk>.
#
# This file is part of compoundpi.
#
# compoundpi is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# compoundpi is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# compoundpi.  If not, see <http://www.gnu.org/licenses/>.

"Implements the client terminal interface"

from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
_str = str
str = type('')
range = xrange
# Py3: correct super-class calls
# Py3: remove getattr, setattr methods

import sys
import io
import os
import re
import datetime
import fractions
import time
import threading
import select
import struct
import socket
import SocketServer as socketserver
try:
    from ipaddress import IPv4Address, IPv4Network
except ImportError:
    from ipaddr import IPv4Address, IPv4Network

from . import __version__
from .terminal import TerminalApplication
from .cmdline import Cmd, CmdSyntaxError, CmdError


def service(s):
    try:
        return int(s)
    except ValueError:
        return socket.servbyname(s)

def address(s):
    host, port = s.rsplit(':', 1)
    return socket.getaddrinfo(host, service(port), 0, socket.SOCK_STREAM)[0][-1]

def network(s):
    return IPv4Network(s)

def zero_or_more(s):
    result = int(s)
    if result < 0:
        raise ValueError('Value must be 0 or more')
    return result

def one_or_more(s):
    result = int(s)
    if result < 1:
        raise ValueError('Value must be 1 or more')
    return result

def path(s):
    if not os.path.exists(s):
        raise ValueError('%s does not exist' % s)
    if not os.path.isdir(s):
        raise ValueError('%s is not a directory' % s)
    return s

def boolean(s):
    s = s.strip().lower()
    if s in {'true', 't', 'yes', 'y', 'on', '1'}:
        return True
    elif s in {'false', 'f', 'no', 'n', 'off', '0'}:
        return False
    raise ValueError('%s is not a valid boolean' % s)


class CompoundPiClient(TerminalApplication):
    """
    This is the CompoundPi client application which provides a command line
    interface through which you can query and interact with any Pi's running
    the CompoundPi server on your configured subnet. Use the "help" command
    within the application for information on the available commands. The
    application can be configured via command line switches, a configuration
    file (defaults to ~/.cpid.ini), or through the interactive command line
    itself.
    """

    def __init__(self):
        super(CompoundPiClient, self).__init__(
            version=__version__,
            config_files=[
                '/etc/cpi.ini',
                '/usr/local/etc/cpi.ini',
                os.path.expanduser('~/.cpi.ini'),
                ],
            config_bools=[
                'video_port',
                ],
            )
        self.parser.set_defaults(
            network='192.168.0.0/16',
            port=5647,
            bind='0.0.0.0:5647',
            timeout=5,
            capture_delay=0,
            capture_count=1,
            video_port=False,
            output='/tmp',
            )
        self.parser.add_argument(
            '-o', '--output', dest='output', action='store', metavar='PATH',
            help='specifies the directory that downloaded images will be '
            'written to (default: %(default)s)')
        self.parser.add_argument(
            '-n', '--network', dest='network', action='store',
            type=network, help='specifies the network that the servers '
            'belong to (default: %(default)s)')
        self.parser.add_argument(
            '-p', '--port', dest='port', action='store', type=service,
            metavar='PORT',
            help='specifies the port that the servers are listening on '
            '(default: %(default)d)')
        self.parser.add_argument(
            '-b', '--bind', dest='bind', action='store',
            type=address, metavar='ADDRESS:PORT',
            help='specifies the address and port that the client listens on '
            'for downloads (default: %(default)s)')
        self.parser.add_argument(
            '-t', '--timeout', dest='timeout', action='store', type=int,
            metavar='SECS', help='specifies the timeout (in seconds) for '
            'network transactions (default: %(default)d)')
        self.parser.add_argument(
            '--capture-delay', dest='capture_delay', action='store', type=int,
            metavar='SECS', help='specifies the delay (in seconds) used to '
            'synchronize captures. This must be less than the network delay '
            '(default: %(default)d)')
        self.parser.add_argument(
            '--capture-count', dest='capture_count', action='store', type=int,
            metavar='NUM', help='specifies the number of consecutive pictures '
            'to capture when requested (default: %(default)d)')
        self.parser.add_argument(
            '--video-port', dest='video_port', action='store_true',
            help="if specified, use the camera's video port for rapid capture")

    def main(self, args):
        proc = CompoundPiCmd()
        proc.network = args.network
        proc.port = args.port
        proc.bind = args.bind
        proc.timeout = args.timeout
        proc.capture_delay = args.capture_delay
        proc.capture_count = args.capture_count
        proc.video_port = args.video_port
        proc.output = args.output
        proc.cmdloop()


class CompoundPiCmd(Cmd):

    prompt = 'cpi> '

    def __init__(self):
        Cmd.__init__(self)
        self.pprint('CompoundPi Client')
        self.pprint(
            'Type "help" for more information, '
            'or "find" to locate Pi servers')
        self.servers = set()
        self.network = '192.168.0.0/16'
        self.port = 5647
        self.timeout = 5
        self.capture_delay = 0
        self.capture_count = 1
        self.video_port = False
        self.output = '/tmp'
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.server = None

    def __getattr__(self, name):
        # Py3: remove this method
        # This method only exists because computed properties don't work with
        # old-style classes in Python 2
        if name == 'bind':
            return self._get_bind()
        elif name == 'network':
            return self._get_network()
        else:
            return Cmd.__getattr__(self, name)

    def __setattr__(self, name, value):
        # Py3: remove this method
        # This method only exists because computed properties don't work with
        # old-style classes in Python 2
        if name == 'bind':
            self._set_bind(value)
        elif name == 'network':
            self._set_network(value)
        else:
            self.__dict__[name] = value

    def _get_bind(self):
        if self.server:
            return IPv4Address(self.server.socket.getsockname()[0])
    def _set_bind(self, value):
        if self.server:
            self.server.shutdown()
            self.server.socket.close()
            self.server_thread = None
        if value is not None:
            self.server = CompoundPiDownloadServer(value, CompoundPiDownloadHandler)
            self.server.cmd = self
            self.server.event = threading.Event()
            self.server.expected_size = None
            self.server.expected_address = None
            self.server.exception = None
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
    bind = property(_get_bind, _set_bind)

    def _get_network(self):
        return self._network
    def _set_network(self, value):
        self._network = network(value)
        self.servers = set()
    network = property(_get_network, _set_network)

    def preloop(self):
        assert self.server
        Cmd.preloop(self)

    def postloop(self):
        Cmd.postloop(self)
        self.bind = None

    def parse_address(self, s):
        try:
            a = IPv4Address(s.strip())
        except ValueError:
            raise CmdSyntaxError('Invalid address "%s"' % s)
        if not a in self.network:
            raise CmdSyntaxError(
                'Address "%s" does not belong to the configured network '
                '"%s"' % (a, self.network))
        return a

    def parse_address_range(self, s):
        if not '-' in s:
            raise CmdSyntaxError('Expected two dash-separated addresses')
        start, finish = (
            self.parse_address(i)
            for i in s.split('-', 1)
            )
        return start, finish

    def parse_address_list(self, s):
        result = set()
        for i in s.split(','):
            if '-' in i:
                start, finish = self.parse_address_range(i)
                result |= {IPv4Address(a) for a in range(start, finish + 1)}
            else:
                result.add(self.parse_address(i))
        return result

    def complete_server(self, text, line, start, finish):
        return [
            str(server)
            for server in self.servers
            if str(server).startswith(text)
            ]

    def no_servers(self):
        raise CmdError(
                "You must define servers first (see help for 'find' and 'add')")

    def unicast(self, data, address):
        self.socket.sendto(data, (str(address), self.port))

    def broadcast(self, data):
        self.socket.sendto(data, (str(self.network.broadcast), self.port))

    def responses(self, servers=None, count=0):
        if servers is None:
            servers = self.servers
        if not count:
            count = len(servers)
        if not servers:
            servers = self.network
        result = dict()
        start = time.time()
        while time.time() - start < self.timeout:
            if select.select([self.socket], [], [], 1)[0]:
                data, address = self.socket.recvfrom(512)
                address, port = address
                address = IPv4Address(address)
                if port != self.port:
                    self.pprint('Ignoring response from wrong port %s:%d' % (address, port))
                elif address in result:
                    self.pprint('Ignoring double response from %s' % address)
                elif address not in servers:
                    self.pprint('Ignoring unexpected response from %s' % address)
                else:
                    result[address] = data.strip()
                    if len(result) == count:
                        break
        return result

    def transact(self, data, addresses):
        if addresses:
            if isinstance(addresses, str):
                addresses = self.parse_address_list(addresses)
            elif isinstance(addresses, IPv4Address):
                addresses = {addresses}
            for address in addresses:
                self.unicast(data, address)
        else:
            addresses = self.servers
            if not addresses:
                self.no_servers()
            self.broadcast(data)
        responses = self.responses(addresses)
        failed = False
        for address in addresses:
            try:
                response = responses[address]
            except KeyError:
                failed = True
                self.pprint('Missing response from %s' % address)
            else:
                if response.splitlines()[-1].strip() != 'OK':
                    failed = True
                    self.pprint(
                        'Unexpected response from %s: %r' % (address, response))
        if failed:
            raise CmdError('Failed to execute successfully on all servers')
        return responses

    def do_config(self, arg=''):
        """
        Prints the client configuration.

        Syntax: config

        The config command is used to display the current client configuration.
        Use the related "set" command to alter the configuration.

        See also: set.

        cpi> config
        """
        self.pprint_table(
            [('Setting', 'Value')] +
            [(name, getattr(self, name)) for name in (
                'network',
                'port',
                'bind',
                'timeout',
                'capture_delay',
                'capture_count',
                'video_port',
                'output',
                )]
            )

    def do_set(self, arg):
        """
        Change a configuration variable.

        Syntax: set <name> <value>

        The set command is used to alter the value of a client configuration
        variable. Use the related "config" command to view the current
        configuration.

        See also: config.

        cpi> set timeout 10
        cpi> set output /home/camera/
        cpi> set capture_count 5
        """
        match = re.match(r' *(?P<name>[A-Za-z_]+) +(?P<value>.*)', arg)
        if not match:
            raise CmdSyntaxError('You must specify a variable name and value')
        name = match.group('name').lower()
        value = match.group('value').strip()
        try:
            value = {
                'network':       network,
                'port':          service,
                'bind':          address,
                'timeout':       one_or_more,
                'capture_delay': zero_or_more,
                'capture_count': one_or_more,
                'video_port':    boolean,
                'output':        path,
                }[name](value)
        except KeyError:
            raise CmdSyntaxError('Invalid configuration variable: %s' % name)
        setattr(self, name, value)

    def do_servers(self, arg=''):
        """
        Display the list of servers.

        Syntax: servers

        The 'servers' command is used to list the set of servers that the
        client expects to communicate with. The content of the list can be
        manipulated with the 'find', 'add', and 'remove' commands.

        See also: find, add, remove.

        cpi> servers
        """
        if arg:
            raise CmdSyntaxError('Unexpected argument "%s"' % arg)
        if not self.servers:
            self.pprint('No servers are defined')
        else:
            self.pprint_table(
                [('Address',)] +
                [(key,) for key in self.servers]
                )

    def do_find(self, arg=''):
        """
        Find all servers on the current subnet.

        Syntax: find [count]

        The 'find' command is typically the first command used in a client
        session to locate all Pi's on the current subnet. If a count is
        specified, the command will display an error if the expected number of
        Pi's is not located.

        See also: add, remove, servers, identify.

        cpi> find
        cpi> find 20
        """
        if arg:
            try:
                count = int(arg)
            except ValueError:
                raise CmdSyntaxError('Invalid find count "%s"' % arg)
            if count < 1:
                raise CmdSyntaxError('Invalid find count "%d"' % arg)
        else:
            count = 0
        self.broadcast('PING')
        responses = self.responses(count=count)
        for address, response in responses.items():
            if response.strip() != 'OK':
                self.pprint('Ignoring bogus response from %s' % address)
                del responses[address]
        if responses:
            self.servers = set(responses.keys())
            self.pprint('Found %d servers' % len(self.servers))
        else:
            raise CmdError('Failed to find any servers')

    def do_add(self, arg):
        """
        Add addresses to the list of servers.

        Syntax: add <addresses>

        The 'add' command is used to manually define the set of Pi's to
        communicate with. Addresses can be specified individually, as a
        dash-separated range, or a comma-separated list of ranges and
        addresses.

        See also: find, remove, servers.

        cpi> add 192.168.0.1
        cpi> add 192.168.0.1-192.168.0.10
        cpi> add 192.168.0.1,192.168.0.5-192.168.0.10
        """
        if not arg:
            raise CmdSyntaxError('You must specify address(es) to add')
        self.servers |= self.transact('PING', arg).keys()

    def complete_add(self, text, line, start, finish):
        # XXX This is wrong - should be addresses in network that *aren't* in self.servers
        return self.complete_server(text, line, start, finish)

    def do_remove(self, arg):
        """
        Remove addresses from the list of servers.

        Syntax: remove <addresses>

        The 'remove' command is used to remove addresses from the set of Pi's
        to communicate with. Addresses can be specified individually, as a
        dash-separated range, or a comma-separated list of ranges and
        addresses.

        See also: add, find, servers.

        cpi> remove 192.168.0.1
        cpi> remove 192.168.0.1-192.168.0.10
        cpi> remove 192.168.0.1,192.168.0.5-192.168.0.10
        """
        if not arg:
            raise CmdSyntaxError('You must specify address(es) to remove')
        self.servers -= self.parse_address_list(arg)

    def complete_remove(self, text, line, start, finish):
        return self.complete_server(text, line, start, finish)

    status_re = re.compile(
            r'RESOLUTION (?P<width>\d+) (?P<height>\d+)\n'
            r'FRAMERATE (?P<rate>\d+(\.\d+)?)\n'
            r'TIMESTAMP (?P<time>\d+(\.\d+)?)\n'
            r'IMAGES (?P<images>\d{,3})\n'
            r'OK')
    def do_status(self, arg=''):
        """
        Retrieves status from the defined servers.

        Syntax: status [addresses]

        The 'status' command is used to retrieve configuration information from
        servers. If no addresses are specified, then all defined servers will
        be queried.

        See also: resolution, framerate.

        cpi> status
        """
        responses = [
            (address, data, self.status_re.match(data))
            for (address, data) in self.transact('STATUS', arg).items()
            ]
        self.pprint_table(
            [('Address', 'Resolution', 'Framerate', 'Timestamp', 'Images')] +
            [
                (
                    address,
                    '%sx%s' % (match.group('width'), match.group('height')),
                    '%sfps' % match.group('rate'),
                    datetime.datetime.fromtimestamp(float(match.group('time'))),
                    int(match.group('images')),
                    )
                for (address, data, match) in responses
                if match
                ])
        for (address, data, match) in responses:
            if not match:
                self.pprint('Invalid response from %s:\n%s' % (address, data))

    def complete_status(self, text, line, start, finish):
        return self.complete_server(text, line, start, finish)

    def do_resolution(self, arg):
        """
        Sets the resolution on the defined servers.

        Syntax: resolution <width>x<height> [addresses]

        The 'resolution' command is used to set the capture resolution of the
        camera on all or some of the defined servers.

        If no address is specified then all currently defined servers will be
        targetted. Multiple addresses can be specified with dash-separated
        ranges, comma-separated lists, or any combination of the two.

        See also: status, framerate.

        cpi> resolution 640x480
        cpi> resolution 1280x720 192.168.0.54
        cpi> resolution 1280x720 192.168.0.1,192.168.0.3
        """
        if not arg:
            raise CmdSyntaxError('You must specify a resolution')
        arg = arg.split(' ', 1)
        try:
            width, height = arg[0].lower().split('x')
            width, height = int(width), int(height)
        except (TypeError, ValueError) as exc:
            raise CmdSyntaxError('Invalid resolution "%s"' % arg[0])
        self.transact(
                'RESOLUTION %d %d' % (width, height),
                arg[1] if len(arg) > 1 else '')

    def do_framerate(self, arg):
        """
        Sets the framerate on the defined servers.

        Syntax: framerate <rate> [addresses]

        The 'framerate' command is used to set the capture framerate of the
        camera on all or some of the defined servers. The rate can be specified
        as an integer or floating-point number, or as a fractional value.

        If no address is specified then all currently defined servers will be
        targetted. Multiple addresses can be specified with dash-separated
        ranges, comma-separated lists, or any combination of the two.

        See also: status, resolution.

        cpi> framerate 30
        cpi> framerate 90 192.168.0.1
        cpi> framerate 15 192.168.0.1-192.168.0.10
        """
        if not arg:
            raise CmdSyntaxError('You must specify a framerate')
        arg = arg.split(' ', 1)
        try:
            rate = fractions.Fraction(rate)
        except (TypeError, ValueError) as exc:
            raise CmdSyntaxError('Invalid framerate "%s"' % arg[0])
        self.transact(
                'FRAMERATE %s' % rate,
                arg[1] if len(arg) > 1 else '')

    def do_capture(self, arg=''):
        """
        Captures images from the defined servers.

        Syntax: capture [addresses]

        The 'capture' command causes the servers to capture an image. Note
        that this does not cause the captured images to be sent to the client.
        See the 'download' command for more information.

        If no addresses are specified, a broadcast message to all defined
        servers will be used in which case the timestamp of the captured images
        are likely to be extremely close together. If addresses are specified,
        unicast messages will be sent to each server in turn.  While this is
        still reasonably quick there will be a measurable difference between
        the timestamps of the last and first captures.

        See also: download, list, clear.

        cpi> capture
        cpi> capture 192.168.0.1
        cpi> capture 192.168.0.50-192.168.0.53
        """
        cmd = 'CAPTURE %d %d'
        params = [self.capture_count, self.video_port]
        if self.capture_delay:
            cmd += ' %f'
            params.append(time.time() + self.capture_delay)
        self.transact(cmd % tuple(params), arg)

    def complete_capture(self, text, line, start, finish):
        return self.complete_server(text, line, start, finish)

    def do_download(self, arg=''):
        """
        Downloads captured images from the defined servers.

        Syntax: download [addresses]

        The 'download' command causes each server to send its captured images
        to the client. Servers are contacted consecutively to avoid saturating
        the network bandwidth. Once images are successfully downloaded from a
        server, they are wiped from the server.
        """
        if arg:
            addresses = self.parse_address_list(arg)
        else:
            addresses = self.servers
            if not addresses:
                self.no_servers()
        for address in addresses:
            self.server.expected_address = address
            response = self.transact('LIST', address)[address]
            response = response.strip().splitlines()[:-1]
            for index, details in enumerate(response):
                try:
                    timestamp, size = details.split(' ', 1)
                    timestamp = float(timestamp)
                    size = int(size)
                except (ValueError, TypeError):
                    raise CmdError(
                        'Received invalid image details from %s' % address)
                self.server.expected_size = size
                self.server.event.clear()
                self.transact('SEND %d %d' % (index, self.port), address)
                if self.server.event.wait(self.timeout):
                    if self.server.exception:
                        raise CmdError(str(self.server.exception))
                else:
                    raise CmdError(
                        'Timed out waiting for image transfer from %s' % address)
                self.pprint('Downloaded image %d from %s' % (index, address))
            self.transact('CLEAR', address)

    def complete_download(self, text, line, start, finish):
        return self.complete_server(text, line, start, finish)

    def do_identify(self, arg):
        """
        Blink the LED on the specified servers.

        Syntax: identify [addresses]

        The 'identify' command can be used to locatea specific Pi server (or
        servers) by their address. It sends a command causing the camera's LED
        to blink on and off for 5 seconds. If no addresses are specified, the
        command will be sent to all defined servers (this can be useful after
        the 'find' command to determine whether any Pi's failed to respond due
        to network issues).

        See also: find.

        cpi> identify
        cpi> identify 192.168.0.1
        cpi> identify 192.168.0.3-192.168.0.5
        """
        responses = self.transact('BLINK', arg)

    def complete_identify(self, text, line, start, finish):
        return self.complete_server(text, line, start, finish)


class CompoundPiDownloadHandler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            if self.client_address[0] != str(self.server.expected_address):
                raise ValueError(
                    'Connection from unexpected address: %s instead of %s' %
                    (self.client_address[0], self.server.expected_address))
            timestamp, size = struct.unpack(_str('<dL'), self.request.recv(12))
            if size != self.server.expected_size:
                raise ValueError(
                    'Image size differs from LIST result: '
                    '%d != %d' % (size, self.server.expected_size))
            # Guard against something sending a ridiculously large file
            if size > 10*1024*1024:
                raise ValueError('Image size is unreasonably large: %d' % size)
            timestamp = datetime.datetime.fromtimestamp(timestamp)
            filename = os.path.join(
                self.server.cmd.output, '%s-%s.jpg' % (
                    timestamp.strftime('%Y%m%d%H%M%S%f'),
                    self.client_address[0],
                ))
            with io.open(filename, 'wb') as output:
                while size > 0:
                    data = self.request.recv(1024)
                    output.write(data)
                    size -= len(data)
            if size > 0:
                raise ValueError('Server did not transmit entire image')
        except Exception as e:
            self.server.exception = e
        else:
            self.server.exception = None
        finally:
            self.server.event.set()


class CompoundPiDownloadServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


main = CompoundPiClient()
