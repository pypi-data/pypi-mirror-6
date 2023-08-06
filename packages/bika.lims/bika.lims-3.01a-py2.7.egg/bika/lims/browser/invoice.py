from bika.lims.browser import BrowserView
from bika.lims.interfaces import IInvoiceView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements


class InvoiceView(BrowserView):

    implements(IInvoiceView)

    template = ViewPageTemplateFile("templates/invoice.pt")
    content = ViewPageTemplateFile("templates/invoice_content.pt")

    def __init__(self, context, request):
        super(InvoiceView, self).__init__(context, request)
        request.set('disable_border', 1)

    def __call__(self):
        context = self.context
        workflow = getToolByName(context, 'portal_workflow')
        # Gather relted objects
        batch = context.aq_parent
        client = context.getClient()
        # Gather general data
        self.invoiceId = context.getId()
        self.invoiceDate = self.ulocalized_time(context.getInvoiceDate())
        self.subtotal = context.getSubtotal()
        self.vatTotal = context.getVATTotal()
        self.total = context.getTotal()
        # Create the batch range
        start = self.ulocalized_time(batch.getBatchStartDate())
        end = self.ulocalized_time(batch.getBatchEndDate())
        self.batchRange = "%s to %s" % (start, end)
        # Gather client data
        self.clientName = client.Title()
        self.clientPhone = client.getPhone()
        self.clientFax = client.getFax()
        self.clientEmail = client.getEmailAddress()
        self.clientAccountNumber = client.getAccountNumber()
        # Get an available client address in a preferred order
        self.clientAddress = None
        addresses = (
            client.getBillingAddress(),
            client.getPostalAddress(),
            client.getPhysicalAddress(),
        )
        for address in addresses:
            if address.get('address'):
                self.clientAddress = address
                break
        # Gather the line items
        items = context.invoice_lineitemms
        self.items = [{
            'invoiceDate': self.ulocalized_time(item['ItemDate']),
            'description': item['ItemDescription'],
            'orderNo': item['ClientOrderNumber'],
            'subtotal': item['Subtotal'],
            'vatTotal': item['ATTotal'],
            'total': item['Total'],
        } for item in items]
        # Render the template
        return self.template()


class InvoicePrintView(InvoiceView):

    template = ViewPageTemplateFile("templates/invoice_print.pt")

    def __call__(self):
        return InvoiceView.__call__(self)
