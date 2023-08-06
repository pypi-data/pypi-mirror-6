from django.conf import settings as django_settings

"""Image Sizes"""
IMAGE_SIZES = (
    (320, 240),
    (900, 600))

"""rss title"""
RSS_TITLE = getattr(
    django_settings,
    'OMBLOG_RSS_TITLE',
    'RSS Feed')

"""rss link"""
RSS_LINK = getattr(
    django_settings,
    'OMBLOG_RSS_LINK',
    '/blog/')

"""cache timeout"""
CACHE_TIMEOUT = getattr(
    django_settings,
    'OMBLOG_CACHE_TIMEOUT',
    60)

"""Cache Enabled?"""
CACHE_ENABLED = getattr(
    django_settings,
    'OMBLOG_CACHE_ENABLED',
    True)

"""Cache prefix"""
CACHE_PREFIX = getattr(
    django_settings,
    'OMBLOG_CACHE_PREFIX',
    'omblog_')


"""Show the hidden if logged in"""
SHOW_HIDDEN_IF_LOGGED_IN = getattr(
    django_settings,
    'OMBLOG_SHOW_HIDDEN_IF_LOGGED_IN',
    True)

"""Total items to show on the index page"""
INDEX_ITEMS = getattr(
    django_settings,
    'OMBLOG_INDEX_ITEMS',
    20)
