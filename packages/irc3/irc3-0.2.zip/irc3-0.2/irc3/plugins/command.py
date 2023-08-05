# -*- coding: utf-8 -*-
__doc__ = '''
==========================================
:mod:`irc3.plugin.command` Command plugin
==========================================

Introduce a ``@command`` decorator

The decorator use `docopts <http://docopt.org/>`_ to parse command arguments.

Example:

Create a python module with some commands:

.. literalinclude:: ../../examples/mycommands.py

..
    >>> import sys
    >>> sys.path.append('examples')
    >>> from irc3 import IrcBot
    >>> IrcBot.defaults.update(async=False, testing=True)

And register it::

    >>> from irc3 import IrcBot
    >>> bot = IrcBot()
    >>> bot.include('irc3.plugins.command')  # register the plugin
    >>> bot.include('mycommands')            # register your commands


Check the result::

    >>> bot.test(':gawel!user@host PRIVMSG #chan :!echo foo')
    >>> bot.sent
    ['PRIVMSG gawel :foo']

In the docstring, ``%%`` is replaced by the command character. ``!`` by
default. You can override it by passing a ``cmd`` parameter to bot's config.

When a command is not public, you can't use it on a channel::

    >>> bot.test(':gawel!user@host PRIVMSG #chan :!adduser foo pass')
    >>> bot.sent
    ["PRIVMSG #chan :You can only use the 'adduser' command in private"]

You can use a guard to prevent untrusted users to run some commands. The
:class:`free_policy` is used by default.

There is two builtin policy:

.. autoclass:: free_policy


.. autoclass:: mask_based_policy

Guard usage::

    >>> config = {
    ...     'irc3.plugins.command': {'guard': mask_based_policy},
    ...     'irc3.plugins.command.masks': ['gawel!*@*']}
    >>> bot = IrcBot(**config)
    >>> bot.include('irc3.plugins.command')  # register the plugin
    >>> bot.include('mycommands')            # register your commands
    >>> bot.test(':foo!u@h PRIVMSG #chan :!echo bar')
    >>> bot.sent
    ["PRIVMSG foo :You are not allowed to use the 'echo' command"]
    >>> bot.test(':gawel!u@h PRIVMSG #chan :!echo bar')
    >>> bot.sent
    ['PRIVMSG gawel :bar']

Mask based guard using permissions::

    >>> config = {
    ...     'irc3.plugins.command': {'guard': mask_based_policy},
    ...     'irc3.plugins.command.masks': {
    ...     'gawel!*@*': ['all_permissions'],
    ...     'foo!*@*': ['help'],
    ... }}
    >>> bot = IrcBot(**config)
    >>> bot.include('irc3.plugins.command')  # register the plugin
    >>> bot.test(':foo!u@h PRIVMSG #chan :!ping')
    >>> bot.sent
    ["PRIVMSG foo :You are not allowed to use the 'ping' command"]
    >>> bot.test(':gawel!u@h PRIVMSG #chan :!ping')
    >>> bot.sent
    ['NOTICE gawel :PONG gawel!']

'''
from irc3 import utils
import functools
import venusian
import fnmatch
import logging
import docopt
import irc3


class free_policy:
    """Default policy"""
    def __init__(self, bot):
        self.bot = bot

    def __call__(self, predicates, meth, mask, target, args):
        return meth(mask, target, args)


class mask_based_policy:
    """Allow only valid masks. Able to take care or permissions"""
    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger(__name__)
        self.masks = bot.config[__name__ + '.masks']
        self.log.debug('Masks: %r', self.masks)

    def has_permission(self, mask, permission):
        for pattern in self.masks:
            if fnmatch.fnmatch(mask, pattern):
                if permission is None or not isinstance(self.masks, dict):
                    return True
                perms = self.masks[pattern]
                if permission in perms or 'all_permissions' in perms:
                    return True
                return False

    def __call__(self, predicates, meth, mask, target, args):
        if self.has_permission(mask, predicates.get('permission')):
            return meth(mask, target, args)
        self.bot.privmsg(
            mask.nick,
            'You are not allowed to use the %r command' % meth.__name__
        )


