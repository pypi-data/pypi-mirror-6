# copyright 2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-cmt views/forms/actions/components for web ui"""

import datetime
from logilab.mtconverter import xml_escape

from cubicweb.view import EntityView
from cubicweb.selectors import (is_instance, match_view, match_context,
                                authenticated_user)
from cubicweb.web import uicfg, Redirect, component
from cubicweb.web.component import Layout
from cubicweb.web.views import primary

from cubes.conference.views.startup import ConferenceIndexView
from cubes.conference.views.forms import subject_reg_open_conf_vocabulary
from cubes.shoppingcart.views import ShoppingCartPrimaryView
from cubes.shoppingcart.views import ShoppingCartEntityFormRenderer

uicfg.autoform_field_kwargs.tag_subject_of(('ShoppingCart', 'book_conf', 'Conference'),
                                           {'choices': subject_reg_open_conf_vocabulary})
uicfg.actionbox_appearsin_addmenu.tag_subject_of(('Conference', 'has_shoppingitemtype', '*'), True)
uicfg.actionbox_appearsin_addmenu.tag_subject_of(('ShoppingCart', 'billing', '*'), True)
uicfg.primaryview_section.tag_subject_of(('ShoppingCart', 'billing', '*'), 'hidden')
uicfg.primaryview_section.tag_object_of(('ShoppingCart', 'billing', 'BillingAddress'), 'hidden')
uicfg.autoform_section.tag_subject_of(('ShoppingCart', 'billing', '*'), 'main', 'inlined')

_ = unicode

# this message is needed to have it appear in translation files
_('creating ShoppingCart (ShoppingCart buyer CWUser %(linkto)s)')

REPLACE_LIST = []


class CmtIndexView(ConferenceIndexView):

    def call(self):
        super(CmtIndexView, self).call()
        rset = self._cw.execute('Any X ORDERBY CD DESC LIMIT 1 WHERE X is BlogEntry, X creation_date CD')
        if rset:
            for post in rset.entities():
                self.w(post.view('primary'))

REPLACE_LIST.append((CmtIndexView, ConferenceIndexView))


class ConferenceRegistrationComponent(component.CtxComponent):
    __regid__ = 'confregistrationbox'
    context = 'left'
    title = _(u'Conference Registration')
    order = 0
    label = None

    def init_rendering(self):
        reg_open = self._cw.execute('Any C WHERE C is Conference, C reg_open True')
        if not reg_open:
            raise component.EmptyComponent()

        # BUGGY: what if there is more than one conf ?
        self.conf = self._cw.entity_from_eid(reg_open[0][0])

        register_now       = _('Register now for the conference !')
        pay_to_confirm     = _('Pay now to confirm your registration !')
        you_are_registered = _('You are registered for the conference')

        if self._cw.session.anonymous_session:
            if reg_open:
                self.label = register_now
        else:
            has_cart = self._cw.execute('Any SC WHERE U eid %(x)s, SC buyer U', {'x': self._cw.user.eid})
            items = self._cw.execute('Any I WHERE U eid %(u)s, SC buyer U, SC items_in_cart I, '
                                     'I item_type T, C has_shoppingitemtype T, C eid %(c)s',
                                     {'u': self._cw.user.eid, 'c': self.conf.eid})
            if has_cart:
                if items:
                    state = has_cart.get_entity(0, 0).cw_adapt_to('IWorkflowable').state
                    if state == 'checked out':
                        self.label = you_are_registered
                    else:
                        self.label = pay_to_confirm
                else:
                    self.label = register_now
            elif reg_open:
                 self.label = register_now
        if self.label is None:
            raise component.EmptyComponent()

    def render_body(self, w):
        label = self._cw._(self.label)
        w(u'<div class="conferenceBox">')
        w(u'<div id="confRegister">')
        w(u'<a href="%s">%s</a>' % (xml_escape(self.conf.absolute_url(vid='conf-registration')), xml_escape(label)))
        w(u'</div></div>')
        # debugging purpose
        return self.label


class ConferenceRegistrationLayout(Layout):
    __select__ = Layout.__select__ & match_context('left') & match_view('confregistrationbox')

    # raw rendering instead of default box layout (no extra div)
    def render(self, w):
        if self.init_rendering():
            view = self.cw_extra_kwargs['view']
            view.render_body(w)


class CmtShoppingCartEntityFormRenderer(ShoppingCartEntityFormRenderer):

    explanation_text = _(u'To register for the conference, add to your shopping '
                         'cart the admission fees listed below.')

REPLACE_LIST.append((CmtShoppingCartEntityFormRenderer, ShoppingCartEntityFormRenderer))

from cubes.cmcicpay import cmcic
from cubes.cmcicpay.views import get_tpe

