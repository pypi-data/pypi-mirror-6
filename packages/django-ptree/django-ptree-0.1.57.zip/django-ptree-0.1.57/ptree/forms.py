from django import forms
import ptree.common
import ptree.models.common
import ptree.sequence_of_experiments.models
from django.db import models
from django.utils.translation import ugettext as _

class FormMixin(object):

    # In general, pTree does not allow a user to go back and change their answer on a previous page,
    # since that often defeats the purpose of the game (e.g. eliciting an honest answer).
    # But you can put it in rewritable_fields to make it an exception.
    ## UPDATE: deprecated for now
    # rewritable_fields = []

    def field_initial_values(self):
        """Return a dict of any initial values"""
        return {}

    def field_choices(self):
        return {}

    def field_labels(self):
        return {}

    def customize(self):
        """Make any customizations to your field forms that are not covered by the other methods"""

    def currency_choices(self, amounts):
        return [(None, '--------')] + [(amount, ptree.common.currency(amount)) for amount in amounts]

    def __init__(self, *args, **kwargs):
        self.process_kwargs(kwargs)

        initial = kwargs.get('initial', {})
        initial.update(self.field_initial_values())
        kwargs['initial'] = initial
        super(FormMixin, self).__init__(*args, **kwargs)

        for field_name, label in self.field_labels().items():
            self.fields[field_name].label = label

        for field_name, choices in self.field_choices().items():
            field = self.fields[field_name]
            try:
                field.widget = field.widget.__class__(choices=choices)
            # if the current widget can't accept a choices arg, fall back to using a Select widget
            except TypeError:
                field.widget = forms.Select(choices=choices)
        self.customize()

    def null_boolean_field_names(self):
        null_boolean_fields_in_model = [field.name for field in self.Meta.model._meta.fields if field.__class__ == models.NullBooleanField]
        return [field_name for field_name in self.Meta.fields if field_name in null_boolean_fields_in_model]

    def clean(self):
        cleaned_data = super(FormMixin, self).clean()
        for field_name in self.null_boolean_field_names():
            if cleaned_data[field_name] == None:
                msg = _('This field is required.')
                self._errors[field_name] = self.error_class([msg])
        return cleaned_data

class ParticipantFormMixin(FormMixin):
    def process_kwargs(self, kwargs):
        self.participant = kwargs.pop('participant')
        self.match = kwargs.pop('match')
        self.treatment = kwargs.pop('treatment')
        self.experiment = kwargs.pop('experiment')
        self.request = kwargs.pop('request')
        self.time_limit_was_exceeded = kwargs.pop('time_limit_was_exceeded')

class ExperimenterFormMixin(FormMixin):
    def process_kwargs(self, kwargs):
        self.experiment = kwargs.pop('experiment')
        self.request = kwargs.pop('request')


class ModelForm(ParticipantFormMixin, forms.ModelForm):
    """
    Try to inherit from this class whenever you can.
    ModelForms are ofter preferable to plain Forms,
    since they take care of saving to the database,
    and they require less code to write and validate.
    """

class ExperimenterModelForm(ExperimenterFormMixin, forms.ModelForm):
    pass

class StubModelForm(ParticipantFormMixin, forms.ModelForm):
    class Meta:
        model = ptree.sequence_of_experiments.models.StubModel
        fields = []