class command:

    venusian = venusian
    defaults = {'permission': None}

    def __init__(self, *func, **predicates):
        self.predicates = predicates
        if func:
            self.__call__ = self.func = func[0]
            self.info = self.venusian.attach(self, self.callback,
                                             category=self.__module__)
        self.category = self.predicates.pop('venusian_category',
                                            self.__module__)

    def callback(self, context, name, ob):
        bot = context.bot
        if self.info.scope == 'class':
            callback = self.func.__get__(bot.get_plugin(ob), ob)
        else:
            @functools.wraps(self.func)
            def wrapper(*args, **kwargs):
                return self.func(bot, *args, **kwargs)
            callback = wrapper
        plugin = bot.get_plugin(Commands)
        self.predicates.update(module=self.func.__module__)
        plugin[self.func.__name__] = (self.predicates, callback)
        bot.log.info('Register command %r', self.func.__name__)

    def __call__(self, func):
        self.__call__ = self.func = func
        self.info = self.venusian.attach(func, self.callback,
                                         category=self.category)
        return func


@irc3.plugin
class Commands(dict):

    def __init__(self, bot):
        self.bot = bot
        config = bot.config.get(__name__, {})
        self.log = logging.getLogger(__name__)
        self.log.debug('Config: %r', config)
        bot.config['cmd'] = self.cmd = config.get('cmd', '!')
        guard = utils.maybedotted(config.get('guard', free_policy))
        self.log.debug('Guard: %s', guard.__name__)
        self.guard = guard(bot)

    @irc3.event((r':(?P<mask>\S+) PRIVMSG (?P<target>\S+) '
                 r':%(cmd)s(?P<cmd>\w+)(\s(?P<data>\w+.*)|$)'))
    def on_command(self, cmd, mask=None, target=None, data=None, **kw):
        predicates, meth = self.get(cmd, (None, None))
        if meth is not None:
            if predicates.get('public', True) is False and target.is_channel:
                self.bot.privmsg(
                    target,
                    'You can only use the %r command in private' % cmd)
            else:
                self.do_command(predicates, meth, mask, target, data)

    def do_command(self, predicates, meth, mask, target, data):
        nick = self.bot.nick
        to = target == nick and mask.nick or target
        doc = meth.__doc__ or ''
        doc = [l.strip() for l in doc.strip().split('\n')]
        doc = [nick + ' ' + l.strip('%%')
               for l in doc if l.startswith('%%')]
        doc = 'Usage:' + '\n    ' + '\n    '.join(doc)
        data = data and data.split() or []
        try:
            args = docopt.docopt(doc, [meth.__name__] + data, help=False)
        except docopt.DocoptExit:
            self.bot.privmsg(to, 'Invalid arguments')
        else:
            msg = self.guard(predicates, meth, mask, target, args)
            self.bot.privmsg(to, msg)

    @command(permission='help')
    def help(self, mask, target, args):
        """Show help

            %%help [<cmd>]
        """
        to = target == self.bot.nick and mask.nick or target
        if args['<cmd>']:
            predicates, meth = self.get(args['<cmd>'], (None, None))
            if meth is not None:
                doc = meth.__doc__ or ''
                doc = [l.strip() for l in doc.split('\n') if l.strip()]
                for line in doc:
                    line = line.replace('%%', self.bot.config.cmd)
                    self.bot.privmsg(to, line)
        else:
            nb = int(self.bot.config.get('help.item_per_line', 8))
            cmds = sorted([self.cmd + k for k in self.keys()])
            msg = ', '.join(cmds[0:nb - 3])
            self.bot.privmsg(to, 'Available commands: ' + msg)
            for x in range(nb - 3, len(cmds), nb):
                msg = ', '.join(cmds[x:x+nb])
                self.bot.privmsg(to, msg)

    def __repr__(self):
        return '<Commands %s>' % sorted([self.cmd + k for k in self.keys()])


@command(permission='admin')
def ping(bot, mask, target, args):
    """ping/pong

        %%ping
    """
    bot.send('NOTICE %(nick)s :PONG %(nick)s!' % dict(nick=mask.nick))


@command(venusian_category='irc3.debug')
def quote(bot, mask, target, args):
    """send quote to the server

        %%quote <args>...
    """
    msg = ' '.join(args['<args>'])
    bot.log.info('quote> %r', msg)
    bot.send(msg)
