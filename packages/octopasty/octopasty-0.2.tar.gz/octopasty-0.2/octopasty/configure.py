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
Configuration structures and actions.
"""

__metaclass__ = type

from gevent import socket
import struct
import os
import sys
import yaml


def study_config(args_config, default=None):
    "Return merged YAML configuration, and initial AMI files."
    ami_files = []
    config_files = []
    for directory in ('.', os.getenv('HOME'),
                      '/usr/local/etc', '/etc'):
        for base in '%s.ami' % default, '.%s.ami' % default:
            name = os.path.join(directory, base)
            if os.path.exists(name):
                name = os.path.realpath(name)
                if name not in config_files:
                    ami_files.append(name)
        for base in '%s.yaml' % default, '.%s.yaml' % default:
            name = os.path.join(directory, base)
            if os.path.exists(name):
                name = os.path.realpath(name)
                if name not in config_files:
                    config_files.append(name)
    if args_config:
        # If any -C, completely ignore config files.
        config_files = args_config
    elif not config_files:
        sys.exit("* No configuration file found.")
    return yaml_merge(config_files), ami_files


def yaml_merge(filenames):
    "Turn one or more YAML files into a single Config instance."

    def subconfig(maker, block):
        result = maker()
        for key, value in block.iteritems():
            result.set(key, value)
        result.final_check()
        return result

    config = Config()
    try:
        for filename in filenames:
            yaml_info = yaml.load(open(filename))
            # FIXME: Valider la structure du fichier YAML elle-même.
            for section, blocks in yaml_info.iteritems():
                if section == 'clients':
                    for block in blocks:
                        client = subconfig(Client_Config, block)
                        if client.name in config.clients:
                            raise ConfigError(
                                "Duplicate client `%s'." % client.name)
                        config.clients[client.name] = client
                elif section == 'servers':
                    for block in blocks:
                        server = subconfig(Server_Config, block)
                        if server.name in config.servers:
                            raise ConfigError(
                                "Duplicate server `%s'." % server.name)
                        config.servers[server.name] = server
                elif section == 'users':
                    for block in blocks:
                        user = subconfig(User_Config, block)
                        if user.name in config.users:
                            raise ConfigError(
                                "Duplicate user `%s'." % user.name)
                        config.users[user.name] = user
                elif section == 'plugins':
                    for block in blocks:
                        plugin = subconfig(Plugin_Config, block)
                        if plugin.plugin in config.plugins:
                            raise ConfigError(
                                "Duplicate plugin `%s'." % plugin.plugin)
                        config.plugins[plugin.plugin] = plugin
                else:
                    raise ConfigError("Unknown section `%s'." % section)
        config.final_check()
    except ConfigError, exception:
        sys.exit('* ' + str(exception))
    return config


class _Config:
    "Base class for *_Config classes, providing common methods."
    name = None

    def __repr__(self):
        text = type(self).__name__.lower().replace('_', ' ')
        if self.name is not None:
            text = self.name + ' ' + text
        return text

    def _set_host(self, value):
        self.check_type('host', value, str)
        self.host = value

    def _set_port(self, value):
        if isinstance(value, str):
            if not value.isdigit():
                raise ConfigError("Invalid port `%s' in %r." % (value, self))
            value = int(value)
        self.check_type('port', value, int)
        if not 0 < value < 1 << 16:
            raise ConfigError("Invalid port `%s' in %r." % (value, self))
        self.port = value

    # To signal that a key needs a value, with no default.
    MUST = object()

    def check_type(self, key, value, types):
        "Check that KEY's VALUE's type is among TYPES."
        if not isinstance(value, types):
            self.invalid_value(key, value)

    def final_check(self):
        "Check that the configuration is consistent.  To be overriden."

    def final_set_default(self, **kws):
        "From KWS, add default values for still undefined attributes."
        for key, value in kws.iteritems():
            if getattr(self, key) is None:
                if value is self.MUST:
                    raise ConfigError("Missing key %s in %r." % (key, self))
                self.set(key, value)

    def invalid_value(self, key, value):
        "Report that KEY's VALUE is invalid."
        raise ConfigError("Invalid %s value %r in %r."
                          % (key, value, self))

    def set(self, key, value):
        "Use the set_KEY method for adapting and saving VALUE into KEY."
        method = getattr(self, 'set_' + key, None)
        if method is None:
            raise ConfigError("Unexpected key %s in %s." % (key, self))
        if getattr(self, key, None) is not None:
            raise ConfigError("Duplicate key %s in %s." % (key, self))
        method(value)


class Config:
    "Main configuration, holding subconfigurations together."

    def __init__(self):
        self.clients = {}
        self.servers = {}
        self.users = {}
        self.plugins = {}

    def final_check(self):
        if self.clients.get('tcp') is None:
            self.clients['tcp'] = Client_Config()
            self.clients['tcp'].name = 'tcp'
            self.clients['tcp'].final_check()
        if not self.servers:
            raise ConfigError("`servers:' section is missing or empty.")
        # FIXME: Commented so pasty starts.  Should not be for opasty.
        #if not self.users:
        #    raise ConfigError("`users:' section is missing or empty.")

        # Check that user servers all have a server configuration.
        for user in self.users.itervalues():
            for server in user.servers:
                if server not in self.servers:
                    raise ConfigError(
                        "Unknown server %s in %r." % (server, user))


class ConfigError(Exception):
    "Configuration error."


class Client_Config(_Config):
    host = None
    name = None
    port = None
    timeout = None

    def final_check(self):
        self.final_set_default(
            host='127.0.0.1', name=self.MUST,
            port=5038 if self.name == 'tcp' else self.MUST)
        if self.name not in ('backdoor', 'http', 'tcp'):
            raise ConfigError("Invalid client name %r in %r."
                              % (self.name, self))

    def set_host(self, value):
        self._set_host(value)

    def set_name(self, value):
        self.check_type('name', value, str)
        self.name = value

    def set_port(self, value):
        self._set_port(value)

    def set_timeout(self, value):
        if isinstance(value, str):
            if not value.isdigit():
                raise ConfigError("Invalid timeout `%s' in %r."
                                  % (value, self))
            value = int(value)
        self.check_type('timeout', value, int)
        self.timeout = value


class Plugin_Config(_Config):
    plugin = None

    def __repr__(self):
        text = type(self).__name__.lower().replace('_', ' ')
        if self.plugin is not None:
            text = self.plugin + ' ' + text
        return text

    def final_check(self):
        self.final_set_default(plugin=self.MUST)
        self.check_type('plugin', self.plugin, str)

    def set(self, key, value):
        setattr(self, key, value)


class Server_Config(_Config):
    host = None
    name = None
    password = None
    port = None
    readonly = None
    username = None

    def final_check(self):
        self.final_set_default(host=self.MUST, name=self.MUST,
                               password=self.MUST, port=5038,
                               readonly=False, username=self.MUST)

    def set_host(self, value):
        self._set_host(value)

    def set_name(self, value):
        self.check_type('name', value, str)
        self.name = value

    def set_port(self, value):
        self._set_port(value)

    def set_password(self, value):
        self.check_type('password', value, str)
        self.password = value

    def set_readonly(self, value):
        if isinstance(value, str):
            value = value.lower() in ('true', 'yes')
        self.check_type('readonly', value, bool)
        self.readonly = value

    def set_username(self, value):
        self.check_type('username', value, str)
        self.username = value


class User_Config(_Config):
    accountcode = None
    acl = None
    action_filter = None
    event_filter = None
    name = None
    password = None
    privileges = None
    servers = None

    def final_check(self):
        self.final_set_default(name=self.MUST, password=self.MUST,
                               privileges=['all'], servers=self.MUST)
        if not hasattr(self, 'accountcode'):
            self.accountcode = self.name

    def set_accountcode(self, value):
        self.check_type('accountcode', value, str)
        self.accountcode = value

    def set_acl(self, value):
        if isinstance(value, str):
            value = value.replace(' ', '').split(',')
        self.check_type('acl', value, list)
        pairs = []
        for fragment in value:
            if not isinstance(fragment, str):
                raise ConfigError("Invalid acl fragment %r in %r."
                                  % (fragment, self))
            if '/' in fragment:
                fragment, rest = fragment.split('/', 1)
                try:
                    size = int(rest)
                except ValueError:
                    raise ConfigError("Invalid acl mask size %r in %r."
                                      % (rest, self))
                if not 0 <= size <= 32:
                    raise ConfigError("Invalid acl mask size %r in %r."
                                      % (size, self))
            else:
                size = 32
            try:
                text = socket.inet_aton(fragment)
            except socket.error:
                raise ConfigError("Invalid acl IP address %r in %r."
                                  % (fragment, self))
            check = struct.unpack('!I', text)[0]
            mask = (1 << 32) - (1 << 32 - size)
            pairs.append((check, mask))
        self.acl = pairs

    def set_action_filter(self, value):
        if isinstance(value, str):
            value = value.replace(' ', '').split(',')
        self.check_type('action_filter', value, list)
        self.action_filter = value

    def set_event_filter(self, value):
        if isinstance(value, str):
            value = value.replace(' ', '').split(',')
        self.check_type('event_filter', value, list)
        self.event_filter = value

    def set_name(self, value):
        self.check_type('name', value, str)
        self.name = value

    def set_password(self, value):
        self.check_type('passowrd', value, str)
        self.password = value

    def set_privileges(self, value):
        if isinstance(value, str):
            value = value.replace(' ', '').split(',')
        self.check_type('privileges', value, list)
        self.privileges = value

    def set_servers(self, value):
        if isinstance(value, str):
            value = value.replace(' ', '').split(',')
        self.check_type('servers', value, list)
        self.servers = value
