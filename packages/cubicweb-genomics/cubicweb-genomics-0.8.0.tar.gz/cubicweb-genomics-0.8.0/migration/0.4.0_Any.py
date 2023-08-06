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

add_entity_type('GenomicRegion')

add_relation_definition('GenomicRegion', 'chromosome', 'Chromosome')
add_relation_definition('GenomicRegion', 'genes', 'Gene')
add_relation_definition('GenomicRegion', 'oncogenes', 'Gene')
add_relation_definition('GenomicRegion', 'atlas_genes', 'Gene')
add_relation_definition('GenomicRegion', 'census_genes', 'Gene')

add_attribute('CghResult', 'log2_ratio')
add_attribute('CghResult', 'status')
add_attribute('CghResult', 'numprobes')
drop_relation_definition('CghResult', 'related_gene', 'Gene')
add_relation_definition('CghResult', 'genomic_region', 'GenomicRegion')

add_relation_definition('Mutation', 'chromosomes', 'Chromosome')
