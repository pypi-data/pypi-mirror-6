from django import template
from django.conf import settings
from django.utils.translation import ugettext as _

register = template.Library()


@register.simple_tag(takes_context=True)
def querystring(context, **kwargs):
    args = context['request'].GET.copy()
    for k, v in kwargs.iteritems():
        args[k] = v
    return args.urlencode()


SORT_FIELD = getattr(settings, 'SORT_FIELD', 'o')
SORT_UP_ICON = getattr(settings, 'SORT_UP_ICON', '&uarr;')
SORT_DOWN_ICON = getattr(settings, 'SORT_DOWN_ICON', '&darr;')

sort_directions = {
    'asc': {'icon': SORT_UP_ICON, 'inverse': 'desc'},
    'desc': {'icon': SORT_DOWN_ICON, 'inverse': 'asc'},
    '': {'icon': SORT_DOWN_ICON, 'inverse': 'asc'},
}


def sortanchor(parser, token):
    """
    Parses a tag that's supposed to be in this format
        '{% sortanchor field title [default] %}'
    Title may be a "string", _("trans string"), or variable
    """
    bits = [b for b in token.split_contents()]
    if len(bits) < 2:
        raise template.TemplateSyntaxError(
                        "anchor tag takes at least 1 argument.")

    title_is_var = False
    try:
        title = bits[2]
        if title[0] in ('"', "'"):
            if title[0] == title[-1]:
                title = title[1:-1]
            else:
                raise template.TemplateSyntaxError('sortanchor tag title '
                        'must be a "string", _("trans string"), or variable')
        elif title.startswith('_("') or title.startswith("_('"):
            title = _(title[3:-2])
        else:
            title_is_var = True
    except IndexError:
        title = bits[1].capitalize()

    if len(bits) > 3:
        default = bits[3]
    else:
        default = False

    return SortAnchorNode(bits[1].strip(), title.strip(), title_is_var,
                                        default)


class SortAnchorNode(template.Node):
    """
    Renders an <a> HTML tag with a link which href attribute
    includes the field on which we sort and the direction.
    and adds an up or down arrow if the field is the one
    currently being sorted on.

    Eg.
        {% sortanchor name Name %} generates
        <a href="/the/current/path/?sort=name" title="Name">Name</a>

    """
    def __init__(self, field, title, title_is_var, is_default):
        self.field = field
        self.title = title
        self.title_is_var = title_is_var
        self.is_default = is_default

    def render(self, context):
        if self.title_is_var:
            self.title = context[self.title]
        request = context['request']
        getvars = request.GET.copy()

        currentsort = ''
        sortby = self.field
        icon = False

        if SORT_FIELD in getvars:
            currentsort = getvars[SORT_FIELD]
        else:
            if self.is_default:
                if self.is_default == '-':
                    currentsort = '-' + self.field
                else:
                    currentsort = self.field

        if currentsort == self.field:
            sortby = "-" + self.field
            icon = SORT_DOWN_ICON

        if currentsort.startswith('-') and currentsort[1:] == self.field:
            icon = SORT_UP_ICON

        if icon:
            title = "%s %s" % (self.title, icon)
        else:
            title = self.title

        getvars[SORT_FIELD] = sortby

        url = '%s?%s' % (request.path, getvars.urlencode())
        return '<a href="%s" title="%s">%s</a>' % (url, self.title, title)


sortanchor = register.tag(sortanchor)
