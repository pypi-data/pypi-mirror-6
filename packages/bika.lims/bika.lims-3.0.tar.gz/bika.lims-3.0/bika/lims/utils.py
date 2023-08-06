from AccessControl import ModuleSecurityInfo, allow_module
from bika.lims import logger
from bika.lims.browser import BrowserView
from bika.lims.config import POINTS_OF_CAPTURE
from DateTime import DateTime
from email import Encoders
from email.MIMEBase import MIMEBase
from magnitude import mg
from Products.Archetypes.public import DisplayList
from Products.CMFCore.utils import getToolByName
import re
import Globals
import json
import urllib2

ModuleSecurityInfo('email.Utils').declarePublic('formataddr')
allow_module('csv')


def to_utf8(text):
    if text == None:
        text = ''
    if isinstance(text, unicode):
        return text.encode('utf-8')
    else:
        return unicode(text).encode('utf-8')


def to_unicode(text):
    if text == None:
        text = ''
    if isinstance(text, str):
        return text.decode('utf-8')
    else:
        return text

# Wrapper for PortalTransport's sendmail - don't know why there sendmail
# method is marked private
ModuleSecurityInfo('Products.bika.utils').declarePublic('sendmail')
# Protected( Publish, 'sendmail')


def sendmail(portal, from_addr, to_addrs, msg):
    mailspool = portal.portal_mailspool
    mailspool.sendmail(from_addr, to_addrs, msg)


class js_log(BrowserView):

    def __call__(self, message):
        """Javascript sends a string for us to place into the log.
        """
        self.logger.info(message)

ModuleSecurityInfo('Products.bika.utils').declarePublic('printfile')


def printfile(portal, from_addr, to_addrs, msg):
    import os

    """ set the path, then the cmd 'lpr filepath'
    temp_path = 'C:/Zope2/Products/Bika/version.txt'

    os.system('lpr "%s"' %temp_path)
    """
    pass


def getUsers(context, roles, allow_empty=True):
    """ Present a DisplayList containing users in the specified
        list of roles
    """
    mtool = getToolByName(context, 'portal_membership')
    pairs = allow_empty and [['', '']] or []
    users = mtool.searchForMembers(roles=roles)
    for user in users:
        uid = user.getId()
        fullname = user.getProperty('fullname')
        if fullname is None:
            fullname = uid
        pairs.append((uid, fullname))
    pairs.sort(lambda x, y: cmp(x[1], y[1]))
    return DisplayList(pairs)


def isActive(obj):
    """ Check if obj is inactive or cancelled.
    """
    wf = getToolByName(obj, 'portal_workflow')
    if (hasattr(obj, 'inactive_state') and obj.inactive_state == 'inactive') or \
       wf.getInfoFor(obj, 'inactive_state', 'active') == 'inactive':
        return False
    if (hasattr(obj, 'cancellation_state') and obj.inactive_state == 'cancelled') or \
       wf.getInfoFor(obj, 'cancellation_state', 'active') == 'cancelled':
        return False
    return True


def formatDateQuery(context, date_id):
    """ Obtain and reformat the from and to dates
        into a date query construct
    """
    from_date = context.REQUEST.get('%s_fromdate' % date_id, None)
    if from_date:
        from_date = from_date + ' 00:00'
    to_date = context.REQUEST.get('%s_todate' % date_id, None)
    if to_date:
        to_date = to_date + ' 23:59'

    date_query = {}
    if from_date and to_date:
        date_query = {'query': [from_date, to_date],
                      'range': 'min:max'}
    elif from_date or to_date:
        date_query = {'query': from_date or to_date,
                      'range': from_date and 'min' or 'max'}

    return date_query


def formatDateParms(context, date_id):
    """ Obtain and reformat the from and to dates
        into a printable date parameter construct
    """
    from_date = context.REQUEST.get('%s_fromdate' % date_id, None)
    to_date = context.REQUEST.get('%s_todate' % date_id, None)

    date_parms = {}
    if from_date and to_date:
        date_parms = 'from %s to %s' % (from_date, to_date)
    elif from_date:
        date_parms = 'from %s' % (from_date)
    elif to_date:
        date_parms = 'to %s' % (to_date)

    return date_parms


