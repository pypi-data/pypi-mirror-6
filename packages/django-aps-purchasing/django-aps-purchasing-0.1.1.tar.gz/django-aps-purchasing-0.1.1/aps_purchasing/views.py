"""Views of the ``aps_purchasing`` app."""
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView

from aps_bom.models import BOM

from .forms import QuotationUploadForm
from .models import Price, Quotation


class QuotationUploadView(CreateView):
    """View to upload a quotation and create Quotation items."""
    model = Quotation
    template_name = 'aps_purchasing/quotation_upload.html'
    form_class = QuotationUploadForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(QuotationUploadView, self).dispatch(
            request, *args, **kwargs)

    def get_success_url(self):
        return reverse('aps_purchasing_quotation_upload')


class ReportView(DetailView):
    """View to display prices and manufacturers belonging to a BOM."""
    template_name = 'aps_purchasing/report.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.object = None
        try:
            self.object = BOM.objects.get(pk=kwargs.get('pk'))
        except BOM.DoesNotExist:
            pass
        return super(ReportView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(ReportView, self).get_context_data(**kwargs)
        if self.object is not None:
            prices = Price.objects.filter(
                quotation_item__mpn__manufacturer__aml__ipn__boms=self.object)
            ctx.update({
                'prices': prices,
            })
        ctx.update({
            'boms': BOM.objects.all(),
        })
        return ctx

    def get_object(self, queryset=None):
        return self.object
