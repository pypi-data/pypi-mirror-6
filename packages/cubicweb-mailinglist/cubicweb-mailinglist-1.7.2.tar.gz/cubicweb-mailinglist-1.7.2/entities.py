"""entity classes for mailing-list entities

:organization: Logilab
:copyright: 2003-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.entities import AnyEntity, fetch_config

class MailingList(AnyEntity):
    """customized class for MailingList entities"""
    __regid__ = 'MailingList'
    fetch_attrs, cw_fetch_order = fetch_config(['name'])
