# -*- coding: utf-8 -*-
"""
View generating a PDF document with the badges.
"""
import os
from tempfile import mkstemp
import itertools

from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas
from math import floor

from cubicweb import ValidationError
from cubicweb.view import EntityView
from cubicweb.web import formfields, Redirect
from cubicweb.web.form import FormViewMixIn
from cubicweb.selectors import is_instance, one_line_rset, match_user_groups
from cubicweb.web.controller import Controller
from cubicweb.web.action import Action
from cubicweb.web.formwidgets import SubmitButton

_ = unicode

# XXX to put in the form
P_WIDTH = 29.7*cm
P_HEIGHT = 21.0*cm
P_MARGIN = 1*cm
B_WIDTH = 9.0*cm
B_HEIGHT = 5.5*cm
LOGO_MAX_WIDTH = B_WIDTH
LOGO_MAX_HEIGHT = 1.5*cm
B_H_MARGIN = 0.1*cm
B_V_MARGIN = 0.5*cm

class BadgePageCanvas(object):
    "Generate and save a pdf page of badges"

    def __init__(self, filename, logo_filename, author='', title=''):
        self.h_badges_num = int(floor((P_WIDTH - 2 * P_MARGIN) / B_WIDTH))
        self.v_badges_num = int(floor((P_HEIGHT - 2 * P_MARGIN) / B_HEIGHT))
        self.badges_per_page = self.h_badges_num * self.v_badges_num
        if self.badges_per_page == 0:
            raise ValueError("Badge size too big")
        self.h_margin = (P_WIDTH - (self.h_badges_num * B_WIDTH)) / 2.0
        self.v_margin = (P_HEIGHT - (self.v_badges_num * B_HEIGHT)) / 2.0
        self.line_width = B_WIDTH - 2 * B_H_MARGIN
        # Logo specs
        self.logo = None
        self.img_width = None
        self.img_height = None
        self.__set_logo(logo_filename)
        self.create_canvas(author, title, filename)

    def __set_logo(self, logo_filename=None):
        "Load the logo and set variables"
        if logo_filename is not None:
            self.logo = ImageReader(logo_filename)
            self.img_width, self.img_height = self.logo.getSize()
            if self.img_width > LOGO_MAX_WIDTH:
                self.img_width *= LOGO_MAX_WIDTH / self.img_width
            if self.img_height > LOGO_MAX_HEIGHT:
                self.img_height = LOGO_MAX_HEIGHT
        else:
            self.logo = None

    def create_canvas(self, author, title, filename):
        "Canvas initialization"
        self.canvas = Canvas(filename)
        self.canvas.setPageSize((P_WIDTH, P_HEIGHT))
        self.canvas.title = title
        self.canvas.author = author
        self.canvas.filename = filename

    def draw_org(self, organization, lxc, lyc):
        "Print the current organization"
        font_size = 16
        while font_size > 0:
            self.canvas.setFont("Helvetica", font_size)
            if self.canvas.stringWidth(organization) <= self.line_width:
                break
            else:
                font_size -= 1
        self.canvas.drawCentredString(lxc + B_WIDTH / 2.0,
                                      lyc + B_V_MARGIN,
                                      organization)

    def draw_name(self, person, lxc, lyc):
        "Print name and surname (one line if short, two lines if long)"
        long_name = person.dc_long_title()
        font_size = 20
        top = B_HEIGHT - self.img_height
        bottom = B_V_MARGIN + font_size
        self.canvas.setFont("Helvetica-Bold", font_size)
        if person.is_chair_at:
            self.canvas.setFillColorRGB(0, .37, 0.01)
        elif person.leads:
            self.canvas.setFillColorRGB(0, 0, .53)
        else:
            self.canvas.setFillColorRGB(0, 0, 0)
        if self.canvas.stringWidth(long_name) <= self.line_width:
            height = lyc + ((top - bottom)/2.0 + bottom) - font_size / 1.5
            self.canvas.drawCentredString(lxc + B_WIDTH / 2.0,
                                          height,
                                          long_name)
        else:
            while font_size > 0:
                self.canvas.setFont("Helvetica-Bold", font_size)
                if (self.canvas.stringWidth(person.firstname) <= self.line_width and
                    self.canvas.stringWidth(person.surname) <= self.line_width):
                    break
                else:
                    font_size -= 1
            height = ((top - bottom)  / 2.0 + bottom) - font_size * 1.15
            self.canvas.drawCentredString(lxc + B_WIDTH / 2.0,
                                          lyc + height + font_size * 1.3,
                                          person.firstname)
            self.canvas.drawCentredString(lxc + B_WIDTH / 2.0,
                                          lyc + height,
                                          person.surname)
        self.canvas.setFillColorRGB(0, 0, 0)

    def fill_page(self, persons):
        "Fill the page with badges"
        self.canvas.setLineWidth(0.25)
        tuples = [[i, j, None] for i in range(self.h_badges_num) \
                  for j in range(self.v_badges_num)]
        tuples[-1][-1] = True
        index_iterator = itertools.cycle(tuples)
        self.canvas.setLineWidth(0.25)
        for person in persons:
            x_index, y_index, page = index_iterator.next()
            lxc = self.h_margin + B_WIDTH * x_index
            lyc = self.v_margin + B_HEIGHT * y_index
            self.canvas.grid([lxc, lxc + B_WIDTH],
                             [lyc, lyc + B_HEIGHT])
            if self.logo:
                self.canvas.drawImage(self.logo,
                                      lxc,
                                      lyc - self.img_height + B_HEIGHT,
                                      LOGO_MAX_WIDTH,
                                      LOGO_MAX_HEIGHT,
                                      preserveAspectRatio=True,
                                      anchor = 'sw')
            # Draw company and name
            if person.representing:
                self.draw_org(person.representing, lxc, lyc)
            self.draw_name(person, lxc, lyc)
            # If needed, generate a new page.
            if page:
                self.canvas.showPage()
                self.canvas.setLineWidth(0.25)
        self.canvas.save()
        return self.canvas


