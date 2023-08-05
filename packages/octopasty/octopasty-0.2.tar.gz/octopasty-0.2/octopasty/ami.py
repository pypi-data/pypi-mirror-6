#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Octopasty is an Asterisk AMI proxy

# Copyright © 2011, 2012  Jean Schurger <jean@schurger.org>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""\
AMI protocol and proxy.
"""

__metaclass__ = type

# Main modules.

import gevent
import random
from gevent import socket
import time

import bubble

# Web related modules.
import Cookie
import json
import urlparse
from xml.sax import saxutils

welcome_prefix = 'Asterisk Call Manager/'
welcome_version = '1.2'

# Maximum time for a bubble to get transient replies or messages.
default_reply_timeout = 10

# Maximum time for a client to stay unused.
idle_client_timeout = 1200

# Maximum time to wait for a Login to be completed from the client.
login_wait_timeout = 60


class AMI_Message(dict):
    "AMI Message.  Case and order preserved, but case insensitive gets."
    # Note: the dict interface is incomplete, but sufficient for our needs.

    # List of command output lines (without the new lines).
    _extra_lines = None

    # Recipient bubble of the AMI message after decoding, else None.
    _received_by = None

    def __init__(self, pairs=()):
        dict.__init__(self)
        # From lower case key to proper capitalization.
        self._canonical = {}
        # Forced sweep order for (lower-case) keys and values.
        self._order = []
        for key, value in pairs:
            self[key] = value

    def __contains__(self, key):
        return key.lower() in self._canonical

    def __delitem__(self, key):
        lower_key = key.lower()
        del self._canonical[lower_key]
        self._order.remove(lower_key)
        dict.__delitem__(self, lower_key)

    def __getitem__(self, key):
        return dict.__getitem__(self, key.lower())

    def __iter__(self):
        for key in self._order:
            yield self._canonical[key]

    def __repr__(self):
        fragments = []
        for key, value in self.iteritems():
            fragments.append('%s: %s' % (key, value))
        if self._extra_lines is None:
            return '{%s}' % ', '.join(fragments)
        return '{%s}%r' % (', '.join(fragments), self._extra_lines)

    def __setitem__(self, key, value):
        lower_key = key.lower()
        canonical = self._canonical.get(lower_key)
        if canonical is None:
            self._canonical[lower_key] = key
            self._order.append(lower_key)
        else:
            assert key in (lower_key, canonical), (
                "Inconsistent capitalization: %s vs %s."
                % (key, canonical))
        dict.__setitem__(self, lower_key, value)

    def __str__(self):
        fragments = []
        write = fragments.append
        if self._received_by is not None:
            write('Received-By: %s\n' % self._received_by)
        for key, value in self.iteritems():
            write('%s: %s\n' % (key, value))
        if self._extra_lines is not None:
            for line in self._extra_lines:
                write('%s\n' % line)
        return ''.join(fragments)

    def clear(self):
        dict.clear(self)
        self._canonical.clear()
        del self._order[:]

    def get(self, key, default=None):
        return dict.get(self, key.lower(), default)

    def iteritems(self):
        for key in self._order:
            yield self._canonical[key], dict.__getitem__(self, key)

    iterkeys = __iter__

    def itervalues(self):
        for key in self._order:
            yield dict.__getitem__(self, key)

    def items(self):
        return list(self.iteritems())

    def keys(self):
        return list(self.iterkeys())

    def values(self):
        return list(self.itervalues())

    ## The following is not part of the dict interface.

    @classmethod
    def decode(cls, lines):
        "Decode a block of lines into a new AMI message."
        self = AMI_Message()
        for line in lines:
            if self._extra_lines is None:
                fragments = line.split(':', 1)
                if len(fragments) == 2:
                    key, value = fragments
                    if key in self:
                        bubble.log.user(
                            "Duplicated key %s in AMI message:\n%s",
                            key, self)
                    else:
                        self[key] = value.strip()
                    continue
                if self.get_lower('Response') != 'follows':
                    bubble.log.user(
                        "Misformed AMI message line %r within:\n%s",
                        line, '\n'.join(lines))
                    continue
                self._extra_lines = []
            if self._extra_lines is not None:
                self._extra_lines.append(line)
        return self

    def get_lower(self, key, default=None):
        "As get(KEY).lower(), save that a None result gets through."
        value = dict.get(self, key.lower(), default)
        if value is not None:
            value = value.lower()
        return value

    def encode(self):
        fragments = []
        write = fragments.append
        for key, value in self.iteritems():
            write('%s: %s\r\n' % (key, value))
        if self._extra_lines is not None:
            for line in self._extra_lines:
                write(line + '\r\n')
        write('\r\n')
        return ''.join(fragments)


class Client(bubble.Reactive_Bubble):
    "Handle a new incoming connection from a client."
    accepted_types = AMI_Message
    idle_timeout = idle_client_timeout

    # IP address and port, or None for an internal login.
    address = None

    # Saved challenge for later login validation.
    challenge = None

    # User configuration, set only once the login succeeded.
    user = None

    # Server name list, set once the login succeeded.
    server_names = None

    class Error(Exception):
        pass

    @bubble.switching
    def configure(self, config, writer):
        "Present an AMI interface to our client."

        def check_for_login():
            gevent.sleep(login_wait_timeout)
            if self.user is None:
                bubble.log.user("%s got no login for %d seconds.",
                                self, login_wait_timeout)
                self.kill(block=False)

        self.config = config
        self.writer = writer
        gevent.spawn(check_for_login)

    def do_AMI_Message(self, ami_message):
        # The asynchronous version is for the AMI client.
        handler = self.get_handler(ami_message)
        if handler is not None:
            handler.main(self, ami_message, block=False)

    def get_handler(self, ami_message):
        try:
            if not ('Action' in ami_message):
                raise Client.Error("Missing Action: in request")
            key = canonical_action.get(ami_message['Action'].lower())
            maker = None if key is None else manager_actions.get(key)
            if maker is None:
                raise Client.Error(
                    "Invalid/unknown command: %s."
                    # Mocking Asterisk, let's pretend we do not know
                    # how to correctly use full stops!
                    " Use Action: ListCommands to show available commands."
                    % ami_message['Action'])
            if self.user is None:
                if maker.need_prior_login:
                    raise Client.Error("Permission denied")
            else:
                if (self.user.action_filter
                    and (maker.name.lower()
                         not in self.user.action_filter)):
                    raise Client.Error("Action rejected by action_filter.")
                if maker.privileges is not None:
                    if not (set(maker.privileges or ())
                            & set(self.user.privileges)):
                        raise Client.Error("Insufficient privileges.")
            return maker()
        except Client.Error, exception:
            # Send AMI error with DIAGNOSTIC message.
            diagnostic = str(exception)
            bubble.log.user('%s', diagnostic)
            ami_reply = AMI_Message([('Response', 'Error'),
                                     ('Message', diagnostic)])
            if 'ActionID' in ami_message:
                ami_reply['ActionID'] = ami_message.get('ActionID')
            self.writer.write_ami_message(ami_reply, block=False)

    @bubble.switching
    def process_ami_message(self, ami_message, block=True):
        # The synchronous version is for the Web client.
        handler = self.get_handler(ami_message)
        if handler is not None:
            handler.main(self, ami_message)


class Log_Forwarder(bubble.Reactive_Bubble):
    "Merely forward all input log entries to the output bus."
    accepted_types = bubble.Log_Entry

    def do_Log_Entry(self, log_entry):
        self.send_message(log_entry)


# The following contents are initially collected from the "asterisk"
# and "internal" modules, and later by the ami.Server.Login bubble
# when each Asterisk server responds to a ListCommands action.

# From lower cased action name to canonical action name.
canonical_action = {}

# From Manager_Action name to Manager_Action subclass.
manager_actions = {}


class Manager_Action(bubble.Active_Bubble):
    """\
