__doc__ = """This module contains many of pTree's internals.
The view classes in this module are just base classes, and cannot be called from a URL.
You should inherit from these classes and put your view class in your game directory (under "games/")
Or in the other view file in this directory, which stores shared concrete views that have URLs."""

from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.context_processors import csrf
from django.conf import settings
import extra_views
import vanilla
import time
import ptree.constants as constants
import logging
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache, cache_control
from ptree.forms import StubModelForm
import ptree.session.models as seq_models
import ptree.session.models
import urllib
import urlparse
from django.utils.translation import ugettext as _
from django.db.models import Q
from ptree.common import assign_participant_to_match
from datetime import datetime

# Get an instance of a logger
logger = logging.getLogger(__name__)

REDIRECT_TO_PAGE_USER_SHOULD_BE_ON_URL = '/shared/RedirectToPageUserShouldBeOn/'

class ExperimentMixin(object):
    """Base mixin class for pTree views.
    Takes care of:
    - retrieving model classes and objects automatically,
    so you can access view.treatment, self.match, self.participant, etc.
    """

    def load_classes(self):
        self.ExperimentClass = self.request.session.get(constants.ExperimentClass)
        self.TreatmentClass = self.request.session.get(constants.TreatmentClass)
        self.ParticipantClass = self.request.session.get(constants.ParticipantClass)
        self.MatchClass = self.request.session.get(constants.MatchClass)

    def load_objects(self):
        self.participant = get_object_or_404(self.ParticipantClass,
            code = self.request.session.get(constants.participant_code))
        self.match = self.participant.match
        self.treatment = self.match.treatment
        self.experiment = self.treatment.experiment

    def save_objects(self):
        for obj in [self.match, self.participant, self.participant.session_participant]:
            if obj:
                obj.save()

    def dispatch(self, request, *args, **kwargs):
        self.load_classes()
        self.load_objects()
        return super(ExperimentMixin, self).dispatch(request, *args, **kwargs)

    @classmethod
    def get_url_base(cls):
        # look for url_base attribute on ExperimentClass
        # if it's not part of a game, but rather a shared module etc, ExperimentClass won't exist.
        # in that case, url_base needs to be defined on the class.
        return getattr(cls, 'ExperimentClass', cls).url_base

    @classmethod
    def url(cls):
        return '/{}/{}/'.format(cls.get_url_base(), cls.__name__)

    @classmethod
    def url_pattern(cls):
        return r'^{}/{}/$'.format(cls.get_url_base(), cls.__name__)

    def last_page_in_sequence_url(self):
        return 'last'

    def page_the_user_should_be_on(self):
        if self.participant.index_in_sequence_of_views >= len(self.treatment.sequence_as_urls()):
            if self.experiment.next_experiment:
                self.participant.session_participant.index_in_session += 1
                self.participant.session_participant.save()
                return self.participant.me_in_next_experiment.start_url()

        return self.treatment.sequence_as_urls()[self.participant.index_in_sequence_of_views]

    def redirect_to_page_the_user_should_be_on(self):
        """Redirect to where the participant should be,
        according to the view index we maintain in their cookies
        Useful if the participant tried to skip ahead,
        or if they hit the back button.
        We can put them back where they belong.
        """
        return HttpResponseRedirect(self.page_the_user_should_be_on())

    def variables_for_template(self):
        return {}

    def get_context_data(self, **kwargs):
        context = {}
        context.update(self.variables_for_template())
        return context

    def assign_participant_to_match(self):
        return assign_participant_to_match(self.MatchClass, self.participant)

