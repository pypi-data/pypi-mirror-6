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
Bubbles.

See the Octopasty manual.
"""

__metaclass__ = type
from cStringIO import StringIO
import codecs
import datetime
import gevent
import gevent.event
import gevent.queue
from gevent import socket
import sys
import time
import traceback

# File encoding.
encoding = 'UTF-8'

# For printing much smaller time stamps.
_initial_stamp = time.time()

# For being able to detect explicit None arguments.
UNSET = object()


class Error(Exception):
    "Misuse of a Bubble object."

    def __init__(self, diagnostic):
        self.diagnostic = '%s: %s' % (gevent.getcurrent(), diagnostic)

    def __str__(self):
        return self.diagnostic


def _repr_greenlet(greenlet):
    "Return our representation of a bubble, or `other' for any other greenlet."
    return repr(greenlet) if isinstance(greenlet, Bubble) else 'other'


def _repr_stamp(stamp):
    "Return a micro-second precise time stamp relative to module import time."
    return '%.6f' % (stamp - _initial_stamp)


## Messages and decorators.

class _Envelope:
    "Envelope for MESSAGE while it sits in an input or magic queue."

    def __init__(self, message, sender):
        self.stamp = time.time()
        self.message = message
        self.sender = sender

    def __repr__(self):
        return ('`%s %s %r\'' % (_repr_stamp(self.stamp),
                                 _repr_greenlet(self.sender),
                                 self.message))


class _Switching:
    "Request to save FUNCTION(*ARGS, **KWS) into ASYNC_RESULT."

    def __init__(self, function, args, kws, async_result):
        self.function = function
        self.args = args
        self.kws = kws
        self.async_result = async_result

    def __repr__(self):
        name = self.function.__name__
        if len(self.args) == 1 and not self.kws:
            # FIXME: Far too kludgey, simplify this!
            if isinstance(self.args[0], _Switching):
                self = self.args[0]
                name = self.function.__name__
            elif name.startswith('do_'):
                if isinstance(self.args[0], Reactive_Bubble):
                    return repr(self.args[0])
                return '%s %r' % (name[3:], self.args[0])
        fragments = []
        write = fragments.append
        write(name + '(')
        separator = ''
        for arg in self.args:
            write(separator)
            separator = ', '
            write(repr(arg))
        for key, value in sorted(self.kws.iteritems()):
            write(separator)
            separator = ', '
            write('%s=%r' % (key, value))
        write(')')
        return ''.join(fragments)


def exposed(function):
    "Decorator for a Bubble method usable from another greenlet."
    function.func_dict['exposed'] = True
    return function


def switching(function):
    """\
Decorator for methods automatically executed in their containing bubble.

