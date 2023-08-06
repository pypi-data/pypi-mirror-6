# -*- coding:utf-8 -*-
from django.utils.translation import ugettext

KB = 1024  # bytes
MB = 1024 * KB  # kb

GENDER_UNDEFINED = 'I'
GENDER_MALE = 'M'
GENDER_FEMALE = 'F'
GENDER_CONFUSED = 'W'
GENDER_CHOICES = (
    (GENDER_UNDEFINED, '???'),
    (GENDER_MALE, ugettext('Male')),
    (GENDER_FEMALE, ugettext('Female')),
    (GENDER_CONFUSED, ugettext("Won't tell"))
)

BBCODE, RST, MARKDOWN, TEXTILE, PLAIN_HTML, PLAIN_TEXT = 0, 1, 2, 3, 4, 5

TEXT_FORMAT_CHOICES = (
    (BBCODE, 'BBcode'),
    (RST, 'reStructuredText'),
    (MARKDOWN, 'Markdown'),
    (TEXTILE, 'Textile'),
    (PLAIN_HTML, 'Plain HTML'),
    (PLAIN_TEXT, 'Plain text'),
)

# plain text, bbcode, markdown, textile, restructuredtext, plain html
MARKUP_CHOICES = (
    (PLAIN_TEXT, 'Plain text'),
    (BBCODE, 'BBCode'),
    (MARKDOWN, 'Markdown'),
    (TEXTILE, 'Textile'),
    (RST, 'reStructuredText'),
    (PLAIN_HTML, 'Plain HTML'),
)

MARKUP_EDITORS = {
    PLAIN_TEXT: 'default',
    BBCODE: 'bbcode',
    MARKDOWN: 'markdown',
    TEXTILE: 'textile',
    RST: 'rest',
    PLAIN_HTML: 'html',
}

TRANSLATE_MARKUP = {}

for code, txt in MARKUP_CHOICES:
    TRANSLATE_MARKUP[txt.lower()] = code

# reply ratings
LIKES, DISLIKES = 1, -1
RATING_CHOICES = (
    (DISLIKES, 'Dislikes'),
    (LIKES, 'Liked'),
)

# thread status
# thread is open -> can view, *edit and reply
THREAD_STATUS_OPEN = 2**1
# thread is open -> can view, can not edit nor reply
THREAD_STATUS_CLOSED = 2**2
THREAD_STATUS_FLAGGED = 2**3
THREAD_STATUS_CH = (
    (THREAD_STATUS_OPEN, ugettext('Open')),
    (THREAD_STATUS_CLOSED, ugettext('Closed')),
    (THREAD_STATUS_FLAGGED, ugettext('Flagged'))
    )

PERMISSION_OPEN = 2**1
PERMISSION_LOGGED = 2**2
PERMISSION_PRIVATE = 2**3

PERMISSIONS = (
    # everybody can enter
    (PERMISSION_OPEN, ugettext('Open access')),
    # only logged users can enter
    (PERMISSION_LOGGED, ugettext('Permited to logged users only')),
    )

IMPROPER_CONTENT = 2**1
SPAM = 2**2
TROLL = 2**3
OTHER = 2**31

REASON_CH = (
    (IMPROPER_CONTENT, ugettext('Improper content')),
    (SPAM, ugettext('Spam')),
    (TROLL, ugettext('Trolling')),
    (OTHER, ugettext('Other reason')),
    )

FLAG_NEW = 2**1
FLAG_READEN = 2**2

PVT_MESSAGE_CH = (
    (FLAG_NEW, ugettext('New message')),
    (FLAG_READEN, ugettext('Readen')),
    )

NICK_NOVICE = 0
NICK_MEDIUM = 1
NICK_HIGH = 2
NICK_MASTER = 3
NICK_CH = (
    (NICK_NOVICE, ugettext('Slave')),
    (NICK_MEDIUM, ugettext('Padawan')),
    (NICK_HIGH, ugettext('Jedi')),
    (NICK_MASTER, ugettext('Lord Siph')),
)