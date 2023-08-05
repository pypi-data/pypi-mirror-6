#!/usr/bin/env python
#
# Copyright 2013 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import inspect
import collections
from importlib import import_module

from .util.decorator import EasyDecorator

__all__ = ['component_class',
           'watches', 'observe', 'observes', 'handle', 'handles',
           'every',
           'triggers_on', 'keyword', 'keywords', 'trigger', 'triggers',
           'ComponentManager']

#Used to mark classes for later inspection
CLASS_MARKER = '_PYAIB_COMPONENT'

#TODO: Include way to require a plugin or component be loaded first


def component_class(cls):
    """
        Let the component loader know to load this class
        If they pass a string argument to the decorator use it as a context
        name for the instance
    """
    if isinstance(cls, basestring):
        context = cls

        def wrapper(cls):
            setattr(cls, CLASS_MARKER, context)
            return cls
        return wrapper

    elif inspect.isclass(cls):
        setattr(cls, CLASS_MARKER, True)
        return cls


def _get_plugs(method, kind):
    """ Setup a place to put plugin hooks, allowing only one type per func """
    if not hasattr(method, '__plugs__'):
        method.__plugs__ = (kind, [])
    elif method.__plugs__[0] != kind:
        raise RuntimeError('Multiple Hook Types on a single method (%s)' %
                           method.__name__)
    return method.__plugs__[1]


def watches(*events):
    """ Define a series of events to later be subscribed to """
    def wrapper(func):
        eplugs = _get_plugs(func, 'events')
        eplugs.extend([event for event in events if event not in eplugs])
        return func
    return wrapper
observes = watches
observe = watches
handle = watches
handles = watches


def every(seconds, name=None):
    """ Define a timer to execute every interval """
    def wrapper(func):
        timers = _get_plugs(func, 'timers')
        timer = (name if name else func.__name__, seconds)
        if timer not in timers:
            timers.append(timer)
        return func
    return wrapper


class triggers_on(object):
    """Define a series of trigger words this method responds too"""
    def __init__(self, *words):
        self.words = words

    def __call__(self, func):
        triggers = _get_plugs(func, 'triggers')
        triggers.extend(set([word for word in self.words
                             if word not in triggers]))
        return func

    class channel(EasyDecorator):
        """Ignore triggers not in channels, or optionally a list of channels"""
        def wrapper(dec, irc_c, msg, trigger, args, kargs):
            if msg.channel:
                #Did they want to restrict which channels
                #Should we lookup allowed channels at run time
                if dec.args and dec.kwargs.get('runtime'):
                    ok = False
                    for attr in dec.args:
                        if hasattr(dec._instance, attr):
                            channel = getattr(dec._instance, attr)
                            if isinstance(channel, basestring)\
                                    and msg.channel.lower() == channel:
                                ok = True
                            elif isinstance(channel, collections.Container)\
                                    and msg.channel.lower() in channel:
                                ok = True
                    if not ok:
                        return
                elif dec.args and msg.channel not in dec.args:
                    return
                return dec.call(irc_c, msg, trigger, args, kargs)

    class private(EasyDecorator):
        """Only pass if triggers is from message not in a channel"""
        def wrapper(dec, irc_c, msg, trigger, args, kargs):
            if not msg.channel:
                return dec.call(irc_c, msg, trigger, args, kargs)

    class helponly(EasyDecorator):
        """Only provide help"""
        def wrapper(dec, irc_c, msg, trigger, args, kargs):
            msg.reply('%s %s' % (trigger, dec.__doc__))

    class autohelp(EasyDecorator):
        """Make --help trigger help"""
        def wrapper(dec, irc_c, msg, trigger, args, kargs):
            if 'help' in kargs or (args and args[0] == 'help'):
                msg.reply('%s %s' % (trigger, dec.__doc__))
            else:
                dec.call(irc_c, msg, trigger, args, kargs)

    class autohelp_noargs(EasyDecorator):
        """Empty args / kargs trigger help"""
        #It was impossible to call autohelp to decorate this method
        def wrapper(dec, irc_c, msg, trigger, args, kargs):
            if (not args and not kargs) or 'help' in kargs or (
                    args and args[0] == 'help'):
                msg.reply('%s %s' % (trigger, dec.__doc__))
            else:
                return dec.call(irc_c, msg, trigger, args, kargs)

    class sub(EasyDecorator):
        """Handle only sub(words) for a given trigger"""
        def __init__(dec, *words):
            dec._subs = words
            for word in words:
                if not isinstance(word, basestring):
                    raise TypeError("sub word must be a string")

        def wrapper(dec, irc_c, msg, trigger, args, kargs):
            if args and args[0].lower() in dec._subs:
                return dec.call(irc_c, msg, '%s %s' % (trigger,
                                                       args[0].lower()),
                                args[1:], kargs)

    subs = sub

    class nosub(EasyDecorator):
        """Prevent call if argument is present"""
        def wrapper(dec, irc_c, msg, trigger, args, kargs):
            if (not dec.args and args) or (dec.args and args
                                           and args[0].lower() in dec.args):
                return
            else:
                return dec.call(irc_c, msg, trigger, args, kargs)

    nosubs = nosub