class CmtShoppingCartPrimaryView(ShoppingCartPrimaryView):

    def reg_state(self, entity):
        if entity.items_in_cart:
            if entity.in_state[0].name == 'in progress':
                return _('not payed for')
            return _('confirmed')
        else:
            return _('empty')

    def render_entity_title(self, entity):
        reg = self.reg_state(entity)
        conf = entity.book_conf[0]
        title = self._cw._('Your registration to %s is %s') % (conf.dc_title(), self._cw._(reg))
        self.w(u'<h1>%s (#%s)</h1>' % (xml_escape(title), entity.eid))

    def render_entity_relations(self, entity):
        super(CmtShoppingCartPrimaryView, self).render_entity_relations(entity)
        reg = self.reg_state(entity)
        btn_modify = (u'<div><a href="%s">%s</a></div>' % (
                self._cw.build_url(entity.eid, vid='edition'),
                self._cw._('modify your registration')))
        if entity.billing:
            self.w(u'<p>%s</p>' % self._cw._('Billing address'))
            entity.billing[0].view('primary', w=self.w)
        else:
            add_url = self._cw.build_url('add/BillingAddress',
                                         __linkto='billing:%d:object' % entity.eid,
                                         __redirectpath='shoppingcart/%d' % entity.eid,
                                         __redirectvid='primary')
            self.w(u'<p><a href="%s">%s</a></p>' % (xml_escape(add_url), self._cw._('Add a billing address')))
        if reg == 'not payed for':
            rset = self._cw.execute('Any C WHERE C has_shoppingitemtype T, I item_type T, '
                                    'SC items_in_cart I, SC eid %(x)s', dict(x=entity.eid))
            conf = rset.get_entity(0,0)
            total = sum(item.quantity*item.item.price for item in entity.items_in_cart)
            tpe = get_tpe(self._cw)
            payreq = cmcic.PaymentRequest()
            payreq.reference = str(entity.eid)
            payreq.amount = "%.2f" % total
            payreq.currency = "EUR"
            payreq.description = conf.title
            payreq.date = datetime.datetime.now().strftime("%d/%m/%Y:%H:%M:%S")
            payreq.lang = "EN"
            #payreq.email = entity.buyer[0].primary_email
            payreq.email = "test@test.zz"
            payreq.url_root = self._cw.base_url()
            payreq.url_ok = entity.absolute_url(__message='The payment succeeded.')
            payreq.url_err = entity.absolute_url(__message='The payment failed.')
            label = self._cw._('pay now %s %s to confirm your registration') % (
                payreq.amount, payreq.currency)
            icon = u'<img alt="OK_ICON" src="%s"/>' % self._cw.uiprops['OK_ICON']
            submit = u'<button type="submit" class="validateButton">%s %s</button>' % (icon, label)
            self.w(u'<table width="100%%"><tr><td>%s</td><td>%s</td></tr></table>' % (
                    cmcic.html_form(tpe, payreq, submit),
                    btn_modify))
        elif reg == 'empty':
            self.w(u'<br /><p style="background-color: #F5E5EE;">')
            self.w(self._cw._('You have not added admission fees for the conference or the tutorials to this shopping cart.<br />'
                              'You are <b>NOT REGISTERED</b> at this point.'))
            self.w(u'</p>')
            self.w(btn_modify)
        else:
            self.w(u'<p><a href="%s">%s</a></p>' % (entity.book_conf[0].absolute_url(), self._cw._('Go to the conference schedule')))

REPLACE_LIST.append((CmtShoppingCartPrimaryView, ShoppingCartPrimaryView))

# XXX move this upstream into cw
def set_field_order(etype, attrs):
    for index, attr in enumerate(attrs):
        uicfg.autoform_field_kwargs.tag_subject_of(
            (etype, attr, '*'), {'order': index})
        uicfg.primaryview_display_ctrl.tag_subject_of(
            (etype, attr, '*'), {'order': index})

set_field_order('BillingAddress',
                ('organisation', 'street', 'street2', 'postalcode', 'city',
                 'country', 'your_ref',))

class BillingAddressPrimaryView(primary.PrimaryView):
    __select__ = primary.PrimaryView.__select__ & is_instance('BillingAddress')

    def render_entity_title(self, entity):
        pass

# registration view
class ConfRegistrationView(EntityView):
    __regid__ = 'conf-registration'
    __select__ = EntityView.__select__ & is_instance('Conference')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w(u'<h1>Registration for conference %s</h1>' % entity.dc_title())
        self.w(u'<div>%s</div>' % self._cw._(
                'You need to create an account and sign in '
                'before you can book the conference'))
        view = self._cw.vreg['views'].select('login_or_register', self._cw)
        self.w(view.render(title=False))

class ConfRegistrationAuthView(EntityView):
    __regid__ = 'conf-registration'
    __select__ = EntityView.__select__ & is_instance('Conference') & authenticated_user()

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        rset = self._cw.execute('Any S WHERE S buyer U, S book_conf C, U eid %(u)s, C eid %(c)s',
                                {'u': self._cw.user.eid, 'c': entity.eid})
        if rset:
            entity = rset.get_entity(0,0)
            url = entity.absolute_url()
        else:
            linkto = 'buyer:%s:subject' % self._cw.user.eid
            url = self._cw.build_url('add/ShoppingCart', __linkto=linkto)
        raise Redirect(url)


## urls

from cubicweb.web.views.urlrewrite import SimpleReqRewriter, rgx

class ConfRewrite(SimpleReqRewriter):
    rules = [
        (rgx('/conference/([^/]+)/registration'),
         dict(rql='Any C WHERE C is Conference, C url_id "%(id)s"' % {'id': r'\1'},
              vid='conf-registration')),
         ]

def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, [new for new,old in REPLACE_LIST])
    for new, old in REPLACE_LIST:
        vreg.register_and_replace(new, old)