Arguments block=True, timeout=None are implied, and obeyed if given; these
should not be declared in the decorated methods.  Whenever blocking, return
the function value, else return a gevent AsyncResult object, for which a
.get() gives access to the function value, then blocking as necessary.
"""

    def wrapper(self, *args, **kws):
        current = gevent.getcurrent()
        if 'block' in kws:
            block = kws['block']
            del kws['block']
        else:
            block = True
        if 'timeout' in kws:
            timeout = kws['timeout']
            del kws['timeout']
        elif isinstance(current, Bubble):
            timeout = current.idle_timeout
        else:
            timeout = None
        if block and self is current:
            # FIXME: What if timeout is not None?
            return function(self, *args, **kws)
        async_result = gevent.event.AsyncResult()
        self.add_message(_Switching(function, args, kws, async_result))
        if block:
            try:
                assert current not in Bubble._waiting_for, Bubble._waiting_for
                Bubble._waiting_for[current] = self
                return async_result.get(timeout=timeout)
            finally:
                del Bubble._waiting_for[current]
        return async_result

    wrapper.func_dict['exposed'] = True
    return wrapper


## Bubble types.


def metawarn(diagnostic):
    "Report DIAGNOSTIC at import time."
    # This function is called from a metaclass, which is itself being
    # used in some class declaration, the one being diagnosed.
    # So, we have to jump two stack levels to get to the proper context.
    import inspect
    frame = inspect.stack()[2]
    codecs.getwriter(encoding)(sys.stderr).write(
        '%s:%d: %s\n' % (frame[1], frame[2], diagnostic))


class MetaBubble(type):
    "Check a bubble class for both static and dynamic consistency."

    # The instance handled by a metaclass is a class, but otherwise,
    # there is nothing special to it.  This is not because SELF just
    # happens to refer to a class that it should be called anything
    # else then SELF: the class is an instance after all.  CLS is
    # also easy to grasp: like everywhere else, it refers to the class
    # being defined rather than an instance of it, which here, is the
    # metaclass itself.

    def __init__(self, name, bases, defs):

        # Check which kind of Bubble class we have!
        if name == 'Bubble':
            is_active = False
            is_reactive = True
        elif name in ('Active_Bubble', 'Reactive_Bubble'):
            is_active = False
            is_reactive = False
        else:
            is_active = issubclass(self, Active_Bubble)
            is_reactive = issubclass(self, Reactive_Bubble)

        # See which kind of messages are accepted by it.
        if 'accepted_types' in defs:
            if not isinstance(self.accepted_types, tuple):
                self.accepted_types = self.accepted_types,
            accepted_names = [accepted.__name__
                              for accepted in self.accepted_types]
        else:
            accepted_names = ()

        # Cross check accepted_types against do_TYPE methods."
        for key, value in defs.iteritems():
            if key.startswith('do_'):
                key = key[3:]
                if is_reactive:
                    if key in accepted_names:
                        accepted_names.remove(key)
                    else:
                        metawarn("Is %s missing from %s.accepted_types?"
                                 % (key, name))
                else:
                    metawarn("Unexpected method do_%s (%s is not reactive)!"
                             % (key, name))
        if is_reactive:
            for accepted_name in accepted_names:
                metawarn("Is do_%s missing?  (see %s.accepted_types)\n" %
                         (accepted_name, name))

        # My own style hurdles! :-)

        if is_active and 'configure' in defs:
            metawarn("%s.configure() unwelcome, maybe main()?" % name)
        if is_reactive and 'main' in defs:
            metawarn("%s.main() unwelcome, maybe configure()?" % name)

        # Detect run-time violations of the bubble principle.

        def closure(name, key, value):
            # NAME identifies the class being instrumented.
            # KEY is the method name within that class.
            # VALUE is the executable method itself.

            def function(self, *args, **kws):
                if self is not gevent.getcurrent():
                    raise Error("Unexposed %s.%s gets called (instance %s)."
                                % (name, key, self))
                return value(self, *args, **kws)

            function.__name__ = key
            return function

        for key in defs:
            if not key.startswith(('_', 'do__')):
                value = getattr(self, key)
                func_dict = getattr(value, 'func_dict', None)
                if not (func_dict is None or func_dict.get('exposed')):
                    setattr(self, key, closure(name, key, value))

        # Track all classes, and prepare to track all instances
        # grouped by class.  Beware the various SELF in the following
        # two lines: CLASS_REGISTRY refers to the metaclass variable,
        # while _RUNNING_INSTANCES gets created as a class variable
        # separately for each subclass of Bubble.
        self.class_registry.add(self)
        self._running_instances = set()

    @classmethod
    def _each_instance(cls, exclude_presets=True):
        "Iterator over living bubbles.  EXCLUDE_PRESETS to ignore presets."
        excludes = []
        if exclude_presets:
            for key, preset in each_hook('preset.*'):
                excludes.append(preset)
        for bubble_type in cls.class_registry:
            for instance in bubble_type._running_instances:
                if instance not in excludes:
                    yield instance

    # The Bubble class and all its subclasses.
    class_registry = set()

    @classmethod
    def dump_instances(cls, envelopes, queues, topology, write):
        "Show all bubbles and how they are related."
        short = not (envelopes or queues or topology)
        current = gevent.getcurrent()
        hooks = {}
        for key, instance in _hook_namespace.iteritems():
            if instance not in hooks:
                hooks[instance] = []
            hooks[instance].append(key)
        write("--- Begin bubble dump ----------------------------------->\n")
        for _, instance in sorted((repr(instance), instance)
                                  for instance in cls._each_instance(False)):
            if not short:
                write('\n')

            # Bubble identification and summary.
            name = str(instance)
            if instance in hooks:
                name += ' (%s)' % ', '.join(sorted(hooks[instance]))
            fragments = []
            if instance is current:
                fragments.append("CURRENT")
            if short:
                length = instance._input_queue.qsize()
                if length == 1:
                    fragments.append("one input")
                elif length > 0:
                    fragments.append("%d inputs" % length)
                length = instance._magic_queue.qsize()
                if length == 1:
                    fragments.append("one magic")
                elif length > 0:
                    fragments.append("%d magics" % length)
                if instance._listening_to:
                    fragments.append("listens to %d"
                                     % len(instance._listening_to))
                if instance._output_bus:
                    fragments.append("outputs to %d"
                                     % len(instance._output_bus))
            if fragments:
                write('%s: %s\n' % (name, ', '.join(fragments)))
            else:
                write('%s\n' % name)

            # Bubble topology.
            if topology:
                if instance._listening_to:
                    write("  Listening to: %s\n"
                          % ', '.join(map(str, instance._listening_to)))
                if instance._output_bus:
                    write("  Output bus: %s\n"
                          % ', '.join(map(str, instance._output_bus)))

            # Bubble queues.
            if queues:
                if instance._input_queue.qsize():
                    write("  Input queue:\n")
                    for counter, value in enumerate(
                            instance._input_queue.queue):
                        write('    %d: %r\n' % (counter + 1, value))
                if instance._magic_queue.qsize():
                    write("  Magic queue:\n")
                    for counter, value in enumerate(
                            instance._magic_queue.queue):
                        write('    %d: %r\n' % (counter + 1, value))

            # Last envelope.
            if envelopes and instance.envelope is not None:
                write("  Envelope: %s\n" % instance.envelope)
        write("--- End bubble dump -------------------------------------<\n")

    @classmethod
    def shutdown_instances(cls, write):
        "Try our best effort to quiesce all non-preset bubbles."

        class Reporter:

            def __init__(self, title, write):
                self.title = title
                self.write = write

            def report(self, text):
                if self.title is not None:
                    self.write(self.title)
                    self.title = None
                self.write('    %s\n' % text)

        report = Reporter("\nShutdown diagnostics:\n", write).report

        # Sort all instances, children first and parent last, but also
        # feeding bubbles first and fed bubbles last.  This assumes
        # (not verified) that children feed parents on average.
        import graph
        instances = list(cls._each_instance())
        arcs = []
        for instance in instances:
            if instance._parent is not None:
                arcs.append(graph.Arc(instance, instance._parent))
            for feeding in instance._output_bus:
                arcs.append(graph.Arc(instance, feeding))
        instances, cycles = graph.sort(instances, arcs)
        del arcs

        # Kill in order, breaking the loops first if any.
        clean = True
        # FIXME: The following sleep is not really OK: giving a chance
        # to other greenlets does not necessarily prevent a premature
        # return into this one.  While such a premature return is unlikely,
        # the greenlet specifications gives no guarantee in this area.
        gevent.sleep(0)
        for instance in cycles + instances:
            if not instance.daemon:
                report("%s still exists: killing it." % instance)
                instance.kill(timeout=.5)
                if not instance.dead:
                    report('%s refuses to die!' % instance)
                    clean = False

        # Diagnose any pending work on a preset bubble.
        # FIXME: Pending work is probably to be expected?  Logs are important.
        for key, preset in each_hook('preset.*'):
            if preset._input_queue.qsize() or preset._magic_queue.qsize():
                report("Preset %s has work pending." % preset)
                clean = False

        # Dump if shutdown is not clean.
        if not clean:
            dump(write=write)


class Bubble(gevent.Greenlet):
    "A Bubble is a Greenlet with an input queue and an output bus."
    __metaclass__ = MetaBubble

    # Unique per-type identification, more legible than id().
    _ordinal = 0
    # Parent bubble, merely for identification in traces.
    _parent = None
    # Number of Tracers currently listening, or None if disallowed.
    _tracer_count = 0
    # Mild machinery to detect inter-bubble AsyncResult deadlocks.
    _waiting_for = {}
    # Accepted types for messages.  A tuple of types.
    accepted_types = _Switching,
    # Die when inactive for that number of seconds (or None).
    idle_timeout = UNSET
    # A daemon bubble may be killed silently at shutdown time.
    daemon = False
    # Envelope of the last accepted message.
    envelope = None
    # Per-instance identification suffix to type name (or None).
    name_suffix = UNSET
    # If enabled, configure the default tracer at start time.
    trace_flag = False

    def __init__(self, suffix=UNSET, timeout=UNSET):
        if suffix is not UNSET:
            self.name_suffix = suffix
        elif self.name_suffix is UNSET:
            cls = type(self)
            cls._ordinal += 1
            self.name_suffix = str(cls._ordinal)
        super(Bubble, self).__init__()

        # Queue of input messages, consumed by get_request calls.
        # Only used in Active_Bubble, set here nevertheless to simplify tests.
        self._input_queue = gevent.queue.Queue()
        # Queue of input requests, consumed by main loop magic.
        self._magic_queue = gevent.queue.Queue()
        # List of bubbles listening for broadcasted messages.
        self._output_bus = []
        # _LISTENING_TO reverses the relation set by _OUTPUT_BUS.
        self._listening_to = []
        # Type to method cache.  Either a do_TYPE method or None.
        self._type_cache = {}

        current = gevent.getcurrent()
        if isinstance(current, Bubble):
            self._parent = current

        if timeout is not UNSET:
            self.idle_timeout = timeout
        elif self.idle_timeout is UNSET:
            if isinstance(current, Bubble):
                self.idle_timeout = current.idle_timeout
            else:
                self.idle_timeout = None

        self.start()
        if self.trace_flag:
            self.set_trace(True)

    def __repr__(self):
        text = type(self).__name__
        if self.name_suffix:
            text += self.name_suffix
        if self._parent is None:
            return text
        return repr(self._parent) + '.' + text

    def _reraise_after_log(self):
        "Last exception is formatted and logged, before being raised again."
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if exc_type is not gevent.GreenletExit:
            buffer = StringIO()
            traceback.print_exc(None, buffer)
            log.error(buffer.getvalue())
        raise

    def _run(self):
        "Process all magic messages."
        try:
            self.bootstrap()
        except:
            self._reraise_after_log()
        try:
            while True:
                try:
                    envelope = self.envelope = self._magic_queue.get(
                        timeout=self.idle_timeout)
                except gevent.queue.Empty:
                    log.warn("%s killed after being idle for %s seconds.",
                             self, self.idle_timeout)
                    break
                else:
                    if self._tracer_count:
                        self.send_message(
                            _Trace(self, self._magic_queue.qsize() + 1,
                                   '\\', envelope))
                    message = envelope.message
                    try:
                        message.function(*message.args, **message.kws)
                    except:
                        self._reraise_after_log()
        finally:
            try:
                self.shutdown()
            except:
                self._reraise_after_log()

    def _send_trace(self, size, mark, envelope, result=None):
        """\
