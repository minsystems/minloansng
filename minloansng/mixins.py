from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url

from minloansng.decorators import ajax_required


class AjaxRequiredMixin(object):
    @method_decorator(ajax_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AjaxRequiredMixin, self).dispatch(request, *args, **kwargs)


class RequestFormAttachMixin(object):
    def get_form_kwargs(self):
        kwargs = super(RequestFormAttachMixin, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class NextUrlMixin(object):
    default_next = "/"

    def get_next_url(self):
        request = self.request
        next_ = request.GET.get('next')
        next_post = request.POST.get('next')
        redirect_path = next_ or next_post or None
        if is_safe_url(redirect_path, request.get_host()):
            return redirect_path
        return self.default_next


class GetObjectMixin(object):
    model = None

    def get_object(self, *args, **kwargs):
        slug = self.kwargs.get(self.slug_url_kwarg)
        ModelClass = self.model
        if slug is not None:
            try:
                obj = ModelClass.objects.get(slug=slug)
            except ModelClass.DoesNotExist:
                return redirect(reverse("404_"))
            except ModelClass.MultipleObjectsReturned:
                obj = ModelClass.objects.filter(slug=slug).first()
        else:
            obj = super(GetObjectMixin, self).get_object(*args, **kwargs)
        return obj


class IsUserOwnerMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if self.request.user != self.get_object().company.user.user:
            return HttpResponseRedirect(reverse('404_'))
        return super(IsUserOwnerMixin, self).dispatch(request, *args, **kwargs)


class IsUserCookieExists(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        cookieExists = request.COOKIES.get('sessionid')
        if not cookieExists:
            return redirect(reverse('minstore:welcome'))
        return super(IsUserCookieExists, self).dispatch(request, *args, **kwargs)