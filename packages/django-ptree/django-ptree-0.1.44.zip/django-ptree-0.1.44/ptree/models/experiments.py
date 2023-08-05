from django.db import models
import common
import ptree.constants as constants
from django.template import defaultfilters
import random
from django.conf import settings

class BaseExperiment(models.Model):
    """
    Base class for all Experiments.
    """

    name = models.CharField(max_length = 500, null = True, blank = True)
    code = common.RandomCharField(length=8)
    is_for_mturk = models.BooleanField(verbose_name='Is for MTurk', default=True)
    payment_was_sent = models.BooleanField(verbose_name='Payment was sent', default=False)
    experimenter_access_code = common.RandomCharField(length=8)

    def __unicode__(self):
        return self.name or str(self.pk)

    def experimenter_input_url(self):
        return '/{}/ExperimenterLaunch/?{}={}&{}={}'.format(self.url_base,
                                                          constants.experiment_code,
                                                          self.code,
                                                          constants.experimenter_access_code,
                                                          self.experimenter_access_code
                                                          )

    def start_url(self):
        """The URL that a user is redirected to in order to start a treatment"""
        return '/{}/GetTreatmentOrParticipant/?{}={}'.format(self.url_base,
                                                                      constants.experiment_code_obfuscated,
                                                                      self.code)


    def pick_treatment_for_incoming_participant(self):
        return random.choice(self.treatments())

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