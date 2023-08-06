from django.forms.widgets import Widget
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string


class BaseWidget(Widget):

    defaults = {}

    def __init__(self, attrs=None):

        _attrs = self.defaults.copy()

        if attrs:
            _attrs.update(attrs)

        super(BaseWidget, self).__init__(attrs=_attrs)

    @property
    def template_name(self):

        raise NotImplementedError

    def build_attrs(self, extra_attrs=None, **kwargs):

        return super(BaseWidget, self).build_attrs(
            extra_attrs=extra_attrs, **kwargs)

    """ Base widget that renders a template """

    def render(self, name, value, attrs=None):

        final_attrs = self.build_attrs(attrs, name=name, value=value)

        html = render_to_string(self.template_name, final_attrs)

        return mark_safe(u"".join(html))


class InOutWidget(BaseWidget):

    """ Widget that handles data with add and remove lists. The
    incoming data should have <name>_add and <name>_rm values,
    sepratated by 'separator'. """

    separator = ";;"

    def convert_item(self, item):

        """ Convert a single incoming value value to the actual value """

        return item

    def value_from_datadict(self, data, files, name):

        """ The data may contain a list of objects to remove, and
        objects to add. Both are prefixed by the field name. The
        returned value is a dict with 'rm' and 'add' lists, that list
        the """

        result = {'rm': [], 'add': []}

        for item in data.get("%s_rm" % name, "").split(self.separator):

            try:
                obj = self.convert_item(item)
                result['rm'].append(obj)
            except:
                pass

        for item in data.get("%s_add" % name, "").split(self.separator):

            try:
                obj = self.convert_item(item)
                result['add'].append(obj)
            except:
                pass

        return result
