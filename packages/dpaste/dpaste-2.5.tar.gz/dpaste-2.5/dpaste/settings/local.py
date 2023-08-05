from dpaste.settings import *
from django.utils.html import mark_safe

def dpaste_about(request):
    return {
        'DPASTE_ABOUT_EXTRA': mark_safe("""
        <h3>Imprint</h3>

        <p><strong>Address:</strong></p>
        <p>
            Martin Mahner<br>
            Lauterbacher Str. 4<br>
            DE-18581 Putbus<br>
            Germany
        </p>

        <p><strong>Jabber/E-Mail:</strong></p>
        <p><a href="mailto:martin@mahner.org">martin@mahner.org</a></p>
    """)
    }

TEMPLATE_CONTEXT_PROCESSORS += ('dpaste.settings.local.dpaste_about',)

DPASTE_SLUG_LENGTH = 16


ugettext = lambda s: s
DPASTE_EXPIRE_CHOICES = (
    ('onetime', ugettext(u'One Time Snippet')),
    (3600, ugettext(u'In one hour')),
    (3600 * 24 * 7, ugettext(u'In one week')),
    (3600 * 24 * 30, ugettext(u'In one month')),
    ('never', ugettext(u'Never')),
)
