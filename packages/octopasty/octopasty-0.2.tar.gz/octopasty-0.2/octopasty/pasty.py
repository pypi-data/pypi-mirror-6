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

# Pasty is an Asterisk AMI user interface.

"""\
User convenience tool for connecting to an AMI.

Usage:
  pasty [-hV] | --help | --version
  pasty [-A AMIFILE...] [-C FILE...]

Options:
  -h, --help           Show this help message and exit.
  -V, --version        Show version numbers.
  -C, --config FILE    Use FILE for configuration.
  -A, --amifile FILE   Do initial AMI messages from FILE.

Options -A and -C may be repeated.  Option -A is currently ignored.
"""

# This program would likely have been just another Bubble within
# Octopasty and the normal way to interact with it from standard
# input.  However, gevent does not properly handle standard input,
# which defeats it all.  So, I had no choice than making this a
# separate program, which use big threads instead of gevents.

__metaclass__ = type

import os
import readline
import socket
import sys

from octopasty import __version__
import ami

# ANSI colors.
_ESC = '\x1b'
NORMAL = _ESC + '[0m'
DOCUM = _ESC + '[36m'
PROMPT = _ESC + '[1;37m'
RULER = _ESC + '[35m'
WARNING = _ESC + '[1;33m'
ERROR = _ESC + '[1;31m'

# FIXME: Configure key bindings, colors, history file, AMI messages sent, etc.


class Main:
    "Main class and entry point."

    # The program uses three threads.  The main thread takes care of
    # the user interaction at the terminal and sends ready AMI
    # messages to the Asterisk server.  Another thread reads the
    # incoming AMI messages from the Asterisk server, unloading the
    # socket, and queues them away for the last thread.  The last
    # thread tries to find time slots where the user terminal is free
    # enough to echo received AMI messages without overly disrupting
    # the typing user.

    def main(self, *arguments):

        # Decode options.
        import docopt
        args = docopt.docopt(__doc__, version=__version__)

        # Read the configuration and establish contact.
        import configure
        config, ami_files = configure.study_config(args['--config'], 'pasty')
        self.handle = socket.socket()
        config_tcp = config.clients['tcp']
        self.handle.connect((config_tcp.host, config_tcp.port))
        sending = self.handle.makefile('w', 0)

        # Prepare to echo whatever Asterisk sends.
        import Queue
        self.accumulated = Queue.Queue()
        import threading
        self.terminal_lock = threading.Lock()
        self.write("Pasty (as from Octopasty %s) on %s, port %s.\n\n"
                   % (__version__, config_tcp.host, config_tcp.port))
        echoing = threading.Thread(target=self.echoing)
        echoing.daemon = True
        echoing.start()
        receiving = threading.Thread(target=self.receiving)
        receiving.daemon = True
        receiving.start()

        # Feed in our configuration AMI files.
        for name in ami_files:
            sending.write(open(name).read())

        # Let the user interact.
        terminal = Terminal()
        terminal.main(sending)
        self.write("\nPasty terminated.\n")

    def echoing(self):
        while True:
            self.write(self.accumulated.get())

    def locked_input(self, prompt):
        self.terminal_lock.acquire()
        value = raw_input(prompt)
        self.terminal_lock.release()
        return value

    def moan(self, text):
        self.write("%s* %s%s\n" % (WARNING, text, NORMAL))

    def receiving(self):
        lines = []
        for line in self.handle.makefile():
            #line = line.replace('\r', '')
            lines.append(line)
            if not line.rstrip():
                self.accumulated.put(''.join(lines))
                lines = []

    def write(self, text):
        self.terminal_lock.acquire()
        sys.stdout.write(text)
        self.terminal_lock.release()


class Completer:
    "Generic completer for Octopasty, forgiving on capitalization."

    def __init__(self, keys):
        self.keys = dict((key.lower(), key) for key in keys)

    def complete(self, text, state):
        if state == 0:
            self.hypotheses = []
            extend = None
            text_lower = text.lower()
            for key in self.keys:
                if key.startswith(text_lower):
                    self.hypotheses.append(self.keys[key])
                    rest = self.keys[key][len(text):]
                    if extend is None:
                        extend = rest
                    else:
                        while extend and not rest.startswith(extend):
                            extend = extend[:-1]
            if extend:
                readline.insert_text(extend)
                return
        if state < len(self.hypotheses):
            return self.hypotheses[state]


