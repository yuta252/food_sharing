from django import template

register = template.Library()

@register.filter
def is_good_exists(obj, args):
    obj_list = obj.filter(message=args)
    if obj_list:
        return True
    else:
        return False