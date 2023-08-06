from django.forms import ModelMultipleChoiceField
from .widgets import TagInput
from .models import Tag


class TagField(ModelMultipleChoiceField):
    """A Typeahead Multiple choice field for Tags"""

    def __init__(self, cache_choices=False, required=False,
                 label=None, initial=None, help_text='', *args, **kwargs):
        super(TagField, self).__init__(self, Tag.objects.all(),
                 required=required, widget=TagInput, label=label,
                 initial=initial, help_text=help_text, *args, **kwargs)

        self.queryset = Tag.objects.all()
