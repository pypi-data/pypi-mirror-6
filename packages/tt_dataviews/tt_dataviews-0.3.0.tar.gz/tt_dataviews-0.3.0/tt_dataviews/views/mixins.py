from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.views.generic.base import TemplateResponseMixin


def non_override_context_mixin(name):
    class NonOverrideContextMixin(object):
        def get_context_data(self, **kwargs):
            context = super(NonOverrideContextMixin, self).get_context_data(**kwargs)
            if name not in context:
                context[name] = getattr(self, 'get_%s' % name)()
            return context

    return NonOverrideContextMixin


class NamedDataAppMixin(non_override_context_mixin('data_app_name')):
    """
    Adds a ``data_app_name`` to the context

    Note: This will not override a previously set ``data_app_name`` in
    the context.
    """
    data_app_name = None

    def get_data_app_name(self):
        if self.data_app_name is None:
            raise ImproperlyConfigured(
                "You must provide a `data_app_name` or a custom "
                "`get_data_app_name` method for this view.")
        return self.data_app_name


class AppTagLineMixin(non_override_context_mixin('app_tagline')):
    """
    Adds an ``app_tagline`` to the context

    Note: This will not override a previously set ``app_tagline`` in
    the context.
    """
    app_tagline = None

    def get_app_tagline(self):
        if self.app_tagline is None:
            raise ImproperlyConfigured(
                "You must porvide an `app_tagline` or a custom "
                "`get_app_tagline` method for this view.")
        return self.app_tagline


class AppTitleMixin(non_override_context_mixin('app_title')):
    """
    Adds an ``app_title`` to the context

    Note: This will not override a previously set ``app_title`` in
    the context.
    """
    app_title = None

    def get_app_title(self):
        if self.app_title is None:
            raise ImproperlyConfigured(
                "You must provide an `app_title` or a custom "
                "`get_app_title` method for this view.")
        return self.app_title


class LandingUrlMixin(non_override_context_mixin('landing_url')):
    """
    Adds a ``landing_url`` context variable

    This requires a ``get_data_app_name`` method to be available,
    generally via ``NamedDataAppMixin``.  It assumes that there is a
    URL route named ``{{ app name }}:landing`` available.  You can
    override ``get_landing_url_name`` if you need to provide a
    different URL name.

    Note: This will not override a previously set ``landing_url`` in
    the context.
    """
    def get_landing_url_name(self):
        return '%s:landing' % self.get_data_app_name()

    def get_landing_url(self):
        return reverse(self.get_landing_url_name())


class LandingTemplateResponseMixin(TemplateResponseMixin):
    """
    Provides a default template name if nothing is provided

    This returns ``{{ data_app_name }}/landing.html`` as the template
    name if ``template_name`` was not automatically provided.
    """
    def get_template_names(self):
        try:
            return (super(LandingTemplateResponseMixin, self)
                    .get_template_names())
        except ImproperlyConfigured:
            # No explicit template_name was set, attempt to calculate it
            pass

        if not hasattr(self, 'get_data_app_name'):
            raise ImproperlyConfigured(
                "You must provide either a `get_data_app_name` method or "
                " specify an explicit `template_name` to use this view.")
        return ['%s/landing.html' % self.get_data_app_name(), ]
