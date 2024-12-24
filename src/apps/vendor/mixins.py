from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin


class CheckVendorMixin(LoginRequiredMixin):
    """
    Mixin to check if the user is a vendor and if the vendor is verified.
    Redirect to become-vendor if not, or to an error page if not verified.
    """

    def dispatch(self, request, *args, **kwargs):
        # Check if the user has a related Vendor instance
        if not hasattr(request.user, 'vendor'):
            messages.error(request, 'You are not a vendor')
            return redirect('vendor:become-vendor')  # Redirect to become-vendor if not a vendor

        vendor = request.user.vendor

        # Check if the vendor is verified
        if not vendor.verification_status:
            messages.error(request, 'Your vendor has not verified yet.')
            return redirect('core:home')

        return super().dispatch(request, *args, **kwargs)