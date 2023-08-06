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

"""cubicweb-genomics schema"""


from yams.buildobjs import (EntityType, RelationDefinition,
                            SubjectRelation, String, RichString,
                            BigInt, Int, Float, Boolean)


###############################################################################
### DATA / RESULTS ENTITIES ###################################################
###############################################################################
class CghResult(EntityType):
    """ CGH results """
    cgh_ratio = Float(required=True)
    log2_ratio = Float(required=True)
    status = String(required=True, maxsize=4)
    numprobes = Int(required=True)
    related_measure = SubjectRelation('GenomicMeasure', cardinality='?*', inlined=True, composite='object')
    genomic_region = SubjectRelation('GenomicRegion', cardinality='?*', inlined=True, composite='object')


class Mutation(EntityType):
    """ Mutational results """
    position_in_gene = Int(required=True) # Position
    mutation_type = String(required=True) # Type, first time
    mutation_id = String(maxsize=128) # Target ID
    ploidy = String(vocabulary=('Het', 'Hom'))
    valid = Boolean(indexed=True)
    biological_classification = String(maxsize=256) # Classification bio / annotation
    classification_type = String(maxsize=256) # Type, second time
    conclusions = String(maxsize=2048) # Concl
    related_measure = SubjectRelation('GenomicMeasure', cardinality='?*', inlined=True, composite='object')
    related_gene = SubjectRelation('Gene', cardinality='?*', inlined=True, composite='object')
    # Variant
    reference_base = String(vocabulary=('A', 'T', 'G', 'C'), required=True) # Ref, first time
    variant_base = String(vocabulary=('A', 'T', 'G', 'C'), required=True) # Variant
    variant_frequency = Float(indexed=True) # Var Freq
    p_value = Float() # P-value
    coverage = Int() # Coverage
    reference_coverage = Int() # Ref Cov
    variant_coverage = Int() # Var Cov
    # Ids
    hotspot_id = String(maxsize=256) # HotSpot
    reference_id = String(maxsize=256) # Ref, second time
    locus_version = String(maxsize=256) # NM
    # Additional infos - Fetched from external bases ?
    comment = String(maxsize=2048) # Comm.x
    protein = String(maxsize=256) # Prot
    nucl = String(maxsize=256) # Nucl
    polyphen = String(maxsize=256) # Polyphen
    sift = String(maxsize=256) # SIFT
    gvd_alignment = String(maxsize=256) # AlignGVD
    base = String(maxsize=256) # Base
    medical_coverage = Int() # Cov Med


###############################################################################
### GENETICS ENTITIES #########################################################
###############################################################################
class Chromosome(EntityType):
    """ Chromosome definition """
    name = String(required=True, unique=True, maxsize=16)
    identifier = String(required=True, indexed=True, maxsize=64)


class Gene(EntityType):
    """ Gene definition """
    name = String(maxsize=256, fulltextindexed=True, indexed=True)
    gene_id = String(maxsize=256, required=True, indexed=True)
    uri = String(maxsize=256, indexed=True)
    start_position = Int(indexed=True)
    stop_position = Int(indexed=True)
    # Allow for translocated genes
    chromosomes = SubjectRelation('Chromosome', cardinality='+*')


class GenomicRegion(EntityType):
    """ Genomic region definition """
    start = Int(required=True)
    stop = Int(required=True)
    width = Int(required=True)
    cytoband_start = String(required=True)
    cytoband_stop = String(required=True)
    chromosome = SubjectRelation('Chromosome', cardinality='1*', inlined=True, composite='object')
    genes = SubjectRelation('Gene', cardinality='**')
    oncogenes = SubjectRelation('Gene', cardinality='**')
    atlas_genes = SubjectRelation('Gene', cardinality='**')
    census_genes = SubjectRelation('Gene', cardinality='**')


class Snp(EntityType):
    """ SNP definition """
    rs_id = String(required=True, unique=True, maxsize=16)
    position = BigInt(required=True, indexed=True)
    chromosome = SubjectRelation('Chromosome', cardinality='1*', inlined=True, composite='object')
    gene = SubjectRelation('Gene', cardinality='**', composite='object')


###############################################################################
### MEASURE ENTITIES ##########################################################
###############################################################################
class GenomicMeasure(EntityType):
    """ A genomic measure """
    type = String(maxsize=256, required=True, indexed=True)
    format = String(maxsize=128, indexed=True)
    chip_serialnum = Int()
    completed = Boolean(indexed=True)
    valid = Boolean(indexed=True)
    platform = SubjectRelation('GenomicPlatform', cardinality='?*', inlined=True)


class GenomicPlatform(EntityType):
    name = String(required=True, maxsize=64)
    related_snps = SubjectRelation('Snp', cardinality='**')


class ColumnRef(EntityType):
    """ Type is channel for transcriptom measure, lane for NGS measure.
        When type is channel, name will be red or green
    """
    name = String(vocabulary=('red', 'green'))
    type = String(maxsize=256, required=True, indexed=True)
    measure = SubjectRelation('GenomicMeasure', cardinality='1*', inlined=True, composite='object')
