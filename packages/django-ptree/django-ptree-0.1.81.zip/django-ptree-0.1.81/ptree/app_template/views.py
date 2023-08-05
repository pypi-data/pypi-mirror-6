import ptree.views
import ptree.views.concrete
import {{ app_name }}.forms as forms
from {{ app_name }}.utilities import ViewInThisApp
from django.utils.translation import ugettext as _
from django.conf import settings
from ptree.common import currency

class GetTreatmentOrParticipant(ViewInThisApp, ptree.views.GetTreatmentOrParticipant):
    pass

class Start(ViewInThisApp, ptree.views.Start):
    template_name = 'Start.html'
    form_class = forms.StartForm

# change the name as necessary
class MyView(ViewInThisApp, ptree.views.UpdateView):

    form_class = forms.MyForm
    template_name = '{{ app_name }}/MyView.html'

    def show_skip_wait(self):
        return self.PageActions.show

    def variables_for_template(self):
        return {}

    def after_valid_form_submission(self):
        """If all you need to do is save the form to the database,
        this can be left blank or omitted."""

class Results(ViewInThisApp, ptree.views.UpdateView):
    template_name = 'Results.html'

    def variables_for_template(self):
        return {'redemption_code': self.participant.external_id or self.participant.code,
                'base_pay': currency(self.treatment.base_pay),
                'bonus': currency(self.participant.bonus()),
                'total_pay': currency(self.participant.total_pay()),
                'another_experiment': not self.experiment.is_last_experiment()}