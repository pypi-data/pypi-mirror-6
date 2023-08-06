"""Notification views for keywords / classification schemes

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from logilab.common.decorators import cached

from cubicweb.predicates import is_instance
from cubicweb.sobjects.notification import NotificationView


class KeywordNotificationView(NotificationView):
    __select__ = is_instance('Keyword')
    msgid_timestamp = True

    def recipients(self):
        """Returns the project's interested people (entities)"""
        creator = self.cw_rset.get_entity(0, 0).created_by[0]
        if not creator.is_in_group('managers') and creator.primary_email:
            return [(creator.primary_email[0].address, 'fr')]
        return []

    def context(self, **kwargs):
        context = NotificationView.context(self, **kwargs)
        entity = self.cw_rset.get_entity(0, 0)
        context['kw'] = entity.name
        return context


class KeywordNameChanged(KeywordNotificationView):
    __regid__ = 'notif_after_update_entity'

    content = _("keyword name changed from %(oldname)s to %(kw)s")

    @cached
    def get_oldname(self, entity):
        session = self.req
        try:
            return session.execute('Any N WHERE X eid %(x)s, X name N',
                                   {'x' : entity.eid}, 'x')[0][0]
        except IndexError:
            return u'?'

    def context(self, **kwargs):
        entity = self.cw_rset.get_entity(0, 0)
        context = KeywordNotificationView.context(self, **kwargs)
        context['oldname'] = self.get_oldname(entity)
        return context

    def subject(self):
        entity = self.cw_rset.get_entity(0, 0)
        return self.req._('keyword name changed from %s to %s') % (
            self.get_oldname(entity), entity.name)
