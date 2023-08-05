# -*- coding: utf-8 -*-
# copyright 2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

"""cubicweb-postgis views/forms/actions/components for web ui"""

from cubicweb import uilib
from cubicweb.web import formfields

# StringField is probably not the worst default choice
formfields.FIELDS['Geometry'] = formfields.StringField
uilib.PRINTERS['Geometry'] = uilib.print_string
formfields.FIELDS['Geography'] = formfields.StringField
uilib.PRINTERS['Geography'] = uilib.print_string
