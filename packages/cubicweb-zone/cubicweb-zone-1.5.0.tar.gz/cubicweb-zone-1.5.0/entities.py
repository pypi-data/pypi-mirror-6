"""entity classes for zone entities

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.entities import AnyEntity, fetch_config
from cubicweb.entities.adapters import ITreeAdapter
from cubicweb.predicates import is_instance


class Zone(AnyEntity):
    """customized class for Zone entities"""
    __regid__ = 'Zone'
    fetch_attrs, fetch_order = fetch_config(['name'])


class ZoneITreeAdapter(ITreeAdapter):
    __select__ = is_instance('Zone')
    tree_relation = 'situated_in'