class Terminal:
    "Terminal User Interface."

    def main(self, sending):

        # Say hello!
        run.write(
            '%s%s>%s\n%s%s%s<%s\n'
            % (RULER, '-' * 70, NORMAL,
               documentation(
                   "Use Enter to start preparing a new AMI message."
                   " When prompted for a key value, use Enter without a"
                   " value to ignore that key" " (yet Action: may not be"
                   " ignored)."
                   " Once all fields have been prompted for, the ready"
                   " AMI message is echoed, and you get a last chance to"
                   " replace or add keys by typing lines in full."
                   " You then send the message by issuing Enter on an"
                   " empty line.\n"
                   '\n'
                   "When prompted for a value, use TAB once for completing"
                   " as much as possible and twice to see available choices."
                   " Typed values are often added to available completions."
                   " Also use arrows or C-p / C-n to navigate, and C-r to"
                   " search."),
                   RULER, '-' * 70, NORMAL))

        # Get back the history, and restore multi-lines.
        readline.parse_and_bind('tab: complete')
        history = os.path.expanduser('~/.pasty-history')
        if os.path.exists(history):
            readline.read_history_file(history)
        for index in range(0, readline.get_current_history_length()):
            text = readline.get_history_item(index + 1)
            if '\\r\\n' in text:
                readline.replace_history_item(
                    index, text.replace('\\r\\n', '\n'))

        # Make sure history is saved, while protecting multi-lines.

        def rewrite_history(history):
            for index in range(readline.get_current_history_length()):
                text = readline.get_history_item(index + 1)
                if '\n' in text:
                    readline.replace_history_item(
                        index, text.replace('\n', '\\r\\n'))
            readline.write_history_file(history)

        import atexit
        atexit.register(rewrite_history, history)

        try:
            while True:
                # Wait until the user is ready and types Enter.
                history_mark = readline.get_current_history_length()
                text = raw_input()
                if text:
                    # We assume that a previous action has been recalled.
                    run.write('\n')
                    sending.write(text.replace('\n', '\r\n') + '\r\n\r\n')
                    continue

                # Prompt for the action.
                ami_message = ami.AMI_Message()
                text = manager_keys['Action'].read(ami_message)
                text2 = ami.canonical_action.get(text.lower())

                # If action is known, prompt with all AMI message keys.
                if text2 is not None:
                    action = manager_actions.get(text2)
                    text = ('%s%s>%s\n%s'
                            % (RULER, '-' * 70, NORMAL,
                               documentation(action.summary)))
                    if action.description:
                        text += '\n' + documentation(action.description)
                    run.write(text)
                    for pair in action.keys:
                        if isinstance(pair, tuple):
                            key, docum = pair
                            run.write('\n' + documentation(docum))
                        else:
                            key = pair
                        key.read(ami_message)
                    run.write('%s%s<%s\n%s\n'
                              % (RULER, '-' * 70, NORMAL,
                                 ami_message.encode().rstrip()))

                # Give the user a last opportunity to edit the message.
                while True:
                    line = raw_input().strip()
                    if not line:
                        break
                    if ':' in line:
                        key, value = line.split(':', 1)
                        ami_message[key] = value
                    else:
                        run.moan("Missing colon in line.")

                # Send the AMI message.  Reply will display asynchronously.
                text = ami_message.encode()
                sending.write(text)

                # Only retain the full AMI message in the history.
                mark = readline.get_current_history_length()
                while mark > history_mark:
                    mark -= 1
                    readline.remove_history_item(mark)
                readline.add_history(text.replace('\r', '').rstrip())

        # Terminate the program.
        except KeyboardInterrupt:
            run.write('\n')


def documentation(text):
    import textwrap
    fragments = []
    write = fragments.append
    write(DOCUM)
    for paragraph in text.rstrip().split('\n'):
        write(textwrap.fill(paragraph))
        write('\n')
    write(NORMAL)
    return ''.join(fragments)


### AMI Message Keys.

# From manager_key name to Manager_Key subclass.
manager_keys = {}


class Manager_Key:

    @classmethod
    def read(this, ami_message):
        if this.fixed is None:
            if this.previous is None:
                this.previous = set()
            choices = this.previous
        else:
            choices = this.fixed
        for name in this.each_name():
            readline.set_completer(Completer(choices).complete)
            while True:
                value = run.locked_input('%s%s:%s ' % (PROMPT, name, NORMAL))
                diagnostic = this.validate(ami_message, value)
                if diagnostic is None:
                    break
                run.moan(diagnostic)
            if not value:
                break
            if this.fixed is None:
                this.previous.add(value)
            # FIXME: Recover capitalization from CHOICES.
            ami_message[name] = value
            return value


class Action(Manager_Key):
    # FIXME: QueueS TAB -> Queue (on recule!)

    @classmethod
    def read(this, ami_message):
        name = this.name
        if this.previous is None:
            this.previous = set()
            for action in manager_actions.itervalues():
                this.previous.add(action.name)
        readline.set_completer(Completer(this.previous).complete)
        while True:
            value = run.locked_input('%s%s:%s ' % (PROMPT, name, NORMAL))
            if value:
                break
        value2 = ami.canonical_action.get(value.lower())
        if value2 is None:
            this.previous.add(value)
        else:
            value = value2
        ami_message[name] = value
        return value


class ActionID(Manager_Key):
    # This is of no interest interactively, so ignore it.

    @classmethod
    def read(this, ami_message):
        pass


class AuthType(Manager_Key):

    @classmethod
    def read(this, ami_message):
        value = 'MD5'
        ami_message[this.name] = value
        return value


class Secret(Manager_Key):

    @classmethod
    def read(this, ami_message):
        name = this.name
        import getpass
        ami_message[name] = getpass.getpass(
            '%s%s:%s ' % (PROMPT, name, NORMAL))
        return '*---*'


## Manager Actions.

# From Manager_Action name to Manager_Action subclass.
manager_actions = {}


def introspect():
    import asterisk

    # Overload all manager key classes.
    for value in Manager_Key.__subclasses__():
        manager_keys[value.__name__] = value
    for key, value in asterisk.manager_keys.iteritems():
        base = manager_keys.get(key, Manager_Key)
        manager_keys[key] = type(key, (value, base), {})

    # Overload all manager actions, shadowing KEYS class attributes by
    # a copy in which manager key class references have been replaced
    # by our overloaded manager key classes.
    for key, value in asterisk.manager_actions.iteritems():
        keys = []
        for pair in value.keys:
            if isinstance(pair, tuple):
                keys.append((manager_keys[pair[0].__name__], pair[1]))
            else:
                keys.append(manager_keys[pair.__name__])
        manager_actions[key] = type(key, (value,), {'keys': keys})

introspect()

### Epilogue.

run = Main()
main = run.main

if __name__ == '__main__':
    main(*sys.argv[1:])