Trace some event in input or magic queue, SIZE long prior to MARK event.
Also given: the ENVELOPE of a queued message, and the RESULT of a computation.
"""
        message = _Trace(self, size, mark, envelope, result)
        for recipient in self._output_bus:
            if _Trace in recipient.accepted_types:
                recipient.add_message(message)

    def _suicide(self, dying):
        # Useful as in DYING.link(self._suicide) merely to drop the argument
        # before killing ourself, so a DYING greenlet implies our own death.
        self.kill()

    def _try_adding_to_magic_queue(self, message):
        "Add MESSAGE to magic queue, else return envelope not yet added."
        message_type = type(message)
        # Set METHOD to the best do_TYPE method for MESSAGE, or None.
        method = self._type_cache.get(message_type, False)
        if method is False:
            for mro in message_type.__mro__:
                method = self._type_cache.get(mro, False)
                if method is not False:
                    break
                try:
                    method = getattr(self, 'do_' + mro.__name__)
                except AttributeError:
                    pass
                else:
                    break
            else:
                method = None
            self._type_cache[message_type] = method
        if method is not None:
            message = _Switching(method, (message,), {}, None)
            message_type = _Switching
        # Create and return an envelope right away if a plain message.
        envelope = _Envelope(message, gevent.getcurrent())
        if self.dead:
            raise Error("Agonizing bubble %s may not receive message %s."
                        % (self, envelope))
        if message_type is not _Switching:
            return envelope
        # Add envelope to magic queue and return None.
        if self._tracer_count:
            self._send_trace(self._magic_queue.qsize(), ':', envelope)
        self._magic_queue.put(envelope)

    @switching
    def add_to_output_bus(self, recipient):
        "Add RECIPIENT to the output bus."
        is_tracer = isinstance(recipient, Tracer)
        if is_tracer and self._tracer_count is None:
            return
        if recipient in self._output_bus:
            raise Error("%s is already listening to %s." % (recipient, self))
        self._output_bus.append(recipient)
        recipient._listening_to.append(self)
        if is_tracer:
            self._tracer_count += 1

    def bootstrap(self):
        "Prepare the bubble for execution."

        # Register that it exists.
        self._running_instances.add(self)

    def do__Switching(self, message):
        if self._tracer_count:
            envelope = self.envelope
            try:
                result = message.function(self, *message.args, **message.kws)
            except:
                self._reraise_after_log()
            self._send_trace(self._magic_queue.qsize(), '/', envelope, result)
        else:
            try:
                result = message.function(self, *message.args, **message.kws)
            except:
                self._reraise_after_log()
        if message.async_result is not None:
            message.async_result.set(result)

    @switching
    def remove_from_output_bus(self, recipient):
        "Remove RECIPIENT from the output bus."
        is_tracer = isinstance(recipient, Tracer)
        if is_tracer and self._tracer_count is None:
            return
        if recipient not in self._output_bus:
            raise Error("%s is not even listening to %s." % (recipient, self))
        self._output_bus.remove(recipient)
        recipient._listening_to.remove(self)
        if is_tracer:
            self._tracer_count -= 1

    def send_message(self, message, warn=True):
        "Send MESSAGE to the output bus.  Warn if no acceptors."
        for recipient in self._output_bus:
            if isinstance(message, recipient.accepted_types):
                recipient.add_message(message)
                warn = False
        if warn:
            log.warn("%s sends message which no bubble accepts:\n%r"
                     % (self, message))

    @switching
    def set_trace(self, flag=True):
        "Trace or untrace this bubble."
        tracer = get_hook('preset.tracer')
        if flag:
            if tracer not in self._output_bus:
                self.add_to_output_bus(tracer)
        else:
            if tracer in self._output_bus:
                self.remove_from_output_bus(tracer)

    def shutdown(self):
        "Prepare the bubble for death."

        # (Try to) make it disappear.  "Simulacron 3" style! :-)
        _hook_monitors.discard(self)
        for recipient in self._output_bus[:]:
            self.remove_from_output_bus(recipient)
        for sender in self._listening_to[:]:
            sender.remove_from_output_bus(self)
        self._running_instances.remove(self)

        # Diagnose any pending work the bubble is abandoning.
        write = get_hook('preset.output').write
        for envelope in self._input_queue.queue:
            write("* Dying %s drops %s.\n" % (self, envelope))
        for envelope in self._magic_queue.queue:
            write("* Dying %s drops %s.\n" % (self, envelope))


class Active_Bubble(Bubble):
    "Bubble which relies on get_message calls."

    @exposed
    def add_message(self, message):
        "Add MESSAGE to input queue or magic queue, as appropriate."
        envelope = self._try_adding_to_magic_queue(message)
        if envelope is not None:
            if not isinstance(envelope.message, self.accepted_types):
                raise Error(
                    "%s does not accept type %s of message %s."
                    % (self, type(envelope.message).__name__, envelope))
            if self._tracer_count:
                self._send_trace(self._input_queue.qsize(), '+', envelope)
            self._input_queue.put(envelope)

    def get_message(self, timeout=UNSET):
        "Get next message from input queue, waiting for it if necessary."
        if timeout is UNSET:
            timeout = self.idle_timeout
        try:
            envelope = self._input_queue.get(timeout=timeout)
        except gevent.queue.Empty:
            raise gevent.Timeout
        else:
            self.envelope = envelope
        if self._tracer_count:
            self._send_trace(
                self._input_queue.qsize() + 1, '-', envelope)
        return envelope.message


class Reactive_Bubble(Bubble):
    "Bubble which relies on do_TYPE methods."

    @exposed
    def add_message(self, message):
        "Add MESSAGE to magic queue."
        envelope = self._try_adding_to_magic_queue(message)
        if envelope is not None:
            raise Error("%s does not accept type %s of message %s."
                        % (self, type(envelope.message).__name__, envelope))


class Input(Reactive_Bubble):
    "Deliver data from some input stream."

    daemon = True
    file = None

    @switching
    def bytes(self, size):
        # FIXME: Should obey self.idle_timeout.
        if size > 0:
            value = self.file.read(size)
            if not value:
                self.kill(block=False)
            return value
        return ''

    @switching
    def line(self):
        # FIXME: Should obey self.idle_timeout.
        value = self.file.readline()
        if not value:
            self.kill(block=False)
        return value

    @switching
    def lines(self):
        # FIXME: Should obey self.idle_timeout.
        value = self.file.readlines()
        if not value:
            self.kill(block=False)
        return value

    @switching
    def rest(self):
        # FIXME: Should obey self.idle_timeout.
        value = self.file.read()
        self.kill(block=False)
        return value

    @switching
    def forward_lines(self, recipient=None):
        # FIXME: Should obey self.idle_timeout.
        if recipient is None:
            for line in self.file:
                self.send_message(line)
        else:
            for line in self.file:
                recipient.add_message(line)
        self.kill(block=False)

    @switching
    def forward_rest(self, recipient=None):
        # FIXME: Should obey self.idle_timeout.
        buffer = self.file.read()
        if buffer:
            if recipient is None:
                self.send_message(buffer)
            else:
                recipient.add_message(buffer)
        self.kill(block=False)

    @switching
    def set_file(self, file):
        self.file = file

    @switching
    def set_socket(self, handle):
        self.file = handle.makefile()


class Output(Reactive_Bubble):
    "Write textual information."

    accepted_types = str, unicode
    daemon = True
    count_reset = None
    count = None

    def bootstrap(self):
        super(Output, self).bootstrap()
        self.file = codecs.getwriter(encoding)(sys.stdout)
        self.write = self.file.write

    def do_str(self, text):
        try:
            self.write(text)
        except socket.error:
            log.debug("%s: Connection has been severed.", self)
            self.kill(block=False)

    def do_unicode(self, text):
        self.write(text)

    @switching
    def flush(self):
        if self.file is not None:
            self.file.flush()

    @switching
    def set_file(self, file, flush=None):
        self.file = file
        if flush is None:
            self.write = file.write
        else:

            def flusher():
                while True:
                    gevent.sleep(1)
                    if self.count is not None:
                        if self.count == 0:
                            file.flush()
                            self.count = None
                        else:
                            self.count -= 1

            def writer(text):
                file.write(text)
                if self.count is None:
                    self.count = self.count_reset

            self.write = writer
            self.count_reset = flush
            self.flusher = gevent.Greenlet(flusher)
            self.flusher.start()

    @switching
    def set_socket(self, handle):
        self.file = handle.makefile('w', 0)
        self.write = self.file.write

    @switching
    def set_write(self, write):
        self.file = None
        self.write = write

    def shutdown(self):
        self.file = None
        self.write = None
        super(Output, self).shutdown()


## Hooks.

# Trace gets activated automatically for matching hooks.
_hook_autotrace = set()
# All monitoring bubbles.
# FIXME: Could it be made the output_bus of some administrative bubble?
_hook_monitors = set()
# Hooks themselves, relating a name to a bubble.
_hook_namespace = {}


def _matching_hook(key, pattern):
    "Is KEY matched, shell style, by PATTERN?"
    import fnmatch
    return fnmatch.fnmatch(key, pattern)


def get_hook(key):
    "Return the value of KEY in the namespace, else None."
    return _hook_namespace.get(key)


def set_hook(key, new):
    "Set KEY to a NEW bubble instance.  Delete KEY if NEW is None."
    previous = _hook_namespace.get(key)
    if new is None:
        if key in _hook_namespace:
            del _hook_namespace[key]
    else:
        _hook_namespace[key] = new
    for monitor in _hook_monitors:
        monitor.add_message((key, previous, new))
    for pattern in _hook_autotrace:
        if _matching_hook(key, pattern):
            new.set_trace()
            break


def each_hook(pattern):
    "Return (KEY, INSTANCE) for all keys matching the shell-style PATTERN."
    for key, instance in _hook_namespace.iteritems():
        if _matching_hook(key, pattern):
            yield key, instance


def add_after_hook(key, new):
    "Insert NEW bubble on the output bus side of bubble hanging on KEY."
    instance = _hook_namespace.get(key)
    listeners = instance._output_bus[:]

    for listener in listeners:
        new.add_to_output_bus(listener)
    instance.add_to_output_bus(new)
    for listener in listeners:
        instance.remove_from_output_bus(listener)


def add_before_hook(key, new):
    "Insert NEW bubble on the input queue side of bubble hanging on KEY."
    instance = _hook_namespace.get(key)
    senders = instance._listening_to[:]

    for sender in senders:
        sender.add_to_output_bus(new)
    new.add_to_output_bus(instance)
    for sender in senders:
        sender.remove_from_output_bus(instance)

    set_hook(key, new)


def replace_hook(key, new):
    "Replace the bubble hanging on hook KEY by NEW bubble."
    instance = _hook_namespace.get(key)
    listeners = instance._output_bus[:]
    senders = instance._listening_to[:]

    for listener in listeners:
        new.add_to_output_bus(listener)
    for sender in senders:
        sender.add_to_output_bus(new)
    for sender in senders:
        sender.remove_from_output_bus(instance)
    for listener in listeners:
        instance.remove_from_output_bus(listener)

    set_hook(key, new)
    # FIXME: Should it move queue contents first?
    instance.kill(block=False)


def monitor_hooks(instance):
    "Bubble INSTANCE wants to monitor all hook changes."
    _hook_monitors.add(instance)


## Debugging.

class Backdoor(Reactive_Bubble):
    "Handle an interactive backdoor into the Python interpreter."

    where = None

    def shutdown(self):
        if self.where is not None:
            self.stop_server()
        super(Backdoor, self).shutdown()

    @switching
    def start_server(self, host='localhost', port=None):
        "Start a server on HOST and PORT."
        assert port is not None
        if self.where is not None:
            self.stop_server()
        self.where = host, port
        log.info("Installing backdoor on %s, port %d.", host, port)
        from gevent.backdoor import BackdoorServer
        server = BackdoorServer(self.where)
        server.start()

    @switching
    def stop_server(self):
        "Stop the server currently executing."

        def read_until(handle, expected):
            text = ''
            while not text.endswith(expected):
                result = handle.recv(1)
                assert result
                text += result
            return text

        host, port = self.where
        log.info("Terminating backdoor on %s, port %d.", host, port)
        handle = socket.create_connection(self.where)
        read_until(handle, '>>> ')
        handle.sendall('quit()\r\n')
        line = handle.makefile().readline()
        assert line.strip() == '', repr(line)
        self.where = None


class Log_Factory:
    """\
