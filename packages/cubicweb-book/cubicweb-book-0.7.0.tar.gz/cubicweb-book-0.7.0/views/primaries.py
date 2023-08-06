"""
Primaries views for Book.

:organization: Logilab
:copyright: 2009-2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from logilab.mtconverter import xml_escape

from cubicweb.selectors import is_instance, score_entity
from cubicweb.web.views.primary import PrimaryView, RelatedView
from cubicweb.web import uicfg

uicfg.primaryview_section.tag_subject_of(('Book', 'has_cover', 'File'), 'hidden')
uicfg.primaryview_section.tag_subject_of(('Book', 'authors', '*'), 'hidden')
uicfg.primaryview_section.tag_subject_of(('Book', 'publisher', '*'), 'hidden')
uicfg.primaryview_section.tag_subject_of(('Book', 'editor', '*'), 'hidden')

uicfg.primaryview_section.tag_object_of(('Book', 'authors', 'Person'), 'relations')
uicfg.primaryview_section.tag_object_of(('Book', 'publisher', 'Editor'), 'relations')

uicfg.primaryview_section.tag_attribute(('Editor', 'name'), 'hidden')

class BookPrimaryView(PrimaryView):
    __select__ = is_instance('Book')

    def render_entity_title(self, entity):
        self.w(u'<h1>%s</h1>' % xml_escape(entity.dc_title()))

    def render_entity_attributes(self, entity):
        self._cw.add_css('cubes.book.css')
        self.w(u'<div class="container">')
        self.w(u'<div class="left">')
        self.render_cover(entity)
        self.w(u'</div>')
        self.w(u'<div>')
        self.w(u'<h3>')
        self.w(u'%s ' % self._cw._('by'))
        self.wview('csv', entity.related('authors'), 'null')
        self.w(u'</h3>')
        self.w(u'%s : %s' % (self._cw._('Summary'), xml_escape(entity.summary or u'')))
        self.w(u'</div>')
        self.w(u'</div>')
        self.render_details(entity)
        self.w(u'<div><h3>%s</h3></div>' % self._cw._('Content'))
        self.w(u'<div>%s</div>' % xml_escape(entity.content or u''))

    def render_details(self, entity):
        _ = self._cw._
        self.w(u'<div><h3>%s</h3>' % _('Details'))
        self.w(u'<ul>')
        self.w(u'<li> %s : %s </li>' % (_('Publication date'), entity.printable_value('publish_date') or u''))
        self.w(u'<li> %s : ' % _('Published by'))
        self.wview('oneline', entity.related('publisher'), 'null')
        self.w(u',  %s %s' % (entity.pages or u'?', _('pages')))
        self.w(u'</li>')
        self.w(u'<li> %s : ' % _('Editor'))
        self.wview('oneline', entity.related('editor'), 'null')
        self.w(u'</li>')
        self.w(u'<li> %s : ' % _('Collection'))
        self.wview('oneline', entity.related('collection'), 'null')
        self.w(u'</li>')
        self.w(u'<li> %s : %s' % (_('Language'), xml_escape(entity.language or u'')))
        self.w(u'</li>')
        self.w(u'<li> ISBN-10: %s' % xml_escape(entity.isbn10 or u''))
        self.w(u'</li>')
        self.w(u'<li>ISBN-13: %s' % xml_escape(entity.isbn13 or u''))
        self.w(u'</li>')
        self.w(u'</ul></div>')

    def render_cover(self, entity):
        if entity.has_cover:
            imgs = [(image.absolute_url(vid='download'), image.data_name)
                    for image in entity.has_cover]
        else:
            imgs = [(self._cw.uiprops['PICTO_NOCOVER'],
                     self._cw._('no cover'))]
        for src, alt in imgs:
            self.w(u'<img alt="%s" src="%s" style="align:right; width:110; height:130" />' %
                   (xml_escape(alt), xml_escape(src)))

class AuthorRelatedView(RelatedView):
    __select__ = is_instance('Person') & score_entity(lambda x: x.reverse_authors)

    def call(self, **kwargs):
        # nb: rset is retreived using entity.related with limit + 1 if any.
        # Because of that, we know that rset.printable_rql() will return rql
        # with no limit set anyway (since it's handled manually)
        if 'dispctrl' in self.cw_extra_kwargs:
            limit = self.cw_extra_kwargs['dispctrl'].get('limit')
            subvid = self.cw_extra_kwargs['dispctrl'].get('subvid', 'author-biblio')
        else:
            limit = None
            subvid = 'author-biblio'
        if limit is None or self.cw_rset.rowcount <= limit:
            if self.cw_rset.rowcount == 1:
                self.wview(subvid, self.cw_rset, row=0)
            elif 1 < self.cw_rset.rowcount <= 5:
                self.wview('author-biblio', self.cw_rset, subvid=subvid)
            else:
                self.w(u'<div>')
                self.wview('simplelist', self.cw_rset, subvid=subvid)
                self.w(u'</div>')
        # else show links to display related entities
        else:
            rql = self.cw_rset.printable_rql()
            self.cw_rset.limit(limit) # remove extra entity
            self.w(u'<div>')
            self.wview('simplelist', self.cw_rset, subvid=subvid)
            self.w(u'[<a href="%s">%s</a>]' % (
                xml_escape(self._cw.build_url(rql=rql, vid=subvid)),
                self._cw._('see them all')))
            self.w(u'</div>')
