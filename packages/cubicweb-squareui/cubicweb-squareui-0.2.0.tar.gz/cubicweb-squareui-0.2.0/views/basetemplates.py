"""bootstrap implementation of base templates

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from logilab.common.decorators import monkeypatch

from logilab.mtconverter import xml_escape

from cubicweb.utils import UStringIO
from cubicweb.web.views import basetemplates


HTML5 = u'<!DOCTYPE html>'

basetemplates.TheMainTemplate.doctype = HTML5

@monkeypatch(basetemplates.TheMainTemplate)
def call(self, view):
    print self
    self.grid_nb_cols = 12
    self.set_request_content_type()
    self.template_header(self.content_type, view)
    self.template_page_content(view)
    self.template_footer(view)

@monkeypatch(basetemplates.TheMainTemplate)
def template_html_header(self, content_type, page_title,
                         additional_headers=()):
    w = self.whead
    lang = self._cw.lang
    self.write_doctype()
    # explictly close the <base> tag to avoid IE 6 bugs while browsing DOM
    self._cw.html_headers.define_var('BASE_URL', self._cw.base_url())
    self._cw.html_headers.define_var('DATA_URL', self._cw.datadir_url)
    w(u'<meta http-equiv="content-type" content="%s; charset=%s"/>\n'
      % (content_type, self._cw.encoding))
    w(u'<meta name="viewport" content="initial-scale=1.0; '
      u'maximum-scale=1.0; width=device-width; "/>')
    w(u'\n'.join(additional_headers) + u'\n')
    # FIXME this is a quick option to make cw work in IE9
    # you'll lose all IE9 functionality, the browser will act as IE8.
    w(u'<meta http-equiv="X-UA-Compatible" content="IE=8" />\n')
    w(u'<!-- Le HTML5 shim, for IE6-8 support of HTML elements -->\n'
      u'  <!--[if lt IE 9]>\n'
      u'        <script src="%s"></script>\n'
      u'  <![endif]-->\n' % self._cw.data_url('js/html5.js'))
    self.wview('htmlheader', rset=self.cw_rset)
    if page_title:
        w(u'<title>%s</title>\n' % xml_escape(page_title))


@monkeypatch(basetemplates.TheMainTemplate)
def template_body_header(self, view):
    self.w(u'<body>\n')
    self.wview('header', rset=self.cw_rset, view=view)

@monkeypatch(basetemplates.TheMainTemplate)
def template_page_content(self, view):
    w = self.w
    w(u'<div id="page" class="container">\n'
      u'<div class="row">\n')
    left_boxes = list(self._cw.vreg['ctxcomponents'].poss_visible_objects(
        self._cw, rset=self.cw_rset, view=view, context='left'))
    right_boxes = list(self._cw.vreg['ctxcomponents'].poss_visible_objects(
        self._cw, rset=self.cw_rset, view=view, context='right'))
    nb_boxes = int(bool(left_boxes)) + int(bool(right_boxes))
    content_cols = 12
    if nb_boxes:
        content_cols = self.grid_nb_cols-(3*nb_boxes)
    self.nav_column(view, left_boxes, 'left')
    self.content_column(view, content_cols)
    self.nav_column(view, right_boxes, 'right')
    self.w(u'</div>\n') # closes class=row

@monkeypatch(basetemplates.TheMainTemplate)
def nav_column(self, view, boxes, context):
    if boxes:
        getlayout = self._cw.vreg['components'].select
        self.w(u'<div id="aside-main-%s" class="col-md-3">\n' %
               context)
        self.w(u'<div class="navboxes" id="navColumn%s">\n' % context.capitalize())
        for box in boxes:
            box.render(w=self.w, view=view)
        self.w(u'</div>\n')
        self.w(u'</div>\n')
    return len(boxes)

@monkeypatch(basetemplates.TheMainTemplate)
def content_column(self, view, content_cols):
    w = self.w
    w(u'<div id="contentColumn" class="col-md-%s">' % content_cols)
    components = self._cw.vreg['components']
    self.content_components(view, components)
    self.content_header(view)
    w(u'<div class="row">')
    w(u'<div id="pageContent">')
    vtitle = self._cw.form.get('vtitle')
    if vtitle:
        w(u'<div class="vtitle">%s</div>\n' % xml_escape(vtitle))
    self.content_navrestriction_components(view, components)
    nav_html = UStringIO()
    if view and not view.handle_pagination:
        view.paginate(w=nav_html.write)
    w(nav_html.getvalue())
    w(u'<div id="contentmain">\n')
    view.render(w=w)
    w(u'</div>\n') # closes id=contentmain
    w(nav_html.getvalue())
    w(u'</div>\n' # closes id=pageContent
      u'</div>\n') # closes row
    self.content_footer(view)
    w(u'</div>\n') # closes div#contentColumn in template_body_header


@monkeypatch(basetemplates.TheMainTemplate)
def content_footer(self, view=None):
    # TODO : do not add the wrapping div if no data
    self.w(u'<div class="row">') # metadata and so
    self.wview('contentfooter', rset=self.cw_rset, view=view)
    self.w(u'</div>\n') # closes row


@monkeypatch(basetemplates.TheMainTemplate)
def content_components(self, view, components):
    """TODO : should use context"""
    rqlcomp = components.select_or_none('rqlinput', self._cw, rset=self.cw_rset)
    if rqlcomp:
        rqlcomp.render(w=self.w, view=view)
    msgcomp = components.select_or_none('applmessages', self._cw, rset=self.cw_rset)
    if msgcomp:
        msgcomp.render(w=self.w)

@monkeypatch(basetemplates.TheMainTemplate)
def content_navrestriction_components(self, view, components):
    # display entity type restriction component
    etypefilter = components.select_or_none(
        'etypenavigation', self._cw, rset=self.cw_rset)
    if etypefilter and etypefilter.cw_propval('visible'):
        etypefilter.render(w=self.w)

@monkeypatch(basetemplates.TheMainTemplate)
def template_footer(self, view=None):
    self.wview('footer', rset=self.cw_rset)
    self.w(u'</div>\n') # closes id="page"
    self.w(u'</body>\n')

@monkeypatch(basetemplates.HTMLPageHeader)
def main_header(self, view):
    """build the top menu with authentification info and the rql box"""
    spans = {'headtext': 'col-md-2',
             'header-center': 'col-md-9',
             'header-right': 'col-md-1 pull-right',
             }
    w = self.w
    w(u'<div id="header" class="navbar navbar-default" role="navigation">'
      u'<div class="container">')
    for colid, context in self.headers:
        w(u'<div id="%s" class="%s">' % (colid, spans.get(colid, 'col-md-2')))
        components = self._cw.vreg['ctxcomponents'].poss_visible_objects(
            self._cw, rset=self.cw_rset, view=view, context=context)
        for comp in components:
            comp.render(w=w)
            w(u'&#160;')
        w(u'</div>\n')
    w(u'</div>\n') # closes class="container,
    w(u'</div>\n') # closes id="header"

@monkeypatch(basetemplates.HTMLPageFooter)
def call(self, **kwargs):
    self.w(u'<footer id="pagefooter">')
    self.w(u'<div id="footer" class="container">')
    self.footer_content()
    self.w(u'</div>\n')
    self.w(u'</footer>\n')
