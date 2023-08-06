from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.sites.models import Site

from registration import models, signals
from registration.forms import CustomRegistrationForm
from registration.views import RegistrationView as BaseRegistrationView


class RegistrationView(BaseRegistrationView):
    """A registration backend that implements a workflow for users that want to
    create their own custom user model.
    This most closely resembles the simple backend, since custom users will
    likely have a lot of logic that is outside the scope for this backend.
    """
    form_class = CustomRegistrationForm
    model = get_user_model()

    def register(self, request, **cleaned_data):
        """Register the user.
        """
        self.create_user(request, **cleaned_data)

        auth_args = {
            'username': cleaned_data[self.model.USERNAME_FIELD],
            'password': cleaned_data['password1'],
        }
        new_user = authenticate(**auth_args)

        login(request, new_user)

        signals.user_registered.send(
            sender=self.__class__, user=new_user, request=request)
        return new_user

    def create_user(self, request, **cleaned_data):
        """Custom create_user method. This is meant to be overridden if you
        want to pass extra form fields when creating a user.
        By default, this method assumes you only need username_field and
        password.
        """
        create_kwargs = {
            self.model.USERNAME_FIELD: cleaned_data[self.model.USERNAME_FIELD],
            'password': cleaned_data['password1'],
            'site': Site.objects.get_current(),
        }
        models.RegistrationProfile.objects.create_inactive_user(
            **create_kwargs)

    def get_success_url(self, request, user):
        return ('registration_complete', (), {})
