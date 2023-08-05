from django.db import models
from ptree.fields import RandomCharField
import ptree.constants as constants
from django.template import defaultfilters
import random
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from ptree.session.models import Session
from ptree.common import id_label_name

class BaseExperiment(models.Model):
    """
    Base class for all Experiments.
    """

    label = models.CharField(max_length = 500,
                            null = True,
                            blank = True,
                            )
    code = RandomCharField(length=8)
    experimenter_access_code = RandomCharField(length=8)

    session = models.ForeignKey(Session,
                                                related_name = '%(app_label)s_%(class)s',
                                                null=True)

    next_experiment_content_type = models.ForeignKey(ContentType,
                                                     null=True,
                                                     related_name = '%(app_label)s_%(class)s_as_next_experiment')
    next_experiment_object_id = models.PositiveIntegerField(null=True)
    next_experiment = generic.GenericForeignKey('next_experiment_content_type',
                                            'next_experiment_object_id',)

    previous_experiment_content_type = models.ForeignKey(ContentType,
                                                     null=True,
                                                     related_name = '%(app_label)s_%(class)s_as_previous_experiment')
    previous_experiment_object_id = models.PositiveIntegerField(null=True)
    previous_experiment = generic.GenericForeignKey('previous_experiment_content_type',
                                            'previous_experiment_object_id',)

    def is_last_experiment(self):
        return not self.next_experiment

    def name(self):
        return id_label_name(self.pk, self.label)

    def __unicode__(self):
        return self.name()

    def experimenter_input_url(self):
        return '/{}/ExperimenterLaunch/?{}={}&{}={}'.format(self.url_base,
                                                          constants.experiment_code,
                                                          self.code,
                                                          constants.experimenter_access_code,
                                                          self.experimenter_access_code)

    def start_url(self):
        """The URL that a user is redirected to in order to start a treatment"""
        return '/{}/Initialize/?{}={}'.format(self.url_base,
                                              constants.participant_code,
                                              self.code)


    def pick_treatment_for_incoming_participant(self):
        # find an open match and see what treatment it's part of.
        try:
            return [m for m in self.matches() if m.is_ready_for_next_participant()][0].treatment
        except IndexError:
            #return super(Experiment, self).pick_treatment_for_incoming_participant()
            treatments = list(self.treatments())
            random.shuffle(treatments)
            return min(treatments, key=lambda treatment: len(treatment.participants()))

    def treatments(self):
        return self.treatment_set.all()

    def matches(self):
        return self.match_set.all()

    def participants(self):
        return self.participant_set.all()

    def experimenter_sequence_of_views(self):
        raise NotImplementedError()

    def experimenter_sequence_as_urls(self):
        """Converts the sequence to URLs.

        e.g.:
        sequence() returns something like [views.IntroPage, ...]
        sequence_as_urls() returns something like ['mygame/IntroPage', ...]
        """
        return [View.url() for index, View in enumerate(self.experimenter_sequence_of_views())]

    class Meta:
        abstract = True
        ordering = ['pk']