keyword = keywords = trigger = triggers = triggers_on


class ComponentManager(object):
    """ Manage and Load all pyaib Components """

    def __init__(self, context, config):
        """ Needs a irc context and its config """
        self._loaded_components = {}
        self.context = context
        self.config = config

    def load(self, name):
        """ Load a python module as a component """
        if self.is_loaded(name):
            return
        #Load top level config item matching component name
        basename = name.split('.').pop()
        config = self.context.config.setdefault(basename, {})
        print("Loading Component %s..." % name)
        self._process_component(name, 'pyaib', CLASS_MARKER,
                                self.context, config)

    def load_configured(self, autoload=None):
        """
            Load all configured components autoload is a list of components
            to always load
        """
        components = []
        if isinstance(autoload, (list, tuple, set)):
            components.extend(autoload)

        #Don't do duplicate loads
        if self.config.load:
            if not isinstance(self.config.load, list):
                self.config.load = self.config.load.split(' ')
            [components.append(comp) for comp in self.config.load
             if comp not in components]
        for component in components:
            self.load(component)

    def is_loaded(self, name):
        """ Determine by name if a component is loaded """
        return name in self._loaded_components

    def _install_hooks(self, context, hooked_methods):
        #Add All the hooks to the right place
        for method in hooked_methods:
            kind, args = method.__plugs__
            if kind == 'events':
                for event in args:
                    context.events(event).observe(method)
            elif kind == 'triggers':
                for word in args:
                    context.triggers(word).observe(method)
            elif kind == 'timers':
                for name, seconds in args:
                    context.timers.set(name, method, every=seconds)

    def _find_annotated_callables(self, class_marker, component_ns, config,
                                  context):
        annotated_callables = []
        for name, member in inspect.getmembers(component_ns):
            #Find Classes marked for loading
            if inspect.isclass(member) and hasattr(member, class_marker):
                obj = member(context, config)
                #Save the context for this obj if the class_marker is a str
                context_name = getattr(obj, class_marker)
                if isinstance(context_name, basestring):
                    context[context_name] = obj
                    #Search for hooked instance methods
                for name, thing in inspect.getmembers(obj):
                    if (isinstance(thing, collections.Callable)
                            and hasattr(thing, '__plugs__')):
                        annotated_callables.append(thing)
            #Find Functions with Hooks
            if (isinstance(member, collections.Callable)
                    and hasattr(member, '__plugs__')):
                annotated_callables.append(member)
        return annotated_callables

    def _process_component(self, name, path, class_marker, context, config):
        if name.startswith('/'):
            importname = name[1:]
            path = None
        else:
            importname = '.'.join([path, name])

        try:
            component_ns = import_module(importname)
        except ImportError as e:
            raise ImportError('pyaib failed to load (%s): %r'
                              % (importname, e))

        annotated_calls = self._find_annotated_callables(class_marker,
                                                         component_ns, config,
                                                         context)
        self._install_hooks(context, annotated_calls)
        self._loaded_components[name] = component_ns
