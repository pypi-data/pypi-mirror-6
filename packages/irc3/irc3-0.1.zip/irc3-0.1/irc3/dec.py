# -*- coding: utf-8 -*-
import functools
import venusian
import re


def plugin(wrapped):
    def callback(context, name, ob):
        bot = context.bot
        bot.get_plugin(ob)
    assert isinstance(wrapped, type)
    venusian.attach(wrapped, callback, category='irc3')
    return wrapped


class event(object):

    venusian = venusian

    def __init__(self, regexp, callback=None):
        self.regexp = regexp
        self.callback = callback

    def async_callback(self, kwargs):  # pragma: no cover
        return self.callback(**kwargs)

    def compile(self, config):
        regexp = getattr(self.regexp, 're', self.regexp)
        if config:
            regexp = regexp % config
        self.cregexp = re.compile(regexp)

    def __call__(self, wrapped):
        def callback(context, name, ob):
            bot = context.bot
            if info.scope == 'class':
                self.callback = getattr(
                    bot.get_plugin(ob),
                    wrapped.__name__)
            else:
                @functools.wraps(wrapped)
                def wrapper(**kwargs):
                    return wrapped(bot, **kwargs)
                self.callback = wrapper
            # a new instance is needed to keep this related to *one* bot
            # instance
            e = self.__class__(self.regexp, self.callback)
            e.compile(bot.config)
            bot.add_event(e)
        info = self.venusian.attach(wrapped, callback, category='rfc1459')
        return wrapped

    def __repr__(self):
        s = getattr(self.regexp, 'name', self.regexp)
        return '<event %s>' % s
