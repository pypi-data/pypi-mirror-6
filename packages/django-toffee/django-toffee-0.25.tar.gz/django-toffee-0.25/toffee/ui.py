from helpers import NavItemTypeError, AbstractNavItem, LinkItem


class Div(object):
    children = []

    def add_children(self, children):
        not_allowed = filter(lambda child: not issubclass(type(child), self.child_type), children)
        if not_allowed:
            raise NavItemTypeError("Unsupported Navigation Item.")
        self.children += children


class Navbar(Div):
    def __init__(self, children, nav_type="pills", fixed_to_top=True, inverted=False, justified=False, align='left'):
        self.children = children
        self.nav_type = nav_type
        self.fixed_to_top = fixed_to_top
        self.inverted = inverted
        self.justified = justified
        self.child_type = AbstractNavItem
        self.align = align


class Content(Div):
    def __init__(self, children, title='', width=9, align='left'):
        self.children = children
        self.align = align
        self.child_type = LinkItem
        self.width = width
        self.title = title


class Sidebar(Div):
    def __init__(self, children, affix=False, width=3, align='left'):
        self.children = children
        self.affix = affix
        self.align = align
        self.child_type = LinkItem
        self.width = width


class Footer(Div):
    def __init__(self, children, align='center'):
        self.children = children
        self.align = align