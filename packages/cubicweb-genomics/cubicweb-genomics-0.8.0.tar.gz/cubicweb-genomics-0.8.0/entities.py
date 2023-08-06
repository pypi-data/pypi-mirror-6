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

"""cubicweb-genomics entity's classes"""
import os.path as osp

from cubicweb.entities import AnyEntity, fetch_config


class GenomicMeasure(AnyEntity):
    __regid__ = 'GenomicMeasure'
    fetch_attrs, fetch_order = fetch_config(('type', 'format'))

    def dc_title(self):
        return u'%s (%s)' % (self._cw._('GenomicMeasure'), self.type)

    @property
    def image_url(self):
        return self._cw.data_url('48x48/genetics.png')

    @property
    def full_filepath(self):
        return self.filepath

    @property
    def subject_id(self):
        """ Return the subject id. Should be overloaded in concrete application
        of this cube """
        return None

    @property
    def formatted_chip_serialnum(self):
        """ Formatted chip serial num
        """
        if self.chip_serialnum:
            return self.chip_serialnum
        else:
            return 'N/A'


class GenomicRegion(AnyEntity):
    __regid__ = 'GenomicRegion'
    fetch_attrs, fetch_order = fetch_config(('start', 'stop', 'chromosome'))


    def dc_title(self):
        return '%s %s (%s-%s)' % (self._cw._('Chromosome'), self.chromosome[0].dc_title(),
                                  self.start, self.stop)
