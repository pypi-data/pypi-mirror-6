# -*- coding: utf-8 -*-
from django.conf import settings
from django.forms.widgets import TextInput
from django.utils.safestring import SafeText

try:
    url = settings.STATIC_URL
except AttributeError:
    try:
        url = settings.MEDIA_URL
    except AttributeError:
        url = ''


class ColorFieldWidget(TextInput):
    class Media:
        css = {
            'all': ("{0}colorful/colorPicker.css".format(url),)
        }
        js = ("{0}colorful/jquery.colorPicker.js".format(url),)

    input_type = 'color'

    # def __init__(self, *args, **kwargs):
    #     super(ColorFieldWidget, self).__init__(*args, **kwargs)

    def render_script(self, id):
        return u'''<script type="text/javascript">
                    (function($){
                        $(document).ready(function(){
                            $('#%s').each(function(i, elm){
                                // Make sure html5 color element is not replaced
                                if (elm.type != 'color') $(elm).colorPicker();
                            });
                        });
                    })('django' in window ? django.jQuery: jQuery);
                </script>
                ''' % id

    def render(self, name, value, attrs={}):
        if not 'id' in attrs:
            attrs['id'] = "#id_{}".format(name)
        render = super(ColorFieldWidget, self).render(name, value, attrs)
        return SafeText(u"{}{}".format(render, self.render_script(attrs['id'])))