Logging function factory, all meant for the LOGGER bubble.

After "log = Log_Factory(LOGGER)", a "log.SYMBOL(FORMAT, *ARGS)" call
sends a log entry to the LOGGER input queue with the arguments saved.
The log entry category is a number automatically allocated or recycled
from SYMBOL, that number is available in "log.SYMBOL.category".
"""

    def __init__(self, logger):
        self._set_logger(logger)
        self._category = 0
        self._symbols = {}

    def __getattr__(self, attribute):
        if attribute.startswith('_'):
            super(Log_Factory, self).__getattr__(attribute)

        def closure(symbol, category):

            def function(format, *args):
                self._logger.add_message(Log_Entry(function, format, args))

            function.category = category
            function.symbol = symbol
            return function

        assert self._category < 32
        self._symbols[self._category] = attribute
        function = closure(attribute, self._category)
        setattr(self, attribute, function)
        self._category += 1
        return function

    def _set_logger(self, logger):
        # FIXME: When @switching, __getattr__ called  with _logger still None.
        # After this gets corrected, document the call in the manual.
        self._logger = logger


class Log_Entry:
    """\
Log entry made by FUNCTION, textual contents is FORMAT % ARGS.
"""

    def __init__(self, function, format, args):
        self.function = function
        self.format = format
        self.args = args

    def __repr__(self):
        return 'Log_Entry([%s], %r)' % (self.function.symbol, self.format)


class Logger(Reactive_Bubble):
    "Copy log messages, filtering them by mask, and adding time stamps."
    accepted_types = Log_Entry, str, unicode

    # White margin for continuation lines.
    _margin = ' ' * 20  # "YYYY-MM-YY HH:MM:SS "
    # How many decimals to a second?  From 0 to 6, < 0 truncates to minutes.
    decimals = 0
    # Mask of logged categories.  Default is to log everything.
    mask = (1 << 32) - 1
    # Whether the time stamp should be included or not.
    stamp = True
    # Maximum line width of each log line, or 0 for no wrapping.
    width = 0

    def do_Log_Entry(self, log):
        if 1 << log.function.category & self.mask:
            self.do_unicode('[' + log.function.symbol + '] ' + log.format,
                            *log.args)

    def do_str(self, format, *args):
        self.do_unicode(format, *args)

    def do_unicode(self, format, *args):

        # Prepare date and time.
        if self.stamp:
            now = datetime.datetime.now()
            date = now.date()
            time = now.time()
            stamp = date.isoformat() + ' %.2d:%.2d' % (time.hour, time.minute)
            if self.decimals >= 0:
                stamp += ':%.2d' % time.second
                if self.decimals > 0:
                    stamp += '.' + ('%.6d' % time.microsecond)[:self.decimals]
            stamp += ' '
        else:
            stamp = ''

        # Write text lines, shifted and split as needed.  Empty lines removed.
        fragments = []
        write = fragments.append
        width = self.width - len(stamp) if self.width else None
        try:
            text = format % args
        except Exception, exception:
            # We should not lose a Logger over a bad format or missing arg!
            text = '%s: (%r %% %r)' % (exception, format, args)
        for line in text.split('\n'):
            if width is not None:
                while len(line) > width:
                    part = line[:width].rstrip()
                    line = line[width:].lstrip()
                    if part:
                        write(stamp + part + '\n')
                        stamp = self._margin
            if line:
                write(stamp + line + '\n')
                stamp = self._margin
        self.send_message(''.join(fragments))

    @switching
    def set_options(self, decimals=None, level=None,
                    mask=None, stamp=None, width=None):
        "Change logging options."

        if decimals is not None:
            self.decimals = decimals
        if level is not None:
            # LEVEL for all categories up to and including that level.
            # If both LEVEL and MASK are given, their effect combine.
            if mask is None:
                mask = 0
            mask |= (1 << level) - 1
        if mask is not None:
            self.mask = mask
        if stamp is not None:
            self.stamp = stamp
        if width is not None:
            self.width = width
        if self.stamp:
            self._margin = ' ' * 16
            if self.decimals >= 0:
                self._margin += ' ' * 3
                if self.decimals > 0:
                    self._margin += ' ' * (1 + self.decimals)
            self._margin += ' '
        else:
            self._margin = ''


class Rug_Logger(Logger):
    # Useful before bubble is wholly setup.
    daemon = True

    def send_message(self, text):
        sys.stderr.write(text)


rug_logger = Rug_Logger(suffix='-init')
log = Log_Factory(rug_logger)


class _Trace:
    """\
