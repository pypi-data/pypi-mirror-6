import sys

from django.conf import settings
from django.utils.importlib import import_module

from ptree.sessionlib.models import Session, SessionExperimenter, SessionParticipant
from ptree.user.models import Experimenter

def create(label, is_for_mturk, subsession_names, base_pay, num_participants):
    session = Session(label=label,
                                is_for_mturk=is_for_mturk,
                                base_pay=base_pay)

    session.save()

    if len(subsession_names) == 0:
        raise ValueError('Need at least one subsession.')

    try:
        session_experimenter = SessionExperimenter()
        session_experimenter.save()
        session.session_experimenter = session_experimenter

        session_participants = []
        for i in range(num_participants):
            participant = SessionParticipant(session = session)
            participant.save()
            session_participants.append(participant)

        subsessions = []
        for app_name in subsession_names:
            if app_name not in settings.INSTALLED_PTREE_APPS:
                print 'Before running this command you need to add "{}" to INSTALLED_PTREE_APPS.'.format(app_name)
                return

            models_module = import_module('{}.models'.format(app_name))
            subsession = models_module.create_subsession_and_treatments()
            subsession.save()
            [t.save() for t in subsession.treatments()]

            session.add_subsession(subsession)
            experimenter = Experimenter(session=session)
            experimenter.subsession = subsession
            subsession.experimenter = experimenter
            experimenter.save()
            for i in range(num_participants):
                participant = models_module.Participant(subsession = subsession,
                                                        session = session,
                                                        session_participant = session_participants[i])
                participant.save()

            print 'Created objects for {}'.format(app_name)
            subsessions.append(subsession)


        session.chain_subsessions(subsessions)
        session.chain_participants()
        session.session_experimenter.chain_experimenters()
    except:
        session.delete()
        raise