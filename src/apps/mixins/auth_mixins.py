
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from django.views import View

class BaseLoginRequiredView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    redirect_field_name = 'next'




class VendorRequiredMixin(LoginRequiredMixin):
    """
    Mixin that requires the user to be logged in and to be a vendor.
    """

    def dispatch(self, request, *args, **kwargs):
        # Call the parent dispatch method to check if the user is logged in
        super().dispatch(request, *args, **kwargs)

        # Check if the user has a related Vendor instance
        if not hasattr(request.user, 'vendor'):
            raise PermissionDenied("You must be a vendor to access this page.")

        return super().dispatch(request, *args, **kwargs)