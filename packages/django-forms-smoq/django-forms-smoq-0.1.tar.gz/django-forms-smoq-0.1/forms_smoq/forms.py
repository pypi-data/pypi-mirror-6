from django.forms import ModelForm, ChoiceField
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models.loading import get_model

GENERIC_DEFAULT_MODEL = getattr(settings, 'GENERIC_DEFAULT_MODEL', None)


class GenericAdminForm(ModelForm):
    content_object = ChoiceField(choices=(("", '-------'),))

    class Meta:
        exclude = ('content_type', 'object_id')

    def __init__(self, *args, **kwargs):
        super(GenericAdminForm, self).__init__(*args, **kwargs)
        self.fields['content_object'].choices = self._get_choices()
        self.fields[
            'content_object'].label = self.get_model()._meta.verbose_name
        self.fields['content_object'].initial = self.instance.object_id

    def _get_choices(self):
        li = [("", "----------")]
        for pt in self.get_model().objects.all():
            li.append((pt.id, unicode(pt)))
        return li

    def get_model(self):
        name = 'GENERIC_%s_MODEL' % str(self._meta.model.__name__).upper()
        model_settings = getattr(settings, name, None)
        if model_settings:
            split = model_settings.split(".")
        else:
            split = GENERIC_DEFAULT_MODEL.split(".")
        return get_model(app_label=split[0], model_name=split[1])

    def get_content_type(self):
        return ContentType.objects.get_for_model(self.get_model())

    def save(self, commit=True):
        self.instance.object_id = self.cleaned_data['content_object']
        self.instance.content_type = self.get_content_type()
        obj = super(GenericAdminForm, self).save(commit=commit)
        return obj


class NoGenericAdminForm(ModelForm):
    pass


if GENERIC_DEFAULT_MODEL:
    AdminGenericForm = GenericAdminForm
else:
    AdminGenericForm = NoGenericAdminForm

