from django.template import Library, Node, TemplateSyntaxError

register = Library()

@register.tag(name="sneak_peek")
def sneak_peek(parser, token):
    tag = None
    style = '"default"'
    try:
        tag, style = token.split_contents()
    except ValueError:
        pass
    if not (style[0] == style[-1] and style[0] in ('"', "'")):
        raise TemplateSyntaxError("%r tag's argument should be in quotes" % tag)
    nodelist = parser.parse(('endsneak_peek',))
    parser.delete_first_token()
    return SneakPeekWrapper(nodelist, style[1:-1])


class SneakPeekWrapper(Node):
    def __init__(self, nodelist, style):
        self.nodelist = nodelist
        self.style = style

    def render(self, context):
        user = context['user']
        user_is_blessed = user.has_perm('sneak_peek_tag.can_view_sneak_peek')

        if user_is_blessed:
            content = self.nodelist.render(context)
            wrapped_hidden_feature = """<div class="django-sneak-peek %s">
                	%s
                </div>""" % (self.style, content)
            return wrapped_hidden_feature
        else:
            return ''
