# -*- coding: utf-8 -*-
"""bootstrap implementation of tableview

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from cubicweb.web.views import tableview

tableview.TableLayout.cssclass = 'table table-striped table-bordered table-condensed'