Base class and default processing for AMI commands.

Essentially, send an AMI action to servers, then aggregate results.
"""
    accepted_types = AMI_Message
    action_id = None

    # Static variable of this base class, saving last server name where
    # action was sent, used to balance load a bit.
    last_server_name = None

    # When false, action may be used even before the user logs in.
    need_prior_login = True

    # List of privilege strings.  None means action is granted to all.
    privileges = None

    def aggregate(self, replies):
        "Aggregate REPLIES into one or more AMI messages."
        # Default is to forward everything received from a single server.
        for ami_messages in replies.itervalues():
            return ami_messages
        return AMI_Message([('Response', 'Error'),
                            ('Message', "No server replied.")])

    def broadcast(self, client, ami_message, server_names):
        "Return a list of server names where AMI_MESSAGE should be sent."
        # An implemented override function may directly return an AMI response
        # instead of a list, bypassing all servers and the need of AGGREGATE.
        # Default is to pick a single server, trying to round-robin among them.
        name = Manager_Action.last_server_name
        if name in server_names:
            index = server_names.index(name) + 1
            server_names = server_names[index:] + server_names[:index]
        for name in server_names:
            if name in Server.registry:
                Manager_Action.last_server_name = name
                return [name]

    def is_last(self, ami_message):
        "Does this AMI message conclude all replies for this server?"
        # Default is to stop on a Response message.
        return 'Response' in ami_message

    @bubble.switching
    def main(self, client, ami_message):
        logging_off = False
        original_action_id = ami_message.get('ActionID')
        try:
            # Comply with a Server: header.
            text = ami_message.get('Server')
            server_names = client.server_names
            if text is not None:
                authorized = set()
                unauthorized = set()
                for name in text.replace(',', ' ').split():
                    if name in client.server_names:
                        authorized.add(name)
                    else:
                        unauthorized.add(name)
                server_names = sorted(authorized)
                if unauthorized:
                    bubble.log.user(
                        "Unauthorized server (%s) in Server header:\n%s",
                        ', '.join(sorted(unauthorized)), ami_message)

            # Broadcast the request.
            broadcast = self.broadcast(client, ami_message, server_names)
            if isinstance(broadcast, AMI_Message):
                response = broadcast
                broadcast = None
            else:
                response = None

            # REPLIES holds, by server, a list of received AMI messages.
            replies = {}
            if broadcast:
                action_id = str(self)
                ami_message['ActionID'] = action_id
                expected = set()
                names = []
                for name in broadcast:
                    server = Server.registry.get(name)
                    if isinstance(self, server.accepting):
                        names.append(server.config.name)
                        server.redirect(action_id, self)
                        server.writer.write_ami_message(
                            ami_message, block=False)
                        expected.add(server)
                    bubble.log.action(
                        "To server %s:\n%s", ', '.join(names), ami_message)

                # Receive and accumulate all replies.
                now = time.time()
                limit = now + default_reply_timeout
                complete = set()
                while complete != expected and now < limit:
                    now = time.time()
                    try:
                        ami_reply = self.get_message(timeout=limit - now)
                    except gevent.Timeout:
                        break
                    else:
                        server = self.envelope.sender
                        bubble.log.action(
                            "From server %s:\n%s",
                            server.config.name, ami_reply)
                        if server not in replies:
                            replies[server] = []
                        replies[server].append(ami_reply)
                        if self.is_last(ami_reply):
                            server.unredirect(action_id, block=False)
                            complete.add(server)
                for server in sorted(expected - complete):
                    bubble.log.error(
                        "Missing or incomplete reply to %s from server %s",
                        self.name, server.config.name)
                    server.unredirect(action_id, block=False)

            # Aggregate replies and send results (often a single AMI message).
            if response is None:
                ami_replies = self.aggregate(replies)
                if isinstance(ami_replies, AMI_Message):
                    ami_replies = ami_replies,
            else:
                ami_replies = response,
            client.writer.write_ami_message(False, block=False)
            for ami_reply in ami_replies:
                # Internally generated AMI messages would miss an ActionID.
                if 'ActionID' in ami_reply:
                    del ami_reply['ActionID']
                if original_action_id is not None:
                    ami_reply['ActionID'] = original_action_id
                client.writer.write_ami_message(ami_reply, block=False)
                if ami_reply.get('Response') == 'Goodbye':
                    logging_off = True
            client.writer.write_ami_message(True, block=False)
        finally:
            if logging_off:
                client.kill(block=False)
            self.kill(block=False)


class Reader(bubble.Active_Bubble):
    "Input augmented with AMI specific methods, and buffering from socket."
    accepted_types = str
    daemon = True

    @bubble.switching
    def forward_ami_messages(self, recipient):
        """\
