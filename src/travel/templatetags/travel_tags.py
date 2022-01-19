from django import template
from django.utils.safestring import mark_safe

register = template.Library()


class HavingNode(template.Node):

    def __init__(self, having_var, context_var, nodelist, nodelist_else):
        self.having_var = having_var
        self.context_var = context_var
        self.nodelist = nodelist
        self.nodelist_else = nodelist_else

    def render(self, context):
        value = self.having_var.resolve(context)
        if value:
            with context.push(**{self.context_var: value}):
                return self.nodelist.render(context)

        if self.nodelist_else:
            return self.nodelist_else.render(context)

        return ''


@register.tag('having')
def do_having(parser, token):
    having_err_msg = "'having' statements should use the format 'having x as y': '{}'"
    bits = token.split_contents()
    if len(bits) < 4:
        raise template.TemplateSyntaxError(having_err_msg.format(token.contents))

    tag_name, having_var, _as, context_var = bits
    having_var = parser.compile_filter(having_var)
    if _as != 'as':
        raise template.TemplateSyntaxError(having_err_msg.format(token.contents))

    nodelist = parser.parse(('else', 'endhaving',))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_else = parser.parse(('endhaving',))
        parser.delete_first_token()
    else:
        nodelist_else = None

    return HavingNode(having_var, context_var, nodelist, nodelist_else)


ICON_MAPPINGS = {
    'edit': 'pencil-square',
    'new-window': 'window-plus',
    'globe': 'globe2',
    'user': 'person-fill',
    'check-circle': 'check-circle-fill',
}


@register.simple_tag
def travel_icon(name):
    name = ICON_MAPPINGS.get(name, name)
    return mark_safe(f'<i class="bi bi-{name}"></i>')