class GenerateBadgeAction(Action):
    __regid__ = 'generate_badge_action'
    title = _('generate badges')
    __select__ = is_instance('Conference') & one_line_rset() & match_user_groups('managers')

    def url(self):
        return self.cw_rset.get_entity(0, 0).absolute_url(vid='badgesform')

class BadgesForm(FormViewMixIn, EntityView):
    """ ask for optional parameters to generate a badge"""
    __regid__ = 'badgesform'
    __select__ = is_instance('Conference') & one_line_rset() & match_user_groups('managers')

    def entity_call(self, conference):
        self.w('<h2>%s</h2>' % self._cw._('Generate badges'))
        self.w('<div>%s</div>' % self._cw._('You can select a new logo, '
                                            'else the site\'s logo will be taken'))
        form = self._cw.vreg['forms'].select('base', self._cw, rset=self.cw_rset,
                                             form_renderer_id='base',
                                             entity=conference,
                                             domid='badgesform',
                                             action=self._cw.build_url('dobadges'),
                                             __errorurl=conference.absolute_url(vid='badgesform'),
                                             form_buttons=[SubmitButton()])
        form.append_field(formfields.FileField(name='logo_field',
                                               label=self._cw.__('logo file')))
        renderer = form.default_renderer()
        self.w(form.render(renderer=renderer))

class BadgesController(Controller):
    __regid__ = 'dobadges'

    def publish(self, rset=None):
        try:
            _filename, stream = self._cw.form['logo_field']
            fd, logo = mkstemp()
            logo_file = open(logo, 'w')
            logo_file.write(stream.read())
            logo_file.close()
            os.close(fd)
            is_logo_tempfile = True
        except (KeyError, ValueError):
            logo = self._cw.uiprops['LOGO']
            is_logo_tempfile = False
        conference = self._cw.execute('Any C WHERE C eid %(c)s',
                                      {'c': self._cw.form['eid']}).get_entity(0, 0)
        raise Redirect(conference.absolute_url(vid='badgeview', logo=logo,
                                               is_logo_tempfile=is_logo_tempfile))

class EmptyPerson(object):
    """ fake class to fake people with empty names to do handmade badges """
    representing = u' '
    is_chair_at = False
    leads = False
    firstname = u''
    surname = u''

    def dc_long_title(self):
        return u' '

class BadgeView(EntityView):
    __regid__ = 'badgeview'
    title = _('generate badges')
    __select__ = is_instance('Conference') & one_line_rset() & match_user_groups('managers')
    content_type = "application/pdf"
    templatable = False
    binary = True
    filename = 'badges.pdf'

    def set_request_content_type(self):
        """overriden to set a .pdf filename"""
        self._cw.set_content_type(self.content_type,
                                  filename=self.filename)

    def call(self):
        conference = self.cw_rset.get_entity(0, 0)
        logo = self._cw.form.get('logo')
        if not logo:
            return
        is_logo_tempfile = self._cw.form.get('is_logo_tempfile') == 'True'
        page = BadgePageCanvas(self.filename, logo,
                               self._cw.user.dc_long_title(), 'Badges',
                               )
        page.fill_page(self.get_users(conference))
        page.fill_page([EmptyPerson(),]*9) #empty badges for last minute attendees
        if is_logo_tempfile:
            os.remove(logo)
        self.w(open(self.filename).read())

    def get_users(self, conference):
        """
        return users which are register to the conference
        """
        rql = ('Any U ORDERBY N WHERE U is CWUser, U surname N?, EXISTS(S is ShoppingCart, '
               'S buyer U, S in_state ST, ST name IN ("awaiting payment", "checked out"), '
               'S items_in_cart I, I item_type IT, C has_shoppingitemtype IT, C eid %(x)s)')
        return self._cw.execute(rql, dict(x=conference.eid)).entities()
