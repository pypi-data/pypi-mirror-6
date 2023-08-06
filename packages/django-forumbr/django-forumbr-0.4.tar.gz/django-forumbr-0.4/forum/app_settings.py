# -*- coding:utf-8 -*-

from django.conf import settings
from .constants import KB, MB

MIN = 60

MARKUP_FORCE_SAFE_HTML = getattr(settings, 'FORUM_MARKUP_FORCE_SAFE_HTML', True)

# Markup language for threads and replies
# one of (plain text, bbcode, markdown, textile, restructuredtext, plain html)
MARKUP = getattr(settings, 'FORUM_MARKUP', 'plain text')

# Default: 120kb
MAX_THREAD_IMAGE_SIZE = getattr(settings, 'FORUM_MAX_THREAD_IMAGE_SIZE', 120 * KB)
# Default: 2mb
MAX_THREAD_ATTACH_SIZE = getattr(settings, 'FORUM_MAX_THREAD_ATTACH_SIZE', 2 * MB)

THREAD_ALLOW_IMAGE = getattr(settings, 'FORUM_THREAD_ALLOW_IMAGE', True)
THREAD_ALLOW_ATTACHMENT = getattr(settings, 'FORUM_THREAD_ALLOW_ATTACHMENT', True)

# max filesize for avatar image. Default: 40kb
AVATAR_MAX_SIZE = getattr(settings, 'FORUM_AVATAR_MAX_SIZE', 40 * KB)

# Can user edit reply?
EDIT_REPLY = getattr(settings, 'FORUM_EDIT_REPLY', False)
# How long, after posting can the user edit the reply? Set to None for unlimited time.
EDIT_REPLY_TIME_LIMIT = getattr(settings, 'FORUM_EDIT_REPLY_TIME_LIMIT', None)
# Add simple, inline reply functionality?
ALLOW_INLINE_REPLY = getattr(settings, 'FORUM_ALLOW_INLINE_REPLY', False)

# Requires clamav and pyclamd. Will complain otherwise.
CHECK_ATTACH_FOR_VIRUS = getattr(settings, 'FORUM_CHECK_ATTACHMENT_FOR_VIRUS', False)

# Pagination sizes
PAGINATE_THREADS_BY = getattr(settings, 'FORUM_PAGINATE_THREADS_BY', 16)
PAGINATE_REPLIES_BY = getattr(settings, 'FORUM_PAGINATE_REPLIES_BY', 12)
PAGINATE_MESSAGES_BY = getattr(settings, 'FORUM_PAGINATE_MESSAGES_BY', 20)

# Maximum number of messages an user can have in his message box
MESSAGE_BOX_SIZE = getattr(settings, 'FORUM_MESSAGE_BOX_SIZE', 40)

if CHECK_ATTACH_FOR_VIRUS:
    try:
        import pyclamd
    except ImportError:
        print('Option CHECK_ATTACH_FOR_VIRUS requires clamav and pyclamd installed.')
        exit(0)