from django import forms
from django.forms.forms import NON_FIELD_ERRORS

# Custom Exceptions
class NavItemTypeError(Exception):
    pass


# Abstract Types
class AbstractNavItem(object):
    def __init__(self, *args, **kwargs):
        pass


class HTMLItem(object):
    def __init__(self, *arg, **kwargs):
        pass


# Generic HTML Items
class LinkItem(HTMLItem):
    def __init__(self, link, text, active='', icon=None):
        self.type = 'link'
        self.link = link
        self.text = text
        self.active = active
        self.icon = icon


class ImageItem(HTMLItem):
    def __init__(self, src, alt=None, responsive=True):
        self.type = 'image'
        self.src = src
        self.alt = alt
        self.responsive = responsive


class FormItem(forms.Form):
    type = 'form'
    action = ''
    method = 'POST'

    def add_error(self, error):
        self._errors[NON_FIELD_ERRORS] = self.error_class([error])


class DropdownItem(HTMLItem):
    def __init__(self, links, text):
        self.type = 'dropdown'
        self.text = text
        self.links = links


class ParagraphItem(HTMLItem):
    def __init__(self, text, alignment='left', heading='', is_alert=False, alert_type='danger'):
        self.type = 'paragraph'
        self.text = text
        self.heading = heading
        self.alignment = alignment
        self.is_alert = is_alert
        self.alert_type = alert_type


class DataTableItem(HTMLItem):
    def __init__(self):
        self.type = 'datatable'


class TableItem(HTMLItem):
    datatable_counter = 0

    # def __init__(self, url_param=None, model=None, columns=[], order_columns=[],
    #              pagination='full_numbers', length_menu=[[25, 50, 100, 200], [25, 50, 100, 200]],
    #              display_length=25, bStateSave="false"):
    def __init__(self, url_param=None, datatable_type='json', pagination='full_numbers', length_menu=[[25, 50, 100, 200], [25, 50, 100, 200]],
                 display_length=25, fields=[], heading = ''):
        self.datatable_counter = TableItem.datatable_counter
        TableItem.datatable_counter += 1
        self.type = 'table'
        # self.model = model
        # self.columns = columns
        # self.order_columns = order_columns
        self.datatable_type = datatable_type
        self.url_param = url_param
        self.pagination = pagination
        self.length_menu = length_menu
        self.display_length = display_length
        self.fields = fields
        self.heading = heading


# Navigation Items
class NavLinkItem(AbstractNavItem):
    def __init__(self, link, text, icon=None):
        self.type = 'link'
        self.link = link
        self.text = text
        self.icon = icon


class NavImageItem(AbstractNavItem):
    def __init__(self, src, alt=None, responsive=True):
        self.type = 'image'
        self.src = src
        self.alt = alt
        self.responsive = responsive


class NavFormItem(AbstractNavItem):
    def __init__(self, action, method, multipart=False):
        self.type = 'form'
        self.action = action
        self.method = method
        self.multipart = multipart


class NavDropdownItem(AbstractNavItem):
    def __init__(self, links, text):
        self.type = 'dropdown'
        self.text = text
        self.links = links


class NavItem(object):
    LINK_ITEM = 0
    IMAGE_ITEM = 1
    FORM = 2
    DROPDOWN = 3

    def __init__(self, item_type):
        self.item_type = item_type

    def __call__(self, **kwargs):
        if self.item_type == self.LINK_ITEM:
            return NavLinkItem(**kwargs)
        elif self.item_type == self.IMAGE_ITEM:
            return NavImageItem(**kwargs)
        elif self.item_type == self.FORM:
            return NavFormItem(**kwargs)
        elif self.item_type == self.DROPDOWN:
            return NavDropdownItem(**kwargs)
        else:
            raise NavItemTypeError("Unsupported Navigation Item.")
        