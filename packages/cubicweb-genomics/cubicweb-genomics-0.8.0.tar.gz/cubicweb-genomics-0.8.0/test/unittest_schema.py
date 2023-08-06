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

""" Schema test """

from cubicweb.devtools.testlib import CubicWebTC

class GenomicSchemaTC(CubicWebTC):
    """ Test proper behavior with respect to the composite relations. """
    def setup_database(self):
        """ Several entities involving composite relations are created,
            according to the schema.
        """
        req = self.request()
        t_gen_meas = req.create_entity('GenomicMeasure',
                                       type=u'Test measure type', format=u'raw')
        t_chrom = req.create_entity('Chromosome', name=u'Test chr 1', identifier=u'chr1')
        t_other_chrom = req.create_entity('Chromosome', name=u'Test chr 2', identifier=u'chr2')
        t_gen_reg = req.create_entity('GenomicRegion', start=5, stop=1000, width=500,
                                      cytoband_start=u'c123', cytoband_stop=u'c567',
                                      chromosome=t_chrom)
        t_gene = req.create_entity('Gene', gene_id=u'BRAF', chromosomes=[t_chrom, t_other_chrom])
        t_cgh_res = req.create_entity('CghResult', cgh_ratio=23.5e-4, log2_ratio=2.3e-5,
                                      status=u'S', numprobes=4, related_measure=t_gen_meas,
                                      genomic_region=t_gen_reg)
        t_mutation = req.create_entity('Mutation', position_in_gene=14,
                                       mutation_type=u'test type', reference_base=u'A',
                                       variant_base=u'G',
                                       related_measure=t_gen_meas,
                                       related_gene=t_gene)
        t_snp = req.create_entity('Snp', rs_id=u'test snp', position=123456789,
                                  chromosome=t_chrom, gene=t_gene)
        t_col_ref = req.create_entity('ColumnRef', name=u'red', type=u'Test colref type',
                                      measure=t_gen_meas)

    def test_cleanup_on_measure_delete(self):
        """ Test that on GenomicMeasure deletion, CghResult, Mutation and ColumnRef
            are deleted, while GenomicRegion, Gene and Chromosome are not deleted.
        """
        req = self.request()
        t_gen_meas = req.execute('Any X WHERE X is GenomicMeasure').get_entity(0, 0)
        req.execute('DELETE GenomicMeasure X WHERE X eid %(gmeseid)s',
                    {'gmeseid': t_gen_meas.eid})
        self.commit()
        db_cgh_res = req.execute('Any X WHERE X is CghResult')
        if db_cgh_res:
            self.fail('The CghResult was not deleted.')
        db_mutation = req.execute('Any X WHERE X is Mutation')
        if db_mutation:
            self.fail('The Mutation was not deleted.')
        db_colref = req.execute('Any X WHERE X is ColumnRef')
        if db_colref:
            self.fail('The ColumnRef was not deleted.')
        db_gen_reg = req.execute('Any X WHERE X is GenomicRegion')
        if not db_gen_reg:
            self.fail('The GenomicRegion was deleted.')
        db_gene = req.execute('Any X WHERE X is Gene')
        if not db_gene:
            self.fail('The Gene was deleted')
        db_chrom = req.execute('Any X WHERE X is Chromosome')
        if not db_chrom:
            self.fail('The Chromosome was deleted.')

    def test_cleanup_on_chromosome_delete(self):
        """ Test that on Chromosome deletion, GenomicRegion, CghResult
            and Snp are deleted, while Gene and GenomicMeasure are
            not deleted.
        """
        req = self.request()
        t_chrom = req.execute('Any X WHERE X is Chromosome, '
                              'X identifier "chr1"').get_entity(0, 0)
        req.execute('DELETE Chromosome X WHERE X eid %(chromeid)s',
                    {'chromeid': t_chrom.eid})
        self.commit()
        db_gen_reg = req.execute('Any X WHERE X is GenomicRegion')
        if db_gen_reg:
            self.fail('The GenomicRegion was not deleted.')
        db_cgh_res = req.execute('Any X WHERE X is CghResult')
        if db_cgh_res:
            self.fail('The CghResult was not deleted.')
        db_snp = req.execute('Any X WHERE X is Snp')
        if db_snp:
            self.fail('The Snp was not deleted.')
        db_gene = req.execute('Any X WHERE X is Gene')
        if not db_gene:
            self.fail('The Gene was deleted.')
        db_gen_meas = req.execute('Any X WHERE X is GenomicMeasure')
        if not db_gen_meas:
            self.fail('The GenomicMeasure was deleted.')

    def test_cleanup_on_region_delete(self):
        """ Test than on GenomicRegion delete, the CghResult
            is deleted, while no Chromosome is deleted.
        """
        req = self.request()
        t_gen_reg = req.execute('Any X WHERE X is GenomicRegion').get_entity(0, 0)
        req.execute('DELETE GenomicRegion X WHERE X eid %(gregeid)s',
                    {'gregeid': t_gen_reg.eid})
        self.commit()
        db_cgh_result = req.execute('Any X WHERE X is CghResult')
        if db_cgh_result:
            self.fail('The CghResult was not deleted.')
        db_chroms = req.execute('Any X WHERE X is Chromosome')
        if db_chroms.rowcount < 2:
            self.fail('Some Chromosomes have been deleted.')

    def test_cleanup_on_gene_delete(self):
        """ Test that on Gene deletion, Snp and Mutation are deleted,
            while no Chromosome is deleted.
        """
        req = self.request()
        t_gene = req.execute('Any X WHERE X is Gene').get_entity(0, 0)
        req.execute('DELETE Gene X WHERE X eid %(geid)s', {'geid': t_gene.eid})
        self.commit()
        db_snp = req.execute('Any X WHERE X is Snp')
        if db_snp:
            self.fail('The Snp was not deleted.')
        db_mutation = req.execute('Any X WHERE X is Mutation')
        if db_mutation:
            self.fail('The Mutation was not deleted.')


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
