# -*- coding: utf-8 -*-
"""this is where you could register procedures for instance

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"
from logilab.common.configuration import REQUIRED

options = (
    ('cw_compatibility',
      {'type' : 'yn',
      'default': True,
      'help': 'specifies if cw_combatibility css must be activated (needed in production)',
      'group': 'bootstrap', 'level': 0,
      }),
)
