from django.conf import settings
gettext = lambda s: s

TESTIMONY_TEMPLATES = getattr(settings, 'TESTIMONY_TEMPLATES',
    (
        ('testimony/list_default.html', gettext('Default list (stationary)')),
        ('testimony/rotator.html', gettext('Continuous scroll (animated)')),
        ('testimony/vticker.html', gettext('Scroll and pause (animated)')),
    )
)

