from DateTime import DateTime
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.browser import BrowserView
from bika.lims.config import POINTS_OF_CAPTURE
from bika.lims.utils import sendmail, encode_header, createPdf
from cStringIO import StringIO
from email.Utils import formataddr
from email.mime.image import MIMEImage
from email.MIMEBase import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import Encoders
from os.path import join
from smtplib import SMTPRecipientsRefused
from smtplib import SMTPServerDisconnected
import App
import Globals
import re

class doPublish(BrowserView):
    """Pre/Re/Publish analysis requests"""
    ar_results = ViewPageTemplateFile("mailtemplates/analysisrequest_results.pt")

    def __init__(self, context, request, action, analysis_requests):
        self.context = context
        self.request = request
        # the workflow transition that invoked us
        self.action = action

        # the list of ARs that we will process.
        # Filter them here so we only publish those with verified analyses.
        workflow = getToolByName(self.context, 'portal_workflow')
        ARs_to_publish = []
        for ar in analysis_requests:
            if workflow.getInfoFor(ar, 'review_state') in ['verified', 'published']:
                ARs_to_publish.append(ar)
            else:
                if ar.getAnalyses(review_state='verified'):
                    ARs_to_publish.append(ar)
                else:
                    if ar.getAnalyses(review_state='published'):
                        ARs_to_publish.append(ar)
        self.analysis_requests = ARs_to_publish

    def formattedResult(self, result, precision=2):
        if not result:
            return ''
        try:
            return str('%%.%sf' % precision)%float(result)
        except:
            return result

    def __call__(self):

        rc = getToolByName(self.context, REFERENCE_CATALOG)
        workflow = getToolByName(self.context, 'portal_workflow')

        BatchEmail = self.context.bika_setup.getBatchEmail()

        username = self.context.portal_membership.getAuthenticatedMember().getUserName()
        self.reporter = self.user_fullname(username)
        self.reporter_email = self.user_email(username)

        # signature image
        self.reporter_signature = ""
        c = [x for x in self.bika_setup_catalog(portal_type='LabContact')
             if x.getObject().getUsername() == username]
        if c:
            sf = c[0].getObject().getSignature()
            if sf:
                self.reporter_signature = sf.absolute_url() + "/Signature"

        # lab address
        self.laboratory = laboratory = self.context.bika_setup.laboratory
        self.lab_address = "<br/>".join(laboratory.getPrintAddress())

        # group/publish analysis requests by contact
        ARs_by_contact = {}
        for ar in self.analysis_requests:
            contact_uid = ar.getContact().UID()
            if contact_uid not in ARs_by_contact:
                ARs_by_contact[contact_uid] = []
            ARs_by_contact[contact_uid].append(ar)

        for contact_uid, ars in ARs_by_contact.items():
            ars.sort()
            self.contact = ars[0].getContact()
            self.pub_pref = self.contact.getPublicationPreference()
            batch_size = 'email' in self.pub_pref and BatchEmail or 5

            # client address
            self.client = ars[0].aq_parent
            self.client_address = "<br/>".join(self.client.getPrintAddress())

            self.Footer = self.context.bika_setup.getResultFooter()

            # send batches of ARs to each contact
            for b in range(0, len(ars), batch_size):
                self.batch = ars[b:b+batch_size]
                self.any_accredited = False
                self.any_drymatter = False
                # get all services from all requests in this batch into a
                # dictionary:
                #   {'Point Of Capture': {'Category': [service,service,...]}}
                self.services = {}

                out_fn = "_".join([ar.Title() for ar in self.batch])

                for ar in self.batch:
                    if ar.getReportDryMatter():
                        self.any_drymatter = True
                    states = ("verified", "published")
                    for analysis in ar.getAnalyses(full_objects=True,
                                                   review_state=states):
                        service = analysis.getService()
                        poc = POINTS_OF_CAPTURE.getValue(service.getPointOfCapture())
                        cat = service.getCategoryTitle()
                        if poc not in self.services:
                            self.services[poc] = {}
                        if cat not in self.services[poc]:
                            self.services[poc][cat] = []
                        if service not in self.services[poc][cat]:
                            self.services[poc][cat].append(service)
                        if (service.getAccredited()):
                            self.any_accredited = True

                # compose and send email
                if 'email' in self.pub_pref:

                    # render template
                    ar_results = self.ar_results()
                    ar_results = safe_unicode(ar_results).encode('utf-8')

                    debug_mode = App.config.getConfiguration().debug_mode
                    if debug_mode:
                        open(join(Globals.INSTANCE_HOME,'var', out_fn + ".html"),
                             "w").write(ar_results)

                    ramdisk = StringIO()
                    pdf = createPdf(ar_results, ramdisk)
                    pdf_data = ramdisk.getvalue()
                    ramdisk.close()

                    if debug_mode:
                        open(join(Globals.INSTANCE_HOME,'var', out_fn + ".pdf"),
                             "wb").write(pdf_data)

                    mime_msg = MIMEMultipart('related')
                    mime_msg['Subject'] = self.get_mail_subject()
                    mime_msg['From'] = formataddr(
                        (encode_header(laboratory.getName()),
                         laboratory.getEmailAddress()))
                    mime_msg['To'] = formataddr(
                        (encode_header(self.contact.getFullname()),
                         self.contact.getEmailAddress()))
                    mime_msg.preamble = 'This is a multi-part MIME message.'
                    msg_txt = MIMEText(ar_results, _subtype='html')
                    mime_msg.attach(msg_txt)
                    if not pdf.err:
                        part = MIMEBase('application', "application/pdf")
                        part.add_header('Content-Disposition', 'attachment; filename="%s.pdf"' % out_fn)
                        part.set_payload( pdf_data )
                        Encoders.encode_base64(part)
                        mime_msg.attach(part)

                    try:
                        host = getToolByName(self.context, 'MailHost')
                        host.send(mime_msg.as_string(), immediate=True)
                    except SMTPServerDisconnected, msg:
                        if not debug_mode:
                            raise SMTPServerDisconnected(msg)
                    except SMTPRecipientsRefused, msg:
                        raise WorkflowException(str(msg))

                    if self.action == 'publish':
                        for ar in self.batch:
                            try:
                                workflow.doActionFor(ar, 'publish')
                            except WorkflowException:
                                pass

