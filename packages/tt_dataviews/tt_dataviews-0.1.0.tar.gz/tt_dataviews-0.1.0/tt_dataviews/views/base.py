from django.views.generic.base import TemplateView

from . import mixins


class LandingView(mixins.NamedDataAppMixin, mixins.AppTagLineMixin,
        mixins.AppTitleMixin, mixins.LandingUrlMixin,
        mixins.LandingTemplateResponseMixin, TemplateView):
    """
    Default LandingView used for all Tribune explorers

    You must add strings for following three variables:

    * ``data_app_name``
    * ``app_tagline``
    * ``app_title``

    Next, add a template in ``{{ data_app_name }}/landing.html`` in
    your templates directory, then you're set.  You should generally
    extend ``layouts/data/landing.html``.

    """
    pass