Request to trace some change in RECIPIENT's input or magic queue.

The input or magic queue was SIZE long prior to the change.
TEXT describes the change.  ENVELOPE describes the message.
"""

    result = None

    def __init__(self, recipient, size, mark, envelope, result=None):
        self.stamp = time.time()
        self.current = gevent.getcurrent()
        self.recipient = recipient
        self.size = size
        self.mark = mark
        self.envelope = envelope
        if result is not None:
            self.result = result

    def __repr__(self):
        return ('_Trace("%s %s | %s %d : %s %s%s")'
                % (_repr_stamp(self.stamp), _repr_greenlet(self.current),
                   self.recipient, self.size, self.mark, self.envelope,
                   '' if self.result is None else ' -> %r' % self.result))


class Tracer(Reactive_Bubble):
    "Format trace information onto the output bus."

    _tracer_count = None
    accepted_types = _Trace,
    envelope_option = False
    previous_current = None
    previous_envelope = None
    previous_recipient = None
    previous_sender = None
    width_bubble = 0
    width_middle = 0

    def do__Trace(self, trace):
        fragments = []
        write = fragments.append

        # Handle current bubble for print width and ellipsis.
        if trace.current is self.previous_current:
            text_current = ''
        else:
            self.previous_current = trace.current
            text_current = _repr_greenlet(trace.current)
            if len(text_current) > self.width_bubble:
                self.width_bubble = len(text_current)

        # Handle recipient bubble for print width and ellipsis.
        if trace.recipient is self.previous_recipient:
            text_recipient = ''
        else:
            self.previous_recipient = trace.recipient
            text_recipient = _repr_greenlet(trace.recipient)
            if len(text_recipient) > self.width_bubble:
                self.width_bubble = len(text_recipient)

        # Handle sender bubble for print width and ellipsis.
        if self.envelope_option:
            if trace.envelope.sender is self.previous_sender:
                text_sender = ''
            else:
                self.previous_sender = trace.envelope.sender
                text_sender = _repr_greenlet(trace.envelope.sender)
                if len(text_sender) > self.width_bubble:
                    self.width_bubble = len(text_sender)

        # Format the leftmost columns.
        write(_repr_stamp(trace.stamp) + ' ')
        write(text_current.ljust(self.width_bubble))
        write(' | ')
        write(text_recipient.ljust(self.width_bubble))

        # Format the remaining columns, caring about envelope ellipsis.
        if trace.envelope is self.previous_envelope and trace.result is None:
            write(' %d %s' % (trace.size, trace.mark))
        else:
            self.previous_envelope = trace.envelope
            if self.envelope_option:
                text = '%d %s %s' % (trace.size, trace.mark,
                                     _repr_stamp(trace.envelope.stamp))
                if len(text) > self.width_middle:
                    self.width_middle = len(text)
                    write(' ' + text.ljust(self.width_middle) + ' ')
                write(text_sender.ljust(self.width_bubble))
            else:
                text = '%d %s' % (trace.size, trace.mark)
                if len(text) > self.width_middle:
                    self.width_middle = len(text)
                write(' ' + text.ljust(self.width_middle))
            write(' %r' % trace.envelope.message)
            if trace.result is not None:
                write(' -> %r' % trace.result)

        # Send the formatted trace line in one bunch.
        self.send_message(''.join(fragments) + '\n')

    @switching
    def set_options(self, envelope=None):
        "Change formatting options."
        if envelope is not None:
            self.envelope_option = envelope


def dump(envelopes=False, queues=True, topology=True, write=None):
    if write is None:
        # Beware: sys.stdout gets redefined within the backdoor.
        write = sys.stdout.write
    MetaBubble.dump_instances(envelopes, queues, topology, write)


def dump_summary(write=None):
    if write is None:
        # Beware: sys.stdout gets redefined within the backdoor.
        write = sys.stdout.write
    MetaBubble.dump_instances(False, False, False, write)


## Bootstrap and shutdown.

def bootstrap(timeout=None):
    "Bootstrap a bubble system, launching its preset bubbles."

    backdoor = Backdoor(suffix='-preset', timeout=timeout)
    set_hook('preset.backdoor', backdoor)

    input = Input(suffix='-preset', timeout=timeout)
    set_hook('preset.input', input)

    logger = Rug_Logger(suffix='-preset', timeout=timeout)
    set_hook('preset.logger', logger)

    output = Output(suffix='-preset', timeout=timeout)
    logger.add_to_output_bus(output)
    set_hook('preset.output', output)

    tracer = Tracer(suffix='-preset', timeout=timeout)
    tracer.add_to_output_bus(output)
    set_hook('preset.tracer', tracer)


def set_trace(flag=True):
    "Trace all future bubbles, or not."
    Bubble.trace_flag = flag


def shutdown(write=None):
    "Shutdown a bubble system, waiting for all bubbles to die."
    # FIXME: Rug_Logger does not get killed automatically!
    backdoor = get_hook('preset.backdoor')
    input = get_hook('preset.input')
    logger = get_hook('preset.logger')
    output = get_hook('preset.output')
    tracer = get_hook('preset.tracer')

    if write is None:
        write = output.write
    MetaBubble.shutdown_instances(write)
    backdoor.kill()
    input.kill()
    logger.kill()
    tracer.kill()
    output.kill()
    Bubble.trace_flag = False

    set_hook('preset.backdoor', None)
    set_hook('preset.input', None)
    set_hook('preset.logger', None)
    set_hook('preset.output', None)
    set_hook('preset.tracer', None)
