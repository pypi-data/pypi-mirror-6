__doc__ = """This module contains views that are shared across many game types. 
They are ready to be included in your  Just import this module,
and include these classes in your Treatment's sequence() method."""

from django.shortcuts import render_to_response

from django.conf import settings

import ptree.views.abstract
import ptree.forms

class RedirectToPageUserShouldBeOn(ptree.views.abstract.BaseView):
    url_base = 'shared'

    def get(self, request, *args, **kwargs):
        return self.redirect_to_page_the_user_should_be_on()

class InitializeSequence(ptree.views.abstract.InitializeSequence):
    pass