##                    if not pdf.err:
##                        setheader = self.request.RESPONSE.setHeader
##                        setheader('Content-Type', 'application/pdf')
##                        setheader("Content-Disposition", "attachment;filename=\"%s.pdf\"" % out_fn)
##                        self.request.RESPONSE.write(pdf_data)

                else:
                    raise Exception, "XXX pub_pref %s" % self.pub_pref

        return [ar.RequestID for ar in self.analysis_requests]

    def getResult(self, analysis):
        result = analysis.getResult()
        service = analysis.getService()
        choices = service.getResultOptions()
        for choice in choices:
            if choice['ResultValue'] == result:
                return choice['ResultText']

        precision = service.getPrecision()
        try:
            result = str('%%.%sf' % precision) % float(result)
        except:
            pass

        return result

    def get_managers_from_requests(self):
        ## Script (Python) "get_managers_from_requests"
        ##bind container=container
        ##bind context=context
        ##bind namespace=
        ##bind script=script
        ##bind subpath=traverse_subpath
        ##parameters=batch
        ##title=Get services from requests
        ##
        managers = {'ids': [],
                    'dict': {}}
        departments = {}
        for ar in self.batch:
            ar_mngrs = ar.getResponsible()
            for id in ar_mngrs['ids']:
                new_depts = ar_mngrs['dict'][id]['dept'].split(',')
                if id in managers['ids']:
                    for dept in new_depts:
                        if dept not in departments[id]:
                            departments[id].append(dept)
                else:
                    departments[id] = new_depts
                    managers['ids'].append(id)
                    managers['dict'][id] = ar_mngrs['dict'][id]

        mngrs = departments.keys()
        for mngr in mngrs:
            final_depts = ''
            for dept in departments[mngr]:
                if final_depts:
                    final_depts += ', '
                final_depts += dept
            managers['dict'][mngr]['dept'] = final_depts

        return managers


    def get_mail_subject(self):
        client = self.batch[0].aq_parent
        subject_items = client.getEmailSubject()
        ai = co = cr = cs = False
        if 'ar' in subject_items:
            ai = True
        if 'co' in subject_items:
            co = True
        if 'cr' in subject_items:
            cr = True
        if 'cs' in subject_items:
            cs = True
        ais = []
        cos = []
        crs = []
        css = []
        blanks_found = False
        for ar in self.batch:
            if ai:
                ais.append(ar.getRequestID())
            if co:
                if ar.getClientOrderNumber():
                    if not ar.getClientOrderNumber() in cos:
                        cos.append(ar.getClientOrderNumber())
                else:
                    blanks_found = True
            if cr or cs:
                sample = ar.getSample()
            if cr:
                if sample.getClientReference():
                    if not sample.getClientReference() in crs:
                        crs.append(sample.getClientReference())
                else:
                    blanks_found = True
            if cs:
                if sample.getClientSampleID():
                    if not sample.getClientSampleID() in css:
                        css.append(sample.getClientSampleID())
                else:
                    blanks_found = True
        tot_line = ''
        if ais:
            ais.sort()
            ar_line = 'ARs: %s' % ', '.join(ais)
            tot_line = ar_line
        if cos:
            cos.sort()
            cos_line = 'Orders: %s' % ', '.join(cos)
            if tot_line:
                tot_line += ' '
            tot_line += cos_line
        if crs:
            crs.sort()
            crs_line = 'Refs: %s' % ', '.join(crs)
            if tot_line:
                tot_line += ' '
            tot_line += crs_line
        if css:
            css.sort()
            css_line = 'Samples: %s' % ', '.join(css)
            if tot_line:
                tot_line += ' '
            tot_line += css_line
        if tot_line:
            subject = 'Analysis results for %s' % tot_line
            if blanks_found:
                subject += ' and others'
        else:
            subject = 'Analysis results'
        return subject

