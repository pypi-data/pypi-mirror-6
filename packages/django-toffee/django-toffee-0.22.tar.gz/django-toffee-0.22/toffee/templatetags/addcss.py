from django import template

register = template.Library()


@register.filter(name='addcss')
def addcss(field, css):
    return field.as_widget(attrs={"class": css})


@register.filter(name='titlify')
def titlify(field):
    if "__" in field:
        field = field.split("__")[0]
    elif field.lower() == 'id':
        return 'ID'
    return field.replace('_', ' ').title()