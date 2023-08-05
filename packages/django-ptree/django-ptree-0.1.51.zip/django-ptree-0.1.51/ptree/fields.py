import itertools
import random
import string
from django.db import models
from django import forms

def string_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

class RandomCharField(models.CharField):
    """
    We use this for participant code, treatment code, experiment code
    generates gibberish pronounceable words, like 'satonoha' or 'gimoradi'

    # See https://derrickpetzold.com/p/auto-random-character-field-django/
    """

    vowels = list('aeiou')
    consonants = list(set(string.ascii_lowercase) - set(vowels) - set('qxcyw'))

    def find_unique(self, model_instance, value, callback, *args):
        # exclude the current model instance from the queryset used in finding
        # next valid hash
        queryset = model_instance.__class__._default_manager.all()
        if model_instance.pk:
            queryset = queryset.exclude(pk=model_instance.pk)

        # form a kwarg dict used to implement any unique_together constraints
        kwargs = {}
        for params in model_instance._meta.unique_together:
            if self.attname in params:
                for param in params:
                    kwargs[param] = getattr(model_instance, param, None)
        kwargs[self.attname] = value

        while queryset.filter(**kwargs):
            value = callback()
            kwargs[self.attname] = value
        return value

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('blank', True)
        self.length = kwargs.pop('length', 8)
        kwargs['max_length'] = self.length

        super(RandomCharField, self).__init__(*args, **kwargs)

    def generate_chars(self, *args, **kwargs):
        chars = []
        n = self.length
        char_sets = [self.consonants, self.vowels]
        for char_set in itertools.cycle(char_sets):
            n -= 1
            if n < 0:
                break
            chars.append(random.choice(char_set))

        return ''.join(chars)

    def pre_save(self, model_instance, add):
        if not add:
            return getattr(model_instance, self.attname)

        initial = self.generate_chars()
        value = self.find_unique(model_instance, initial, self.generate_chars)
        setattr(model_instance, self.attname, value)
        return value

    def get_internal_type(self):
        return "CharField"

class _RequiredNullBooleanFormField(forms.NullBooleanField):
    def clean(self, value):
        if value is None:
            raise forms.ValidationError('Choose either Yes or No.')
        return super(_RequiredNullBooleanFormField, self).clean(value)

class RequiredNullBooleanField(models.NullBooleanField):
    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        defaults = {'form_class': _RequiredNullBooleanFormField}
        defaults.update(kwargs)
        return super(RequiredNullBooleanField, self).formfield(**defaults)

