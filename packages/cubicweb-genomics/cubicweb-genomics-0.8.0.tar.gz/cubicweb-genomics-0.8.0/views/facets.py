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

from cubicweb.web import facet
from cubicweb.selectors import is_instance


############################################################################
### GENOMIC FACETS -CGH ####################################################
############################################################################
class CghResultCghRatioFacet(facet.RangeFacet):
    __regid__ = 'cghresult-cgh-ratio'
    __select__ = facet.RangeFacet.__select__ & is_instance('CghResult')
    order = 1
    rtype = 'cgh_ratio'


class CghResultLog2RatioFacet(facet.RangeFacet):
    __regid__ = 'cghresult-log2-ratio'
    __select__ = facet.RangeFacet.__select__ & is_instance('CghResult')
    order = 3
    rtype = 'log2_ratio'


class CghResultStatusFacet(facet.AttributeFacet):
    __regid__ = 'cghresult-status'
    __select__ = facet.AttributeFacet.__select__ & is_instance('CghResult')
    order = 3
    rtype = 'status'


class CghResulNumProbesFacet(facet.RangeFacet):
    __regid__ = 'cghresult-numprobes-ratio'
    __select__ = facet.RangeFacet.__select__ & is_instance('CghResult')
    order = 4
    rtype = 'numbprobes'


############################################################################
### GENOMIC FACETS -MUTATION ###############################################
############################################################################
class MutationPositionInGeneFacet(facet.RangeFacet):
    __regid__ = 'mutation-positioningene'
    __select__ = facet.RangeFacet.__select__ & is_instance('Mutation')
    order = 1
    rtype = 'position_in_gene'


class MutationMutationTypeFacet(facet.AttributeFacet):
    __regid__ = 'mutation-mutationtype'
    __select__ = facet.RangeFacet.__select__ & is_instance('Mutation')
    order = 2
    rtype = 'mutation_type'


class MutationPloidyFacet(facet.AttributeFacet):
    __regid__ = 'mutation-ploidy'
    __select__ = facet.AttributeFacet.__select__ & is_instance('Mutation')
    order = 3
    rtype = 'ploidy'


class MutationValidFacet(facet.AttributeFacet):
    __regid__ = 'mutation-valid'
    __select__ = facet.AttributeFacet.__select__ & is_instance('Mutation')
    order = 4
    rtype = 'valid'


class MutationGeneFacet(facet.RelationAttributeFacet):
    __regid__ = 'mutation-gene'
    __select__ = facet.RelationAttributeFacet.__select__ & is_instance('Mutation')
    rtype = 'related_gene'
    role = 'subject'
    order = 5
    target_attr = 'gene_id'


class MutationReferenceBaseFacet(facet.AttributeFacet):
    __regid__ = 'mutation-reference_base'
    __select__ = facet.AttributeFacet.__select__ & is_instance('Mutation')
    order = 6
    rtype = 'reference_base'


class MutationVariantBaseFacet(facet.AttributeFacet):
    __regid__ = 'mutation-variant_base'
    __select__ = facet.AttributeFacet.__select__ & is_instance('Mutation')
    order = 7
    rtype = 'variant_base'
