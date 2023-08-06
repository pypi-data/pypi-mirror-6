from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView


class ProfileView(TemplateView):
    template_name = 'account/profile.html'

profile = login_required(
    ProfileView.as_view()
)