Receive and decode all AMI messages and send them to RECIPIENT.
Also mark the AMI message as having been sent to this recipient.
When MESSAGE_TIMEOUT is specified and timeout occurs, exit this bubble.
"""
        lines = []
        while True:
            line = self.get_message().rstrip()
            if line:
                lines.append(line)
            else:
                ami_message = AMI_Message.decode(lines)
                ami_message._received_by = recipient
                recipient.add_message(ami_message)
                lines = []

    @bubble.switching
    def read_line(self):
        "Read a single line from socket."
        return self.get_message()

    @bubble.switching
    def set_file(self, file):
        input = bubble.Input(suffix=None)
        input.link(self._suicide)
        input.set_file(file)
        input.forward_lines(self, block=False)

    @bubble.switching
    def set_socket(self, handle):
        "Use socket HANDLE to read it and buffer its contents into here."
        input = bubble.Input(suffix=None)
        input.link(self._suicide)
        input.set_socket(handle)
        input.forward_lines(self, block=False)


class Server(bubble.Reactive_Bubble):
    "Handle AMI messages in and out of an Asterisk server."
    accepted_types = AMI_Message
    # Forbid inheriting IDLE_TIMEOUT from other bubbles, like Login.
    idle_timeout = None
    registry = {}

    # FIXME: Connection should be re-established whenever it breaks,
    # and login should be re-attempted each time Asterisk sends its
    # welcome message.

    class Login(bubble.Active_Bubble):
        "Send a Login action to SERVER and wait for the response."
        accepted_types = AMI_Message
        idle_timeout = default_reply_timeout

        @bubble.switching
        def main(self, server):
            action_id = str(self)
            name = server.config.name
            server.redirect(action_id, self)
            try:

                # Send the Login request.
                server.writer.write_ami_message(
                    AMI_Message([('Action', 'Login'),
                                 ('ActionID', action_id),
                                 ('Username', server.config.username),
                                 ('Secret', server.config.password)]),
                    block=False)
                try:
                    ami_reply = self.get_message(
                        timeout=default_reply_timeout)
                except gevent.Timeout:
                    bubble.log.error(
                        "Server %s does not reply to Login request.", name)
                    server.set_logged_in(False, block=False)
                    return
                else:
                    if ami_reply['Response'] != 'Success':
                        bubble.log.error(
                            "Unsuccessful Login:\n%s", ami_reply)
                        server.set_logged_in(False, block=False)
                        return

                # Save commands accepted by this server.
                accepting = set()
                if not server.config.readonly:

                    # Send the ListCommands request.
                    server.writer.write_ami_message(
                        AMI_Message([('Action', 'ListCommands'),
                                     ('ActionID', action_id)]),
                        block=False)
                    try:
                        ami_reply = self.get_message(
                            timeout=default_reply_timeout)
                    except gevent.Timeout:
                        bubble.log.error(
                            "Server %s does not reply to"
                            " ListCommands request.",
                            name)
                        server.set_logged_in(False, block=False)
                        return
                    else:
                        if ami_reply['Response'] != 'Success':
                            bubble.log.error(
                                "Unsuccessful ListCommands:\n%s", ami_reply)
                            server.set_logged_in(False, block=False)
                            return

                        for key, value in ami_reply.iteritems():
                            if key in ('ActionID', 'Response'):
                                continue
                            if not ('(Priv:' in value and value.endswith(')')):
                                bubble.log.warn(
                                    "For server %s,"
                                    " %s does not specify Priv:\n%s",
                                    name, key, value)
                                continue
                            fragments = value.split('(Priv:', 1)
                            documentation = fragments[0].rstrip()
                            privileges = fragments[1].lstrip()[:-1]
                            privileges = (None if privileges == '<none>'
                                          else tuple(privileges.split(',')))
                            if key.lower() in canonical_action:
                                maker = manager_actions[
                                    canonical_action[key.lower()]]
                                if (privileges != maker.privileges
                                        and hasattr(maker, '_defined_by')):
                                    bubble.log.warn(
                                        "For server %s, %s has privileges:\n%s"
                                        "\nFor the same, server %s shows:\n%s",
                                        name, key, privileges,
                                        maker._defined_by, maker.privileges)
                            else:
                                maker = type(key, (Manager_Action,),
                                             {'name': key,
                                              'summary': documentation,
                                              '_defined_by': name,
                                              'privileges': privileges})
                                canonical_action[key.lower()] = key
                                manager_actions[key] = maker
                            accepting.add(maker)

                # Everything is OK!
                server.accepting = tuple(accepting)
                server.set_logged_in(True, block=False)

            finally:
                server.unredirect(action_id, block=False)

    class Logoff(bubble.Active_Bubble):
        "Send a Logoff action to SERVER and wait for the response."
        accepted_types = AMI_Message
        idle_timeout = default_reply_timeout

        @bubble.switching
        def main(self, server):
            action_id = str(self)
            name = server.config.name
            server.redirect(action_id, self)
            try:
                server.writer.write_ami_message(
                    AMI_Message([('Action', 'Logoff')]),
                    block=False)
                # The following loop skips over unrelated events or replies.
                now = time.time()
                limit = now + default_reply_timeout
                while False and now < limit:
                    now = time.time()
                    try:
                        ami_reply = self.get_message(timeout=limit - now)
                    except gevent.Timeout:
                        bubble.log.error(
                            "Server %s does not reply to Logoff request.",
                            name)
                        break
                    else:
                        if ami_reply['Response'] == 'Success':
                            server.logged_in = False
                            break
            finally:
                server.unredirect(action_id, block=False)

    # If logging into Asterisk server was successful.
    logged_in = False

    @bubble.switching
    def configure(self, config):
        name = config.name
        if name in Server.registry:
            bubble.log.error("Server %s already configured.", name)
            return
        self.name_suffix = '-' + name
        Server.registry[name] = self
        self.config = config
        bubble.log.debug("Contacting Asterisk server %s at %s, port %d.",
                         name, config.host, config.port)
        handle = socket.socket()
        handle.connect((config.host, config.port))
        self.reader = Reader(suffix=None)
        self.reader.set_socket(handle)
        self.writer = Writer(suffix=None)
        self.writer.configure('rawman')
        self.writer.set_socket(handle)
        # Accept nothing until ListCommand output gets analyzed.
        self.accepting = ()
        try:
            line = self.reader.read_line(timeout=default_reply_timeout)
        except gevent.Timeout:
            bubble.log.error(
                "Server %s does not reply to connection attempt.", name)
        else:
            if line.startswith(welcome_prefix):
                self.redirections = {}
                self.login = self.Login(suffix=None)
                self.login.main(self, block=False)
                self.reader.forward_ami_messages(self, block=False)
            else:
                bubble.log.error(
                    "Was expecting `%s', got:\n%r", welcome_prefix, line)

    def do_AMI_Message(self, ami_message):
        action_id = ami_message.get('ActionID')
        if action_id is None:
            if ami_message.get('Event') is None:
                bubble.log.warn(
                    "Was expecting an event from %s, got:\n%s",
                    self, ami_message)
            else:
                # It's possible that no client listen for events.
                self.send_message(ami_message, warn=False)
        else:
            action = self.redirections.get(action_id)
            # Action ID may come from another AMI tool, and be unknown here.
            if action is None:
                bubble.log.warn(
                    "Unexpected ActionID from %s, got:\n%s",
                    self, ami_message)
            else:
                action.add_message(ami_message)

    @bubble.switching
    def redirect(self, action_id, action):
        assert action_id not in self.redirections, action_id
        self.redirections[action_id] = action

    @bubble.switching
    def set_logged_in(self, success):
        if success:
            self.logged_in = True
            bubble.set_hook('ami.server.%s' % self.config.name, self)
            bubble.log.info(
                "Logged into Asterisk server %s at %s, port %d.",
                self.config.name, self.config.host, self.config.port)
        self.login.kill(block=False)

    def shutdown(self):
        bubble.set_hook('ami.server.%s' % self.config.name, None)
        if self.logged_in:
            bubble.log.info(
                "Logging off of Asterisk server %s at %s, port %d.",
                self.config.name, self.config.host, self.config.port)
            self.writer.write_ami_message(
                AMI_Message([('Action', 'Logoff')]),
                block=False)
            # FIXME: Read and check response.  Replace the above by:
            #self.Logoff().main(self, block=False)
        else:
            bubble.log.error(
                "Cannot log into Asterisk server %s at %s, port %d.",
                self.config.name, self.config.host, self.config.port)
        super(Server, self).shutdown()

    @bubble.switching
    def unredirect(self, action_id):
        del self.redirections[action_id]


class Web(bubble.Active_Bubble):
    "Serve AMI Web requests."
    name_suffix = None

    @bubble.exposed
    def application(self, environ, start_response):

        # Require a query string and a recognized content type.
        writer_conf = None
        path_info = environ.get('PATH_INFO')
        if path_info == '/json':
            writer_conf = 'json'
            content_type = 'application/json'
        elif path_info == '/manager':
            writer_conf = 'manager'
            content_type = 'text/html'
        elif path_info == '/mxml':
            writer_conf = 'mxml'
            content_type = 'text/html'
        elif path_info == '/rawman':
            writer_conf = 'rawman'
            content_type = 'text/plain'
        query_string = environ.get('QUERY_STRING')
        if writer_conf is None or query_string is None:
            start_response("404 Not found", [])
            return

        # Recover the session client or create a new one.
        cookie = Cookie.SimpleCookie(environ.get('HTTP_COOKIE'))
        try:
            session = cookie['mansession_id'].value
        except KeyError:
            client = None
        else:
            client = self.active_sessions.get(session)
        if client is None:
            session = '%.8x' % random.randint(0, (1 << 32) - 1)
            if 'REMOTE_ADDR' in environ and 'REMOTE_PORT' in environ:
                suffix = ('-web-%s:%s'
                          % (environ['REMOTE_ADDR'], environ['REMOTE_PORT']))
            else:
                suffix = '-web-' + session
            client = Client(suffix=suffix)
            self.active_sessions[session] = client
            writer = Writer(suffix=suffix, timeout=idle_client_timeout)
            client.configure(self.config, writer)

        # Plumber so the results return to the original requester.
        fragments = []
        client.writer.set_write(fragments.append)
        client.writer.configure(writer_conf)

        # Trigger the action by sending the request to the client.
        start_response(
            "200 OK", [
                ('Content-type', content_type),
                ('Cache-Control', 'no-cache, no-store'),
                ('Set-Cookie',
                 'mansession_id="%s"; Version=1; Max_Age=60' % session),
                ('Pragma', 'SuppressEvents')])
        ami_message = AMI_Message()
        for key, value in urlparse.parse_qsl(query_string):
            ami_message[key] = value
        # Login actions from the Web should have "Events: off" forced!
        if ami_message.get_lower('Action') == 'login':
            ami_message['Events'] = 'off'
        client.process_ami_message(ami_message)

        # Collect and return the results.
        yield ''.join(fragments)

    @bubble.switching
    def main(self, config):
        self.config = config
        config_web = config.clients.get('http')
        self.host = config_web.host
        self.port = config_web.port
        self.active_sessions = {}

        class Logger:

            def write(self, text):
                bubble.log.web('%s', text)

        from gevent.wsgi import WSGIServer
        server = WSGIServer((self.host, self.port),
                            self.application, log=Logger())
        bubble.log.info(
            "Listening for HTTP AMI on %s, port %d.",
            self.host, self.port)
        server.serve_forever()

    def shutdown(self):
        bubble.log.info(
            "Terminating HTTP AMI on %s, port %d.", self.host, self.port)
        for client in self.active_sessions.itervalues():
            client.writer.kill(block=False)
            client.kill(block=False)
        super(Web, self).shutdown()


class Welcomer(bubble.Active_Bubble):
    "Launch a new Client bubble for each incoming connection."
    name_suffix = None

    def bootstrap(self):
        super(Welcomer, self).bootstrap()
        self.clients = set()

    @bubble.switching
    def main(self, config):
        handle = socket.socket()
        handle.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self.config_tcp = config.clients['tcp']
        handle.bind((self.config_tcp.host, self.config_tcp.port))
        handle.listen(1)
        bubble.set_hook('ami.welcomer', self)
        bubble.log.info(
            "Listening for TCP AMI on %s, port %d.",
            self.config_tcp.host, self.config_tcp.port)

        while True:
            handle2, address = handle.accept()
            bubble.log.debug(
                "Incoming connection from %s, port %s.", *address)
            suffix = '-ami-%s:%s' % address
            writer = Writer(suffix=suffix)
            writer.configure('rawman')
            writer.set_socket(handle2)
            client = Client(suffix=suffix)
            self.clients.add(client)
            client.link(self.clients.remove)
            client.address = address
            client.configure(config, writer)
            reader = Reader(suffix=suffix)
            reader.set_socket(handle2)
            reader.forward_ami_messages(client, block=False)
            writer.add_message(welcome_prefix + welcome_version + '\r\n')

    def shutdown(self):
        bubble.log.info(
            "Terminating TCP AMI on %s, port %d.",
            self.config_tcp.host, self.config_tcp.port)
        bubble.set_hook('ami.welcomer', None)
        for client in list(self.clients):
            self.client.kill()
        super(Welcomer, self).shutdown()


class Writer(bubble.Output):
    "Output augmented with AMI specific methods."

    # When AMI_MESSAGE is exactly False, write an prologue, that is,
    # an introduction for a series of AMI messages.  If exactly True,
    # then write an epilogue, that is, a conclusion for such a series.

    ami_messages = None

    @bubble.switching
    def configure(self, format):
        "FORMAT is 'json', 'manager', 'mxml' or 'rawman'."
        self.write_ami_message = getattr(self, 'write_%s' % format)

    @bubble.switching
    def write_json(self, ami_message):
        if ami_message is False:
            self.ami_messages = []
            return ''
        if ami_message is True:
            text = json.JSONEncoder(indent=2).encode(self.ami_messages)
            self.add_message(text)
            self.ami_messages = None
            return text
        if ami_message._extra_lines is not None:
            bubble.log.error(
                "FIXME: How to JSON encode lines?\n%s",
                '\n'.join(ami_message._extra_lines))
        if self.ami_messages is None:
            # If False has not been used, True will not be either, so
            # process the message right away.
            text = json.JSONEncoder(indent=2).encode(ami_message)
            self.add_message(text)
            return text
        self.ami_messages.append(ami_message)
        return ''

    @bubble.switching
    def write_manager(self, ami_message):
        fragments = []
        write = fragments.append
        if ami_message is False:
            write(
                '<html>\n'
                '<title>Asterisk&trade; Manager Interface</title>'
                '<body bgcolor="#ffffff">\n'
                '<table align=center bgcolor="#f1f1f1" width="500">\n'
                '<tr><td colspan="2" bgcolor="#f1f1f1">'
                '<h1>Manager Tester</h1></td></tr>\n'
                '<tr><td colspan="2" bgcolor="#f1f1f1">'
                '<form action="manager" method="post">\n'
                '   Action: <select name="action">\n'
                '      <option value="">-----&gt;</option>\n'
                '      <option value="login">login</option>\n'
                '      <option value="command">Command</option>\n'
                '      <option value="waitevent">waitevent</option>\n'
                '      <option value="listcommands">listcommands</option>\n'
                '   </select>\n'
                '   or <input name="action"><br/>\n'
                '   CLI Command <input name="command"><br>\n'
                '   user <input name="username"> pass <input type="password"'
                '    name="secret"><br>\n'
                '   <input type="submit">\n'
                '</form>\n'
                '</td></tr>\n')
        elif ami_message is True:
            write('</table></body>\n'
                  '</html>\n')
        else:
            for key, value in ami_message.iteritems():
                write('<tr><td>%s</td><td>%s</td></tr>\n'
                      % (saxutils.escape(key), saxutils.escape(value)))
            if ami_message._extra_lines is not None:
                bubble.log.error(
                    "FIXME: How to Manager encode lines?\n%s",
                    '\n'.join(ami_message._extra_lines))
            write('<tr><td colspan="2"><hr></td></tr>\n')
        self.add_message(''.join(fragments))

    @bubble.switching
    def write_mxml(self, ami_message):
        fragments = []
        write = fragments.append
        if ami_message is False:
            write('<ajax-response>\n')
        elif ami_message is True:
            write('</ajax-response>\n')
        else:
            write('<response type=\'object\' id=\'unknown\'>\n')
            line = '   <generic'
            for key, value in ami_message.iteritems():
                fragment = ' %s=\'%s\'' % (
                    saxutils.escape(key.lower()),
                    saxutils.escape(value).replace('\'', '&apos;'))
                line2 = line + fragment
                if len(line2) > 79:
                    write(line + '\n')
                    line = '           ' + fragment
                else:
                    line = line2
            fragment = ' />'
            line2 = line + fragment
            if len(line2) > 79:
                write(line + '\n')
                line = '           ' + fragment
            else:
                line = line2
            write(line + '\n')
            if ami_message._extra_lines is not None:
                bubble.log.error(
                    "FIXME: How to MXML encode lines?\n%s",
                    '\n'.join(ami_message._extra_lines))
            write('</response>\n')
        self.add_message(''.join(fragments))

    @bubble.switching
    def write_rawman(self, ami_message):
        if not isinstance(ami_message, bool):
            self.add_message(ami_message.encode())


def introspect():
    import asterisk
    import internal
    for key in set(asterisk.manager_actions) | set(internal.manager_actions):
        bases = []
        base = asterisk.manager_actions.get(key)
        if base is not None:
            bases.append(base)
        base = internal.manager_actions.get(key)
        if base is not None:
            bases.append(base)
        bases.append(Manager_Action)
        assert key.lower() not in canonical_action, key
        canonical_action[key.lower()] = key
        manager_actions[key] = type('*' + key, tuple(bases), {})

introspect()