class SequenceMixin(ExperimentMixin):
    """
    View that manages its position in the match sequence.
    """

    @classmethod
    def url(cls, index):
        return '/{}/{}/{}/'.format(cls.get_url_base(), cls.__name__, index)

    @classmethod
    def url_pattern(cls):
        return r'^{}/{}/(\d+)/$'.format(cls.get_url_base(), cls.__name__)


    success_url = REDIRECT_TO_PAGE_USER_SHOULD_BE_ON_URL

    class PageActions:
        show = 'show'
        skip = 'skip'
        wait = 'wait'

    def show_skip_wait(self):
        return self.PageActions.show

    # TODO: this is intended to be in the user's project, not part of pTree core.
    # but maybe have one in pTree core as a fallback in case the user doesn't have it.
    wait_page_template = 'ptree/WaitPage.html'

    def wait_page_body_text(self):
        pass

    def wait_page_title_text(self):
        pass

    def time_limit_in_seconds(self):
        return None

    def has_time_limit(self):
        return bool(self.time_limit_seconds())

    def set_time_limit(self, context):
        page_expiration_times = self.request.session[constants.page_expiration_times]
        if page_expiration_times.has_key(self.index_in_sequence_of_views):
            page_expiration_time = page_expiration_times[self.index_in_sequence_of_views]
            if page_expiration_time is None:
                remaining_seconds = None
            else:
                remaining_seconds = max(0, int(page_expiration_times[self.index_in_sequence_of_views] - time.time()))
        else:
            remaining_seconds = self.time_limit_in_seconds()

            if remaining_seconds is None:
                page_expiration_times[self.index_in_sequence_of_views] = None
            elif remaining_seconds > 0:
                page_expiration_times[self.index_in_sequence_of_views] = time.time() + remaining_seconds
            else:
                raise ValueError("Time limit must be None or a positive number.")

        print 'set: {}'.format(page_expiration_times)
        if remaining_seconds is not None:
            minutes_component, seconds_component = divmod(remaining_seconds, 60)
        else:
            minutes_component, seconds_component = None, None

        time_limit_parameters = {
            constants.time_limit_minutes_component: str(minutes_component),
            constants.time_limit_seconds_component: str(seconds_component).zfill(2),
            constants.time_limit_in_seconds: remaining_seconds,
        }

        context.update(time_limit_parameters)



    def get_time_limit_was_exceeded(self):
        page_expiration_times = self.request.session[constants.page_expiration_times]
        print 'get: {}'.format(page_expiration_times)
        page_expiration_time = page_expiration_times[self.index_in_sequence_of_views]

        if page_expiration_time is None:
            return False
        return time.time() > (page_expiration_time + settings.TIME_LIMIT_GRACE_PERIOD_SECONDS)

    def timer_message(self):
        pass

    @method_decorator(never_cache)
    @method_decorator(cache_control(must_revalidate=True, max_age=0, no_cache=True, no_store = True))
    def dispatch(self, request, *args, **kwargs):
        self.load_classes()
        self.load_objects()
        self.index_in_sequence_of_views = int(args[0])
        # remove it since post() may not be able to accept args.
        args = args[1:]

        # by default it's false (e.g. for GET requests), but can be set to True in post() method
        self.time_limit_was_exceeded = False

        page_action = self.show_skip_wait()
        if not page_action in [self.PageActions.show, self.PageActions.skip, self.PageActions.wait]:
            raise ValueError('show_skip_wait() must return one of the following: [self.PageActions.show, self.PageActions.skip, self.PageActions.wait]')

        if self.request.is_ajax() and self.request.GET[constants.check_if_wait_is_over] == constants.get_param_truth_value:
            no_more_wait = page_action != self.PageActions.wait
            return HttpResponse(int(no_more_wait))

        # if the participant shouldn't see this view, skip to the next
        if page_action == self.PageActions.skip:
            self.participant.index_in_sequence_of_views += 1
            self.participant.save()
            return self.redirect_to_page_the_user_should_be_on()

        # if the participant tried to skip past a part of the experiment
        # (e.g. by typing in a future URL)
        if not self.user_is_on_right_page():
            # then bring them back to where they should be
            return self.redirect_to_page_the_user_should_be_on()

        if page_action == self.PageActions.wait:
            return render_to_response(self.wait_page_template,
                {'SequenceViewURL': '{}?{}={}'.format(self.request.path,
                                                   constants.check_if_wait_is_over,
                                                   constants.get_param_truth_value),
                'debug_values': self.get_debug_values() if settings.DEBUG else None,
                'wait_page_body_text': self.wait_page_body_text(),
                'wait_page_title_text': self.wait_page_title_text()})
        return super(SequenceMixin, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.time_limit_was_exceeded = self.get_time_limit_was_exceeded()
        return super(SequenceMixin, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        context = {'form': kwargs['form']}
        context.update(self.variables_for_template())
        context['timer_message'] = self.timer_message()

        if settings.DEBUG:
            context[constants.debug_values] = self.get_debug_values()

        self.set_time_limit(context)
        self.save_objects()
        return context


    def get_debug_values(self):
        try:
            match_id = self.match.pk
        except:
            match_id = ''
        return [('Index among participants in match', self.participant.index_among_participants_in_match),
                ('Participant', self.participant.pk),
                ('Match', match_id),
                ('Treatment', self.treatment.pk),
                ('Experiment code', self.experiment.code),]


    def get_extra_form_kwargs(self):
        return {'participant': self.participant,
               'match': self.match,
               'treatment': self.treatment,
               'experiment': self.experiment,
               'request': self.request,
               'time_limit_was_exceeded': self.time_limit_was_exceeded}

    def get_form(self, data=None, files=None, **kwargs):
        """
        Given `data` and `files` QueryDicts, and optionally other named
        arguments, and returns a form.
        """
        kwargs.update(self.get_extra_form_kwargs())
        cls = self.get_form_class()
        return cls(data=data, files=files, **kwargs)


    def after_valid_form_submission(self):
        """Should be implemented by subclasses as necessary"""
        pass

    def update_index_in_sequence_of_views(self):
        if self.index_in_sequence_of_views == self.participant.index_in_sequence_of_views:
            self.participant.index_in_sequence_of_views += 1

    def post_processing_on_valid_form(self, form):
        pass

    def form_valid(self, form):
        self.form = form
        self.after_valid_form_submission()
        self.post_processing_on_valid_form(form)
        self.update_index_in_sequence_of_views()
        self.save_objects()
        return super(SequenceMixin, self).form_valid(form)

    def form_invalid(self, form):
        """

        """
        return self.render_to_response(self.get_context_data(form=form, form_invalid = True ))

    def user_is_on_right_page(self):
        """Will detect if a participant tried to access a page they didn't reach yet,
        for example if they know the URL to the redemption code page,
        and try typing it in so they don't have to play the whole game.
        We should block that."""

        return self.request.path == self.page_the_user_should_be_on()


class BaseView(ExperimentMixin, vanilla.View):
    """
    A basic view that provides no method implementations.
    """
    pass

class TemplateView(ExperimentMixin, vanilla.TemplateView):
    """
    A template view.
    """
    pass

class SequenceTemplateView(SequenceMixin, vanilla.TemplateView):
    """
    A sequence template view.
    """
    pass

class UpdateView(SequenceMixin, vanilla.UpdateView):

    # if form_class is not provided, we use an empty form based on StubModel.
    form_class = StubModelForm

    def post_processing_on_valid_form(self, form):
        # form.save will also get called by the super() method, so this is technically redundant.
        # but it means that you don't need to access cleaned_data in after_valid_form_submission,
        # which is a little more user friendly.
        form.save(commit = True)

    def get_object(self):
        Cls = self.get_form_class().Meta.model
        if Cls == self.MatchClass:
            return self.match
        elif Cls == self.ParticipantClass:
            return self.participant
        elif Cls == seq_models.StubModel:
            return seq_models.StubModel.objects.all()[0]
        else:
            # For AuxiliaryModels
            return Cls.objects.get(object_id=self.participant.id,
                                   content_type=ContentType.objects.get_for_model(self.participant))

class CreateView(SequenceMixin, vanilla.CreateView):
    def post_processing_on_valid_form(self, form):
        instance = form.save(commit=False)
        if hasattr(instance, 'participant'):
            instance.participant = self.participant
        if hasattr(instance, 'match'):
            instance.match = self.match
        instance.save()


class ModelFormSetView(extra_views.ModelFormSetView):
    extra = 0

    def formset_valid(self, formset):
        for form in formset:
            self.after_valid_form_submission()
            self.post_processing_on_valid_form(form)
        self.update_index_in_sequence_of_views()
        self.save_objects()
        return super(ModelFormSetView, self).formset_valid(formset)


class CreateMultipleView(extra_views.ModelFormSetView, CreateView):
    pass

class UpdateMultipleView(extra_views.ModelFormSetView, UpdateView):
    pass


class InitializeSessionParticipant(vanilla.UpdateView):

    @classmethod
    def url_pattern(cls):
        return r'^InitializeSessionParticipant/$'

    def get(self, *args, **kwargs):
        self.request.session.clear()

        sequence_code = self.request.GET.get(constants.session_code)
        participant_code = self.request.GET.get(constants.session_participant_code)

        if not participant_code or sequence_code:
            return HttpResponse('Missing parameter in URL')
        if participant_code and sequence_code:
            return HttpResponse('Redundant parameters in URL')

        if participant_code:
            session_participant = get_object_or_404(seq_models.SessionParticipant, code=participant_code)
            session = session_participant.session
        else:
            session = get_object_or_404(seq_models.Session, )
            if session.is_for_mturk:
                try:
                    mturk_worker_id = self.request.GET[constants.mturk_worker_id]
                    mturk_assignment_id = self.request.GET[constants.mturk_assignment_id]
                    assert mturk_assignment_id != 'ASSIGNMENT_ID_NOT_AVAILABLE'
                except:
                    print 'A visitor to this experiment was turned away because they did not have the MTurk parameters in their URL.'
                    print 'This URL only works if clicked from a MTurk job posting with the JavaScript snippet embedded'
                    return HttpResponse(_('To participate, you need to first accept this Mechanical Turk HIT and then re-click the link (refreshing this page will not work).'))
                try:
                    session_participant = seq_models.SessionParticipant.objects.get(mturk_worker_id = mturk_worker_id,
                                                                      session = session)
                except self.ParticipantClass.DoesNotExist:
                    try:
                        session_participant = seq_models.SessionParticipant.objects.filter(session = session,
                                                                             visited=False)[0]
                    except IndexError:
                        raise IndexError("No Participant objects left in the database to assign to new visitor.")

                    session_participant.mturk_worker_id = mturk_worker_id
                    session_participant.mturk_assignment_id = mturk_assignment_id

        session_participant.visited = True
        session_participant.time_started = datetime.now()

        participant_label = self.request.GET.get(constants.participant_label)
        if participant_label is not None:
            session_participant.label = participant_label

        if session_participant.ip_address == None:
            session_participant.ip_address = self.request.META['REMOTE_ADDR']

        session_participant.save()

        self.request.session[constants.session_participant_id] = session_participant.id
        self.session_participant = session_participant
        self.session = session

        return HttpResponseRedirect(session_participant.me_in_first_experiment.start_url())

class Initialize(vanilla.View):
    """
    The first View when participants visit a site.
    Doesn't have any UI.
    Just looks up the participant,
    decides what Treatment to randomize them to,
    and redirects to that Treatment.
    """

    def get_next_participant_in_experiment(self):
        try:
            return self.ParticipantClass.objects.filter(
                experiment=self.experiment,
                visited=False)[0]
        except IndexError:
            raise IndexError("No Participant objects left in the database to assign to new visitor.")

    def get(self, request, *args, **kwargs):
        self.request.session.clear()
        self.request.session[constants.page_expiration_times] = {}

        participant_code = self.request.GET.get(constants.participant_code)
        treatment_code = self.request.GET.get(constants.treatment_code)

        assert participant_code

        self.participant = None
        self.experiment = None
        self.treatment = None


        self.participant = get_object_or_404(self.ParticipantClass, code = participant_code)
        self.experiment = self.participant.experiment
        self.treatment = self.participant.treatment or self.experiment.pick_treatment_for_incoming_participant()
        self.participant.treatment = self.treatment

        self.participant.visited = True
        self.participant.time_started = datetime.now()

        self.participant.save()
        self.request.session[constants.participant_code] = self.participant.code
        self.request.session[constants.treatment_code] = self.treatment.code
        self.persist_classes()

        return HttpResponseRedirect(self.treatment.sequence_as_urls()[0])

    @classmethod
    def get_url_base(cls):
        """urls.py requires that each view know its own URL.
        a URL base is the first part of the path, usually the name of the game"""
        return cls.ExperimentClass.url_base

    @classmethod
    def url(cls):
        """What the URL looks like, so we can redirect to it"""
        return '/{}/{}/'.format(cls.get_url_base(), cls.__name__)

    @classmethod
    def url_pattern(cls):
        """URL pattern regular expression, as required by urls.py"""
        return r'^{}/{}/$'.format(cls.get_url_base(), cls.__name__)

    def persist_classes(self):
        """We need these classes so that we can load the objects.
        We need to store it in cookies,
        rather than relying on each View knowing its Experiment, Treatment, etc.
        Although this is the case with the views in the games (which inherit from their Start view),
        some Views are in a shared module and therefore can be bound to different Experiments, Treatments, etc.
        """

        self.request.session[constants.ExperimentClass] = self.ExperimentClass
        self.request.session[constants.TreatmentClass] = self.TreatmentClass
        self.request.session[constants.ParticipantClass] = self.ParticipantClass
        self.request.session[constants.MatchClass] = self.MatchClass