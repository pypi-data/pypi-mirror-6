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

# Organizing and starting the Octopasty application.

"""\
Octopasty is an Asterisk AMI proxy.

Usage:
  opasty [-hV] | --help | --version
  opasty [-C FILE...] [-p PID] [-l SPEC...]
         [-d] [-t HOOK...] [-A AMIFILE...] [-P SPEC]

Options:
  -h, --help             Show this help message and exit.
  -V, --version          Show version numbers.
  -C, --config FILE...   Use FILE for configuration.
  -p, --pid PID          File to receive the process ID.
  -l, --log SPEC...      Log many things according to SPEC.
  -d, --debug            Activate message trace (very verbose).
  -t, --trace HOOK...    Automatically trace according to HOOK pattern.
  -A, --amifile FILE...  Do initial AMI messages (`-' for standard input).
  -P, --plugins SPEC     Plugins to activate (if not given, activate all).

Options -AClt may all accept more than one value.  Each SPEC is FLAGS:FILE.
FLAGS is a comma separated list of symbols among: action, debug, error, event,
info, warn, and maybe others; if FLAGS: is not given, everything is assumed.
If FILE is not given, standard error is assumed. See the Octopasty manual for
the glorious details.
"""

__metaclass__ = type

from gevent import monkey
monkey.patch_socket()
monkey.patch_ssl()

import os
import pkg_resources
import sys

import ami
import bubble
import configure
# FIXME: Unnice mix of absolute and relative imports.
from octopasty import __version__


