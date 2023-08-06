"""Specific views for mailinglists entities

:organization: Logilab
:copyright: 2003-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

from cubicweb.predicates import is_instance, score_entity
from cubicweb.view import EntityView, EntityAdapter
from cubicweb import tags
from cubicweb.web import uicfg, action
from cubicweb.web.views import primary, baseviews


for attr in ('name', 'homepage', 'archive', 'mlid', 'email_address'):
    uicfg.primaryview_section.tag_attribute(('MailingList', attr), 'hidden')
uicfg.primaryview_section.tag_subject_of(('MailingList', 'mailinglist_of', '*'),
                                         'sideboxes')

class MLPrimaryView(primary.PrimaryView):
    __select__ = is_instance('MailingList')
    show_attr_label = False

    def render_entity_attributes(self, entity):
        super(MLPrimaryView, self).render_entity_attributes(entity)
        _ = self._cw._
        self.w(u'<ul>')
        if entity.homepage:
            self.w(u'<li>%s</li>' % tags.a(_('(un)subscribe'),
                                           href=entity.homepage))
        if entity.archive:
            self.w(u'<li>%s</li>' % tags.a(_('browse archives'),
                                           href=entity.archive))
        self.w(u'<li>%s %s</li>'
               % (_('to post on the mailinglist:'),
                  tags.a(entity.email_address,
                         href=u'mailto:' + entity.email_address)))
        self.w(u'</ul>')


class MLDoapItemView(EntityView):
    __regid__ = 'doapitem'
    __select__ = is_instance('MailingList')

    def cell_call(self, row, col):
        """ element as an item for an doap description """
        entity = self.cw_rset.get_entity(row, col)
        self.w(u'<doap:mailing-list rdf:resource="%s" />\n' % entity.absolute_url())


class MLArchiveAction(action.Action):
    __regid__ = 'mlarchive'
    __select__ = is_instance('MailingList') & score_entity(lambda x: x.archive)

    category = 'mainactions'
    title = _('browse archives')
    order = 20

    def url(self):
        return self.cw_rset.get_entity(0, 0).archive


class MLRegisterAction(action.Action):
    __regid__ = 'mlregister'
    __select__ = is_instance('MailingList') & score_entity(lambda x: x.homepage)

    category = 'mainactions'
    title = _('(un)subscribe')
    order = 21

    def url(self):
        return self.cw_rset.get_entity(0, 0).homepage


class MLISIOCContainerAdapter(EntityAdapter):
    """interface for entities which may be represented as an ISIOC container"""
    __regid__ = 'ISIOCContainer'
    __select__ = is_instance('MailingList')

    # isioc interface
    def isioc_type(self):
        return 'MailingList'

    def isioc_items(self):
        return self.reverse_sent_on

def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (MLISIOCContainerAdapter,))
    if 'sent_on' in vreg.schema['MailingList'].object_relations():
        vreg.register(MLISIOCContainerAdapter)
