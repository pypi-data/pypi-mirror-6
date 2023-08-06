# -*- coding: utf-8 -*-
# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# copyright 2013 CEA (Saclay, FRANCE), all rights reserved.
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

from cubicweb.web.views.csvexport import CSVRsetView
from cubicweb.selectors import is_instance


class SnpCSVView(CSVRsetView):
    """CSV view for SNP"""
    __select__ = CSVRsetView.__select__ & is_instance('Snp')

    def call(self):
        req = self._cw
        rows = [['"rs_id"', '"position"', '"chromosome"']]
        for entity in self.cw_rset.entities():
            row = [entity.rs_id, entity.position, entity.chromosome[0].name]
            rows.append(row)
        writer = self.csvwriter()
        writer.writerows(rows)


class GenomicMeasureCSVView(CSVRsetView):
    """CSV view for GenomicMeasure"""
    __select__ = CSVRsetView.__select__ & is_instance('GenomicMeasure')

    def call(self):
        req = self._cw
        rows = [('"subject_id"', '"type"', '"format"', '"filepath"')]
        for entity in self.cw_rset.entities():
            rows.append([entity.subject_id, entity.type,
                         entity.format, entity.filepath])
        writer = self.csvwriter()
        writer.writerows(rows)
