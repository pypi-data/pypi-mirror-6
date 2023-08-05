"""Views for the aps_bom app."""
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404
from django.views.generic import CreateView, TemplateView
from django.utils.decorators import method_decorator

from . import settings
from .forms import BOMUploadForm, CBOMUploadForm
from .models import CBOM


class BOMDownloadView(TemplateView):
    """
    View that displays a CBOM translated into BOM and allows downloading the
    BOMItem list as BOM.csv.

    """
    template_name = 'aps_bom/bom_download.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        try:
            self.cbom = CBOM.objects.get(pk=kwargs.get('cbom_pk'))
        except CBOM.DoesNotExist:
            raise Http404
        return super(BOMDownloadView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(BOMDownloadView, self).get_context_data(**kwargs)
        ctx.update({
            'object': self.cbom,
            'bom': self.cbom.get_bom(),
            'bom_items': self.cbom.get_bom_items(),
            'csv_file': self.cbom.get_bom_csv_file(),
        })
        return ctx


class BOMUploadView(CreateView):
    """
    Lets a user upload a BOM.csv file and from it create a new BOM instance.

    """
    form_class = BOMUploadForm
    template_name = 'aps_bom/bom_upload.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(BOMUploadView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(BOMUploadView, self).get_form_kwargs()
        kwargs.update({'files': self.request.FILES})
        return kwargs

    def get_success_url(self):
        return settings.BOM_UPLOAD_SUCCESS_URL


class CBOMUploadView(CreateView):
    """
    Lets a user upload a cBOM.csv file and from it create a new CBOM instance.

    """
    form_class = CBOMUploadForm
    template_name = 'aps_bom/cbom_upload.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CBOMUploadView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(CBOMUploadView, self).get_form_kwargs()
        kwargs.update({'files': self.request.FILES})
        return kwargs

    def get_success_url(self):
        return reverse('aps_bom_bom_download', kwargs={
            'cbom_pk': self.object.pk})
