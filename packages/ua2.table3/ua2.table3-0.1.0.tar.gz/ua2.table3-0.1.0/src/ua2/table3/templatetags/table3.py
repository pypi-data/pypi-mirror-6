from django import template

register = template.Library()

# http://stackoverflow.com/questions/5755150/altering-one-query-parameter-in-a-url-django
@register.simple_tag(takes_context=True)
def url_replace(context, field, *args):
    dict_ = context['request'].GET.copy()
    dict_[field] = ''.join(args)
    return dict_.urlencode()
