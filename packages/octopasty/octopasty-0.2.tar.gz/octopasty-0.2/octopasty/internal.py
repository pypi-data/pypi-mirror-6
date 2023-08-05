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
Base AMI actions getting special Octopasty processing.
"""

__metaclass__ = type

import hashlib
import random
from gevent import socket
import struct

import ami
import bubble

# From Manager_Action name to Manager_Action subclass.
manager_actions = {}


class Manager_Action:
    "Base for all manager actions bubbles."
    # This base class is merely used for finding derived classes in
    # this module.  The real Manager_Action base sits in the ami.py
    # module and gets mixed in, see it for default fields and methods.


class Octopasty_Action(Manager_Action):
    "Octopasty actions are only visible to users with octopasty privileges."
    privileges = 'all', 'octopasty'


class Challenge(Manager_Action):
    "Generate Challenge for MD5 Auth."
    name = 'Challenge'
    need_prior_login = False

    def broadcast(self, client, ami_message, server_names):

        if client.user is not None:
            bubble.log.user("Already authenticated.")
            return ami.AMI_Message([
                ('Response', 'Success'),
                ('Message', "Already authenticated")])

        if ami_message.get_lower('AuthType') != 'md5':
            bubble.log.user("Authentication type not supported.")
            return ami.AMI_Message([
                ('Response', 'Error'),
                ('Message', "Authentication type not supported")])

        client.challenge = str(random.randint(100000000, 999999999))
        return ami.AMI_Message([
            ('Response', 'Success'),
            ('Challenge', client.challenge)])


class IAXpeers(Manager_Action):
    "List IAX peers."
    name = 'IAXpeers'
    privileges = 'system', 'reporting', 'all'

    # Grrr!  https://issues.asterisk.org/jira/browse/ASTERISK-15880
    # My feeling is that, despite said "corrected", the only correction
    # is the addition of the closing message, as the intermediate events
    # still miss the ActionID.  So. the code below cannot work.

    # FIXME: IAXpeerlist also needs special processing.

    def aggregate(self, replies):
        results = [ami.AMI_Message([
            ('Response', 'Success'),
            ('EventList', 'start'),  # Note: lower-case "s"
            ('Message', 'Peer status list will follow')])]
        for name, ami_messages in replies.iteritems():
            if len(ami_messages) < 2:
                bubble.log.error(
                    "From %s, IAXpeers action reply is too short", name)
                continue
            if ami_messages[0].get('Response') != 'Success':
                bubble.log.error(
                    "From %s, IAXpeers action failed", name)
                continue
            if ami_messages[-1].get('Event') != 'PeerlistComplete':
                bubble.log.error(
                    "From %s, IAXpeers events do not complete", name)
                continue
            value = ami_messages[-1].get('ListItems')
            if not (value and value.isdigit()
                    and int(value) == len(ami_messages) - 2):
                bubble.log.error(
                    "From %s, IAXpeersComplete has invalid ListItems", name)
                continue
            results += ami_messages[1:-1]
        results.append(ami.AMI_Message([
            ('Event', 'PeerlistComplete'),
            ('EventList', 'Complete'),  # Note: upper-case "C".
            ('ListItems', str(len(results) - 1))]))
        return results

    def broadcast(self, client, ami_message, server_names):
        return server_names

    def is_last(self, ami_message):
        return ami_message.get('Event') == 'PeerlistComplete'


class ListCommands(Manager_Action):
    "List available manager commands."
    name = 'ListCommands'

    def broadcast(self, client, ami_message, server_names):
        accepting = set()
        for name in server_names:
            server = ami.Server.registry.get(name)
            if server:
                accepting |= set(server.accepting)
        response = ami.AMI_Message([('Response', 'Success')])
        has_octopasty = 'octopasty' in client.user.privileges
        for key, maker in sorted(ami.manager_actions.items()):
            if not (issubclass(maker, Manager_Action)
                    or maker in accepting):
                continue
            privileges = maker.privileges
            # Actions with octopasty among privileges are invisible,
            # save for user having octopasty privilege.
            if privileges is not None and 'octopasty' in privileges:
                if not has_octopasty:
                    continue
            response[maker.name] = (
                '%s  (Priv: %s)'
                % (maker.summary,
                   # Looking like Asterisk even where it is wrong :-).
                   ','.join(privileges) if privileges else '<none>'))
        return response


class Login(Manager_Action):
    "Login Manager."
    name = 'Login'
    need_prior_login = False

    class Events_Forwarder(bubble.Reactive_Bubble):
        "Copy random events to the user."
        accepted_types = ami.AMI_Message
        daemon = True

        @bubble.switching
        def configure(self, event_filter, writer):
            self.event_filter = event_filter
            self.writer = writer
            writer.link(self._suicide)

        def do_AMI_Message(self, ami_message):
            "Copy random events to the user."
            event = ami_message.get_lower('Event')
            if event is None:
                bubble.log.warn(
                    "Was expecting an event from %s, got:\n%s",
                    self.envelope.sender, ami_message)
            elif self.event_filter is None or event in self.event_filter:
                self.writer.write_ami_message(ami_message, block=False)
                bubble.log.event(
                    "From server %s:\n%s",
                    self.envelope.sender.server_config.name, ami_message)
            else:
                bubble.log.debug("Filtered out event:\n%s", ami_message)

    def broadcast(self, client, ami_message, server_names):

        def deny(diagnostic):
            bubble.log.user("Login failed: %s.", diagnostic)
            return ami.AMI_Message([
                ('Response', 'Error'),
                ('Message', "Authentication refused")])

        # Validate login.
        if client.user is not None:
            bubble.log.user("Already authenticated.")
            return ami.AMI_Message([
                ('Response', 'Success'),
                ('Message', "Already authenticated")])
        username = ami_message.get('Username')
        user = client.config.users.get(username)
        if user is None:
            return deny("Unknown username.")
        secret = ami_message.get('Secret')
        password = user.password
        if client.challenge is None:
            if (hashlib.md5(secret).hexdigest() != password
                    and hashlib.sha1(secret).hexdigest() != password):
                return deny("Password does not match.")
        elif hashlib.md5(client.challenge + secret) != password:
            return deny("Challenge was not successful.")
        if not (client.address is None or user.acl is None):
            for check, mask in user.acl:
                ip = struct.unpack(
                    '!I', socket.inet_ntoa(client.address))[0]
                if (ip ^ check) & mask == 0:
                    break
            else:
                return deny("Access not allowed from this IP.")

        # Listen to random events from all servers; launch them as needed.
        show_events = ami_message.get_lower('Events') != 'off'
        if show_events:
            events_forwarder = self.Events_Forwarder(suffix=None)
            events_forwarder.configure(user.event_filter, client.writer)
        client.server_names = []
        for name in user.servers:
            server = ami.Server.registry.get(name)
            if server is None:
                server = ami.Server()
                if show_events:
                    server.add_to_output_bus(events_forwarder)
                server.configure(client.config.servers[name])
                # FIXME: What if Asterisk refuses to reply?
            elif show_events:
                server.add_to_output_bus(events_forwarder)
            client.server_names.append(name)

        # Login is successful!
        client.user = user
        bubble.log.info("%s logged in user %s.", client, user.name)
        return ami.AMI_Message([
            ('Response', 'Success'),
            ('Message', "Authentication accepted")])


class Logoff(Manager_Action):
    "Logoff Manager."
    name = 'Logoff'

    def broadcast(self, client, ami_message, server_names):
        # Asterisk would use:
        #message = "Thanks for all the fish."
        # Octopasty prefers:
        message = "Don't panic."
        return ami.AMI_Message([('Response', 'Goodbye'),
                                ('Message', message)])


class QueueStatus(Manager_Action):
    "Show queue status."
    name = 'QueueStatus'

    def aggregate(self, replies):
        results = [ami.AMI_Message([
            ('Response', 'Success'),
            ('Message', 'Channel status will follow')])]
        for name, ami_messages in replies.iteritems():
            if len(ami_messages) < 2:
                bubble.log.error(
                    "From %s, QueueStatus action reply is too short", name)
                continue
            if ami_messages[0].get('Response') != 'Success':
                bubble.log.error(
                    "From %s, QueueStatus action failed", name)
                continue
            if ami_messages[-1].get('Event') != 'QueueStatusComplete':
                bubble.log.error(
                    "From %s, QueueStatus events do not complete", name)
                continue
            results += ami_messages[1:-1]
        results.append(ami.AMI_Message([('Event', 'QueueStatusComplete')]))
        return results

    def broadcast(self, client, ami_message, server_names):
        return server_names

    def is_last(self, ami_message):
        return ami_message.get('Event') == 'QueueStatusComplete'


class Status(Manager_Action):
    "List channel status."
    name = 'Status'
    privileges = 'system', 'call', 'reporting', 'all'

    def aggregate(self, replies):
        results = [ami.AMI_Message([
            ('Response', 'Success'),
            ('Message', 'Channel status will follow')])]
        for name, ami_messages in replies.iteritems():
            if len(ami_messages) < 2:
                bubble.log.error(
                    "From %s, Status action reply is too short", name)
                continue
            if ami_messages[0].get('Response') != 'Success':
                bubble.log.error(
                    "From %s, Status action failed", name)
                continue
            if ami_messages[-1].get('Event') != 'StatusComplete':
                bubble.log.error(
                    "From %s, Status events do not complete", name)
                continue
            value = ami_messages[-1].get('Items')
            if not (value and value.isdigit()
                    and int(value) == len(ami_messages) - 2):
                bubble.log.error(
                    "From %s, StatusComplete has invalid Items", name)
                continue
            results += ami_messages[1:-1]
        results.append(ami.AMI_Message([
            ('Event', 'StatusComplete'),
            ('Items', str(len(results) - 1))]))
        return results

    def broadcast(self, client, ami_message, server_names):
        return server_names

    def is_last(self, ami_message):
        return ami_message.get('Event') == 'StatusComplete'


def introspect():
    abstracts = Manager_Action, Octopasty_Action
    for abstract in abstracts:
        for value in abstract.__subclasses__():
            if value not in abstracts:
                manager_actions[value.__name__] = value

introspect()