class Main:

    def main(self):
        bubble.bootstrap()
        try:
            self.real_main()
        except SystemExit:
            pass
        except:
            bubble.log._set_logger(bubble.rug_logger)
            import StringIO
            import traceback
            buffer = StringIO.StringIO()
            traceback.print_exc(file=buffer)
            bubble.log.error('%s', buffer.getvalue())
        finally:
            bubble.shutdown()

    def real_main(self):

        # Decode options.
        import docopt
        args = docopt.docopt(__doc__, version=__version__)

        # Save our process ID.
        if args['--pid'] is not None:
            try:
                pid = int(file(args['--pid']).read().strip())
                os.kill(pid, 0)
            except (IOError, OSError, ValueError):
                file(args['--pid'], 'w').write('%d\n' % os.getpid())
            else:
                sys.exit("Program with PID %d is still running!" % pid)

        # Put everything in motion.
        try:
            self.bootstrap_all(args)

            # Accept external connections to create more clients.
            if 'http' in self.config.clients:
                self.web = ami.Web()
                self.web.main(self.config, block=False)
            if 'tcp' in self.config.clients:
                self.welcomer = ami.Welcomer()
                self.welcomer.main(self.config, block=False)

            # Bootstrap plugins.
            for entry in pkg_resources.iter_entry_points('OctoPlugin'):
                if self.within_plugins_spec(entry, 'bootstrap'):
                    bubble.log.info("Activating plugin %s", entry)
                    entry.load()(self.config)

            # Block until interrupted.
            if self.web is not None:
                self.web.join()
            if self.welcomer is not None:
                self.welcomer.join()

        # Shutdown all.
        except KeyboardInterrupt:
            self.output.write('\n')
            self.shutdown_all()

        # Unsave our process ID.
        finally:
            if args['--pid'] is not None:
                os.remove(args['--pid'])

    def bootstrap_all(self, args):
        self.writer = None
        self.internal = None
        self.web = None
        self.welcomer = None

        if args['--log']:
            log_specs = args['--log']
        else:
            log_specs = ['info,warn,error:']

        if args['--plugins'] is None:
            self.plugins_spec = None
        else:
            self.plugins_spec = args['--plugins'].split(',')

        self.config, ami_files = configure.study_config(
            args['--config'], 'opasty')
        self.output = bubble.get_hook('preset.output')
        self.output.set_write(sys.stderr.write)
        self.bootstrap_logs(log_specs)

        bubble.log.info("Bootstrapping opasty (as from Octopasty %s)."
                        % __version__)
        config_backdoor = self.config.clients.get('backdoor')
        if config_backdoor:
            bubble.get_hook('preset.backdoor').start_server(
                config_backdoor.host, config_backdoor.port)
        if args['--debug']:
            bubble.set_trace()
        elif args['--trace']:
            for trace in args['--trace']:
                bubble.trace_hook(trace)

        # Prepare an internal client, feed it with initial AMI messages.

        def log_internal(text):
            bubble.log.event('\n%s', text.replace('\r', ''))

        self.writer = ami.Writer(suffix='-opasty')
        self.writer.configure('rawman')
        self.writer.set_write(log_internal)
        self.internal = ami.Client(suffix='-opasty')
        self.internal.configure(self.config, self.writer)
        for ami_file in ami_files + (args['--amifile'] or []):
            bubble.log.user("Reading %s …", ami_file)
            reader = ami.Reader()
            reader.set_file(open(ami_file))
            reader.forward_ami_messages(self.internal)
            reader.kill(block=False)
            bubble.log.user("Reading %s … done!", ami_file)

    def bootstrap_logs(self, log_specs):
        "Setup all AMI logs according to saved options."
        self.log_instances = []
        self.output_instances = []

        for spec in log_specs:

            # Decode the spec.
            if ':' in spec:
                flag, name = spec.split(':', 1)
                if flag:
                    if flag.isdigit():
                        mask = int(flag)
                    else:
                        mask = 0
                        for symbol in flag.split(','):
                            mask |= 1 << getattr(bubble.log, symbol).category
                else:
                    mask = None
            else:
                mask = None
                name = spec

            # Prepare needed bubbles.
            if name:
                self.output = bubble.Output(suffix='-opasty')
                self.output.set_file(open(name, 'a'), 1)
                self.output_instances.append(self.output)
            else:
                self.output = bubble.get_hook('preset.output')
            logger = bubble.Logger(suffix='-opasty')
            logger.set_options(mask=mask)
            logger.add_to_output_bus(self.output)
            self.log_instances.append(logger)

        if len(self.log_instances) == 1:
            logger = self.log_instances[0]
            logger.name_suffix = None
            bubble.log._set_logger(logger)
        else:
            log_forwarder = ami.Log_Forwarder(suffix='-opasty')
            for logger in self.log_instances:
                log_forwarder.add_to_output_bus(logger)
            self.log_instances.append(log_forwarder)
            bubble.log._set_logger(log_forwarder)

    def shutdown_all(self):
        bubble.log.info("Shutting down opasty (as from Octopasty %s)."
                        % __version__)
        if self.web is not None:
            self.web.kill()
        if self.welcomer is not None:
            self.welcomer.kill()
        for server in ami.Server.registry.values():
            server.kill()
        if self.internal is not None:
            self.internal.kill()

        # Shutdown plugins.
        for entry in pkg_resources.iter_entry_points('OctoPlugin'):
            if self.within_plugins_spec(entry, 'shutdown'):
                bubble.log.info("Deactivating plugin %s", entry)
                entry.load()(self.config)

        bubble.set_trace(False)
        self.shutdown_logs()

    def shutdown_logs(self):
        "Exit all AMI logs, in reverse order they were created."
        bubble.log._set_logger(bubble.rug_logger)
        while self.log_instances:
            self.log_instances.pop().kill()
        while self.output_instances:
            self.output_instances.pop().kill()

    def within_plugins_spec(self, entry, suffix):
        if entry.name == suffix:
            return True
        if not entry.name.endswith('_' + suffix):
            return False
        if self.plugins_spec is None:
            return True
        return entry.name[: - (len(suffix) + 1)] in self.plugins_spec


run = Main()
main = run.main

if __name__ == '__main__':
    main()