def formatDuration(context, totminutes):
    """ Format a time period in a usable manner: eg. 3h24m
    """
    mins = totminutes % 60
    hours = (totminutes - mins) / 60

    if mins:
        mins_str = '%sm' % mins
    else:
        mins_str = ''

    if hours:
        hours_str = '%sh' % hours
    else:
        hours_str = ''

    return '%s%s' % (hours_str, mins_str)

# encode_header function copied from roundup's rfc2822 package.
hqre = re.compile(r'^[A-z0-9!"#$%%&\'()*+,-./:;<=>?@\[\]^_`{|}~ ]+$')

ModuleSecurityInfo('Products.bika.utils').declarePublic('encode_header')


def encode_header(header, charset='utf-8'):
    """ Will encode in quoted-printable encoding only if header
    contains non latin characters
    """

    # Return empty headers unchanged
    if not header:
        return header

    # return plain header if it does not contain non-ascii characters
    if hqre.match(header):
        return header

    quoted = ''
    # max_encoded = 76 - len(charset) - 7
    for c in header:
        # Space may be represented as _ instead of =20 for readability
        if c == ' ':
            quoted += '_'
        # These characters can be included verbatim
        elif hqre.match(c):
            quoted += c
        # Otherwise, replace with hex value like =E2
        else:
            quoted += "=%02X" % ord(c)
            plain = 0

    return '=?%s?q?%s?=' % (charset, quoted)


def zero_fill(matchobj):
    return matchobj.group().zfill(8)

num_sort_regex = re.compile('\d+')

ModuleSecurityInfo('Products.bika.utils').declarePublic('sortable_title')


def sortable_title(portal, title):
    """Convert title to sortable title
    """
    if not title:
        return ''

    def_charset = portal.plone_utils.getSiteEncoding()
    sortabletitle = title.lower().strip()
    # Replace numbers with zero filled numbers
    sortabletitle = num_sort_regex.sub(zero_fill, sortabletitle)
    # Truncate to prevent bloat
    for charset in [def_charset, 'latin-1', 'utf-8']:
        try:
            sortabletitle = unicode(sortabletitle, charset)[:30]
            sortabletitle = sortabletitle.encode(def_charset or 'utf-8')
            break
        except UnicodeError:
            pass
        except TypeError:
            # If we get a TypeError if we already have a unicode string
            sortabletitle = sortabletitle[:30]
            break
    return sortabletitle


def logged_in_client(context, member=None):
    if not member:
        membership_tool = getToolByName(context, 'portal_membership')
        member = membership_tool.getAuthenticatedMember()

    client = None
    groups_tool = context.portal_groups
    member_groups = [groups_tool.getGroupById(group.id).getGroupName()
                 for group in groups_tool.getGroupsByUserId(member.id)]

    if 'Clients' in member_groups:
        for obj in context.clients.objectValues("Client"):
            if member.id in obj.users_with_local_role('Owner'):
                client = obj
    return client


def changeWorkflowState(content, wf_id, state_id, acquire_permissions=False,
                        portal_workflow=None, **kw):
    """Change the workflow state of an object
    @param content: Content obj which state will be changed
    @param state_id: name of the state to put on content
    @param acquire_permissions: True->All permissions unchecked and on riles and
                                acquired
                                False->Applies new state security map
    @param portal_workflow: Provide workflow tool (optimisation) if known
    @param kw: change the values of same name of the state mapping
    @return: None
    """

    if portal_workflow is None:
        portal_workflow = getToolByName(content, 'portal_workflow')

    # Might raise IndexError if no workflow is associated to this type
    found_wf = 0
    for wf_def in portal_workflow.getWorkflowsFor(content):
        if wf_id == wf_def.getId():
            found_wf = 1
            break
    if not found_wf:
        logger.error("%s: Cannot find workflow id %s" % (content, wf_id))

    wf_state = {
        'action': None,
        'actor': None,
        'comments': "Setting state to %s" % state_id,
        'review_state': state_id,
        'time': DateTime(),
        }

    # Updating wf_state from keyword args
    for k in kw.keys():
        # Remove unknown items
        if k not in wf_state:
            del kw[k]
    if 'review_state' in kw:
        del kw['review_state']
    wf_state.update(kw)

    portal_workflow.setStatusOf(wf_id, content, wf_state)

    if acquire_permissions:
        # Acquire all permissions
        for permission in content.possible_permissions():
            content.manage_permission(permission, acquire=1)
    else:
        # Setting new state permissions
        wf_def.updateRoleMappingsFor(content)

    # Map changes to the catalogs
    content.reindexObject(idxs=['allowedRolesAndUsers', 'review_state'])
    return


