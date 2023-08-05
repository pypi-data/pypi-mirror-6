"""Documentation at http://django-ptree.readthedocs.org/en/latest/app.html"""

from django.db import models
import ptree.models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

class Experiment(ptree.models.BaseExperiment):

    # this will be in the URL users see,
    # so you may want to change it to a code name
    # if you don't want to reveal to users the name of the experiment.
    url_base = '{{ app_name }}'

class Treatment(ptree.models.BaseTreatment):
    experiment = models.ForeignKey(Experiment)

    # define any other attributes or methods here.
    
    def sequence_of_views(self):
    
        import {{ app_name }}.views as views
        return [views.Start,
                views.MyView, # insert your views here
                views.Results]
                
class Match(ptree.models.BaseMatch):

    treatment = models.ForeignKey(Treatment)
    experiment = models.ForeignKey(Experiment)

    def is_ready_for_next_participant(self):
        """You can change this if you want more complex behavior."""
        return len(self.participants()) < self.treatment.participants_per_match

    # define any other attributes or methods here.
            
class Participant(ptree.models.BaseParticipant):

    match = models.ForeignKey(Match, null = True)
    treatment = models.ForeignKey(Treatment, null = True)
    experiment = models.ForeignKey(Experiment)

    my_field = models.BooleanField(default=False)

    def bonus(self):
        # make sure this doesn't trigger an exception if the match isn't finished.
        # return None if the bonus cannot be calculated yet.
        return None
            
    # define any other attributes or methods here.
    

def create_experiment_and_treatments():

    experiment = Experiment()
    experiment.save()

    # you can create more treatments. just make a loop.
    treatment = Treatment(experiment = experiment,
                          base_pay = 100,
                          participants_per_match = 1,
                          # other attributes here...
                          )
    treatment.save()

    return experiment

