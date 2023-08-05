from django.forms import Widget
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from .models import Tag

class TagInput(Widget):
    def render(self, name, value, attrs=None):
        return mark_safe( render_to_string('bootstrap-tags.html', {
            'name': name,
            'value': value,
            'attrs': attrs,
            'tags': Tag.objects.all(),
        }) )

    class Media:
        css = {
            'all': (
                'css/bootstrap-tags.css',
            )
        }
        js = (
            'js/bootstrap3-typeahead.min.js',
            'js/bootstrap-tags.js',
        )