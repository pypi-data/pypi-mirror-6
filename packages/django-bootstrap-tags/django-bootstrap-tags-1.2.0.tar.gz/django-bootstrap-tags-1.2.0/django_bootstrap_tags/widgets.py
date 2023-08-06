from django.forms import SelectMultiple
from django.utils.text import slugify
from .models import Tag


class TagInput(SelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        new_attrs = {
            'class': 'tag-input'
        }
        if attrs:
            new_attrs.update(attrs)

        return super(TagInput, self).render(
            name=name,
            value=value,
            attrs=new_attrs,
            choices=choices
        )

    def value_from_datadict(self, data, files, name):
        value = []
        for tag in data.getlist(name):
            try:
                int(tag)
            except ValueError:
                try:
                    t = Tag.objects.get(slug=slugify(tag))
                except Tag.DoesNotExist:
                    t = Tag()
                    t.tag = tag
                    t.slug = slugify(tag)
                    t.save()
                tag = u'%i' % t.pk
            value.append(tag)
        return value

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