class bika_bsc_counter(BrowserView):

    def __call__(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        return bsc.getCounter()


class bika_browserdata(BrowserView):

    """Returns information about services from bika_setup_catalog.
    This view is called from ./js/utils.js and it's output is cached
    in browser localStorage.
    """

    def __call__(self):
        translate = self.context.translate
        bsc = getToolByName(self.context, 'bika_setup_catalog')

        data = {
            'categories': {},  # services keyed by "POC_category"
            'services': {},    # service info, keyed by UID
        }

        # Loop ALL SERVICES
        services = dict([(b.UID, b.getObject()) for b
                         in bsc(portal_type="AnalysisService",
                                inactive_state="active")])

        for uid, service in services.items():
            # Store categories
            # data['categories'][poc_catUID]: [uid, uid]
            key = "%s_%s" % (service.getPointOfCapture(),
                             service.getCategoryUID())
            if key in data['categories']:
                data['categories'][key].append(uid)
            else:
                data['categories'][key] = [uid, ]

            # Get dependants
            # (this service's Calculation backrefs' dependencies)
            backrefs = []
            # this function follows all backreferences so we need skip to
            # avoid recursion. It should maybe be modified to be more smart...
            skip = []

            def walk(items):
                for item in items:
                    if item.portal_type == 'AnalysisService'\
                       and item.UID() != service.UID():
                        backrefs.append(item)
                    if item not in skip:
                        skip.append(item)
                        brefs = item.getBackReferences()
                        walk(brefs)
            walk([service, ])

            # Get dependencies
            # (services we depend on)
            deps = {}
            calc = service.getCalculation()
            if calc:
                td = calc.getCalculationDependencies()

                def walk(td):
                    for depserv_uid, depserv_deps in td.items():
                        if depserv_uid == uid:
                            continue
                        depserv = services[depserv_uid]
                        category = depserv.getCategory()
                        cat = '%s_%s' % (category.UID(), category.Title())
                        poc = '%s_%s' % \
                            (depserv.getPointOfCapture(),
                             POINTS_OF_CAPTURE.getValue(depserv.getPointOfCapture()))
                        srv = '%s_%s' % (depserv.UID(), depserv.Title())
                        if poc not in deps:
                            deps[poc] = {}
                        if cat not in deps[poc]:
                            deps[poc][cat] = []
                        if not srv in deps[poc][cat]:
                            deps[poc][cat].append(srv)
                        if depserv_deps:
                            walk(depserv_deps)
                walk(td)

            # Get partition setup records for this service
            separate = service.getSeparate()
            containers = service.getContainer()
            containers.sort(lambda a, b: cmp(
                int(a.getJSCapacity() and a.getJSCapacity().split(" ")[0] or '0'),
                int(b.getJSCapacity() and b.getJSCapacity().split(" ")[0] or '0')
            ))
            preservations = service.getPreservation()
            partsetup = service.getPartitionSetup()

            # Single values become lists here
            for x in range(len(partsetup)):
                if 'container' in partsetup[x] \
                   and isinstance(partsetup[x]['container'], str):
                    partsetup[x]['container'] = [partsetup[x]['container'], ]
                if 'preservation' in partsetup[x] \
                   and isinstance(partsetup[x]['preservation'], str):
                    partsetup[x]['preservation'] = [partsetup[x]['preservation'], ]
                minvol = partsetup[x].get('vol', '0 g')
                try:
                    mgminvol = minvol.split(' ', 1)
                    mgminvol = mg(float(mgminvol[0]), mgminvol[1])
                except:
                    mgminvol = mg(0, 'ml')
                try:
                    mgminvol = str(mgminvol.ounit('ml'))
                except:
                    pass
                try:
                    mgminvol = str(mgminvol.ounit('g'))
                except:
                    pass
                partsetup[x]['vol'] = str(mgminvol)

            # If no dependents, backrefs or partition setup exists
            # nothing is stored for this service
            if not (backrefs or deps or separate or
                    containers or preservations or partsetup):
                continue

            # store info for this service
            data['services'][uid] = {
                'backrefs': [s.UID() for s in backrefs],
                'deps': deps,
            }

            data['services'][uid]['Separate'] = separate
            data['services'][uid]['Container'] = \
                [container.UID() for container in containers]
            data['services'][uid]['Preservation'] = \
                [pres.UID() for pres in preservations]
            data['services'][uid]['PartitionSetup'] = \
                partsetup

        uc = getToolByName(self.context, 'uid_catalog')

        # SamplePoint and SampleType autocomplete lookups need a reference
        # to resolve Title->UID
        data['st_uids'] = {}
        for st_proxy in bsc(portal_type='SampleType',
                        inactive_state='active'):
            st = st_proxy.getObject()
            data['st_uids'][st.Title()] = {
                'uid': st.UID(),
                'minvol': st.getJSMinimumVolume(),
                'containertype': st.getContainerType() and st.getContainerType().UID() or '',
                'samplepoints': [sp.Title() for sp in st.getSamplePoints()]
            }

        data['sp_uids'] = {}
        for sp_proxy in bsc(portal_type='SamplePoint',
                        inactive_state='active'):
            sp = sp_proxy.getObject()
            data['sp_uids'][sp.Title()] = {
                'uid': sp.UID(),
                'composite': sp.getComposite(),
                'sampletypes': [st.Title() for st in sp.getSampleTypes()]
            }

        data['containers'] = {}
        for c_proxy in bsc(portal_type='Container'):
            c = c_proxy.getObject()
            pres = c.getPreservation()
            data['containers'][c.UID()] = {
                'title': c.Title(),
                'uid': c.UID(),
                'containertype': c.getContainerType() and c.getContainerType().UID() or '',
                'prepreserved': c.getPrePreserved(),
                'preservation': pres and pres.UID() or '',
                'capacity': c.getJSCapacity(),
            }

        data['preservations'] = {}
        for p_proxy in bsc(portal_type='Preservation'):
            p = p_proxy.getObject()
            data['preservations'][p.UID()] = {
                'title': p.Title(),
                'uid': p.UID(),
            }

        data['prefixes'] = dict([(p['portal_type'], p['prefix']) for p in self.context.bika_setup.getPrefixes()])

        return json.dumps(data)


def tmpID():
    import os, binascii
    return binascii.hexlify(os.urandom(16))


def createPdf(htmlreport, outfile=None, css=None):
    # XXX css must be a local file - urllib fails under robotframework tests.
    css_def = ''
    if css:
        if css.startswith("http://") or css.startswith("https://"):
            # Download css file in temp dir
            u = urllib2.urlopen(css)
            _cssfile = Globals.INSTANCE_HOME + '/var/' + tmpID() + '.css'
            localFile = open(_cssfile, 'w')
            localFile.write(u.read())
            localFile.close()
        else:
            _cssfile = css
        cssfile = open(_cssfile, 'r')
        css_def = cssfile.read()
    from weasyprint import HTML, CSS
    htmlfilepath = Globals.INSTANCE_HOME + "/var/" + tmpID() + ".html"
    htmlfile = open(htmlfilepath, 'w')
    htmlfile.write(htmlreport)
    htmlfile.close()
    if not outfile:
        outfile = Globals.INSTANCE_HOME + "/var/" + tmpID() + ".pdf"
    if css:
        HTML(htmlfilepath).write_pdf(outfile,
            stylesheets=[CSS(string=css_def)])
    else:
        HTML(htmlfilepath).write_pdf(outfile)
    return open(outfile, 'r').read()


def attachPdf(mimemultipart, pdfreport, filename=None):
    part = MIMEBase('application', "application/pdf")
    part.add_header('Content-Disposition',
                    'attachment; filename="%s.pdf"' % (filename or tmpID()))
    part.set_payload(pdfreport)
    Encoders.encode_base64(part)
    mimemultipart.attach(part)
