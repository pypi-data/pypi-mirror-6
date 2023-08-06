#-*- coding: utf-8 -*-

import random

import pmxbot
from pmxbot.core import command
from pmxbot.karma import Karma

@command('pm', aliases=('piratemotivate',), doc='Arggh matey')
def pm(client, event, channel, nick, rest):
    if rest:
        rest = rest.strip()
        Karma.store.change(rest, 2)
        rcpt = rest
    else:
        rcpt = channel

    if random.random() > 0.95:
        return "Arrggh ye be doin' great, grand work, %s!" % rcpt
    return "Arrggh ye be doin' good work, %s!" % rcpt


@command('lm', aliases=('latinmotivate',), doc='Rico Suave')
def lm(client, event, channel, nick, rest):
    if rest:
        rest = rest.strip()
        Karma.store.change(rest, 2)
        rcpt = rest
    else:
        rcpt = channel
    return '¡Estás haciendo un buen trabajo, %s!' % rcpt

@command('fm', aliases=('frenchmotivate',), doc='pmxbot parle français')
def fm(client, event, channel, nick, rest):
    if rest:
        rest = rest.strip()
        Karma.store.change(rest, 2)
        rcpt = rest
    else:
        rcpt = channel
    return 'Vous bossez bien, %s!' % rcpt

@command('jm', aliases=('japanesemotivate',), doc='')
def jm(client, event, channel, nick, rest):
    if rest:
        rest = rest.strip()
        Karma.store.change(rest, 2)
        rcpt = rest
    else:
        rcpt = channel

    hon_romaji = ' san'
    hon_ja = ' さん'

    # Use correct honorific.
    bosses = pmxbot.config.get('bosses', set())
    if any(rcpt.lower().startswith(boss_nick) for boss_nick in bosses):
        hon_romaji = ' sensei'
        hon_ja = ' 先生'

    elif rcpt == channel:
        hon_romaji = ''
        hon_ja = ''

    emoji = '(^_−)−☆'

    # reference the vars to avoid linter warnings
    emoji, hon_romaji, hon_ja

    return (
        '{rcpt}{hon_ja}, あなたわよくやっています! '
        '({rcpt}{hon_romaji}, anata wa yoku yatte '
        'imasu!)  -  {emoji}'.format(**vars())
    )

@command('danke', aliases=('dankeschoen','ds','gm','germanmotivate'),
    doc='Danke schön!')
def danke(client, event, channel, nick, rest):
    if rest:
        rest = rest.strip()
        Karma.store.change(rest, 1)
        rcpt = rest
    else:
        rcpt = channel
    return 'Danke schön, {rcpt}! Danke schön!'.format(rcpt=rcpt)

@command('esperantomotivate', aliases=('em',), doc='Esperanto motivate')
def em(client, event, channel, nick, rest):
    if rest:
        rest = rest.strip()
        Karma.store.change(rest, 2)
        rcpt = rest
    else:
        rcpt = channel
    return 'Vi faras bonan laboron, {rcpt}!'.format(rcpt=rcpt)
