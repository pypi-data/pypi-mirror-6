# -*- coding: utf-8 -*-
"""
Load urls for debug/development
"""
import datetime, json, random, string, pytz

from optparse import OptionValueError, make_option

from django.conf import settings
from django.core.cache import cache
from django.core.management.base import CommandError, BaseCommand
from django.contrib.auth.models import User
from django.utils.timezone import utc

from djangotribune.models import Channel, Message, Url
from djangotribune.parser import MessageParser

PREFIXES = (
    u'Lorem ipsum',
    u'Hey',
    u'Vestibulum era es huma nest',
    u'',
    u'Plop plop',
    u'[:totoz]',
    u'Haaaaaan :',
    u'C\'est vraiment <b>impensable</b> ce genre de choses',
    u'',
    u'C\'est sur que cette url c de la bombe',
    u'Everyone going to',
    u'Command doesn\'t accept any arguments',
    u'[:BREAKING NEWS]',
)
SUFFIXES = (
    u'c\'est du charabia',
    u'[:huit]',
    u'see this',
    u'mais non',
    u'nec vergiture',
    u'...',
    u'j\'crois que c\'est clair',
    u'[:totoz]',
    u'mais non',
    u'plip plap plup',
    u'prout',
)
UAS = (
    'Mozilla Firefox 42',
    'dummy',
    'Chromium 7556 (Webkit)',
    'anonymous',
    'sveebot',
)

class Anonymous(object):
    uas = (
        'Mozilla Firefox 42',
        'dummy',
        'Chromium 7556 (Webkit)',
        'anonymous',
        'sveebot',
    )
    def __str__(self):
        self.get_username()
        
    def __unicode__(self):
        self.get_username()
        
    @property
    def username(self):
        return random.choice(self.uas)
    

class Command(BaseCommand):
    option_list = BaseCommand.option_list
    help = "Command for fooooooo"

    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError("Command doesn't accept any arguments")
        
        users = list(User.objects.all())+[None]
        
        fp = open("/home/django/Essais/urls.json", "r")
        dump = json.load(fp)
        fp.close()
        
        for item in dump:
            parser = MessageParser()
            content = random.choice(PREFIXES)+ " "+item['fields']['url']+" " + random.choice(SUFFIXES)
            rendered = parser.render(content)
            created = datetime.datetime.utcnow().replace(tzinfo=utc)
            
            user_agent = "foo"
            author = random.choice(users)
            if author is None:
                user_agent = random.choice(UAS)
            
            new_message = Message(
                created=created,
                # Enforce the same time that the one stored in created
                clock=created.astimezone(pytz.timezone(settings.TIME_ZONE)).time(),
                channel=None,
                author=author,
                user_agent=user_agent,
                ip="192.168.0.101",
                raw=content,
                web_render=rendered['web_render'],
                remote_render=rendered['remote_render'],
            )
            new_message.save()
            self._save_urls(new_message, rendered['urls'])

    def _save_urls(self, message_instance, urls):
        """Save URLs finded in message content"""
        SAVE_URLS_BY_POST = 5 # limit
        l = []
        for coming_url in urls[:SAVE_URLS_BY_POST]:
            if coming_url not in l:
                new_url = message_instance.url_set.create(
                    author = message_instance.author,
                    url = coming_url
                )
                l.append(coming_url)
