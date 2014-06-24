#!/usr/bin/env python
'''Test of NI-DM SPM export tool

@author: Camille Maumet <c.m.j.maumet@warwick.ac.uk>, Satrajit Ghosh
@copyright: University of Warwick 2014
'''
import unittest
import os
from subprocess import call
import re
import rdflib
from rdflib.graph import Graph
from TestResultDataModel import TestResultDataModel

import logging

logger = logging.getLogger(__name__)

# FIXME: Extend tests to more than one dataset (group analysis, ...)
'''Tests based on the analysis of single-subject auditory data based on test01_spm_batch.m using SPM12b r5918.
'''
class TestSPMResultsDataModel(unittest.TestCase, TestResultDataModel):

    def setUp(self):
        self.my_execption = ""

        # Display log messages in console
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

        TestResultDataModel.setUp(self) 
        self.ground_truth_dir = os.path.join(self.ground_truth_dir, 'spm', 'example001')

        # Current module directory is used as test directory
        self.test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'spmexport', 'example001')
        
        # RDF obtained by the SPM export 
        self.spmexport = Graph()

        #  Turtle file obtained with SPM NI-DM export tool
        self.spm_export_ttl = os.path.join(self.test_dir, 'spm_nidm.ttl');
        print "\n\nComparing: "+self.spm_export_ttl
        self.spmexport.parse(self.spm_export_ttl, format='turtle')


    '''Test01: Comparing that the ttl file generated by SPM and the expected ttl file (generated manually) are identical'''
    # FIXME: If terms PR is accepted then these tests should be moved to TestResultDataModel.py
    def test01_ex1_auditory_singlesub_full_graph(self):
        #  Turtle file of ground truth (manually computed) RDF
        ground_truth_ttl = os.path.join(self.ground_truth_dir, 'example001_spm_results.ttl');

        print "\n\nwith: "+ground_truth_ttl

        # RDF obtained by the ground truth export
        gt = Graph()
        gt.parse(ground_truth_ttl, format='turtle')

        self.compare_full_graphs(gt, self.spmexport)

        if self.my_execption:
            raise Exception(self.my_execption)


    # '''Test02: Test availability of attributes needed to perform a meta-analysis as specified in use-case *1* at: http://wiki.incf.org/mediawiki/index.php/Queries'''
    # def test02_metaanalysis_usecase1(self):
    #     prefixInfo = """
    #     prefix prov: <http://www.w3.org/ns/prov#>
    #     prefix spm: <http://www.fil.ion.ucl.ac.uk/spm/ns/#>
    #     prefix nidm: <http://nidm.nidash.org/>

    #     """
    #     # Look for:
    #     # - "location" of "Contrast map",
    #     # - "location" of "Contrast variance map",
    #     # - "prov:type" in "nidm" namespace of the analysis software.
    #     query = prefixInfo+"""
    #     SELECT ?cfile ?efile ?stype WHERE {
    #      ?aid a spm:contrast ;
    #           prov:wasAssociatedWith ?sid.
    #      ?sid a prov:Agent;
    #           a prov:SoftwareAgent;
    #           a ?stype . 
    #      FILTER regex(str(?stype), "nidm") 
    #      ?cid a nidm:contrastMap ;
    #           prov:wasGeneratedBy ?aid ;
    #           prov:atLocation ?cfile .
    #      ?eid a nidm:contrastStandardErrorMap ;
    #           prov:wasGeneratedBy ?aid ;
    #           prov:atLocation ?efile .
    #     }
    #     """

    #     if not self.successful_retreive(self.spmexport.query(query), 'ContrastMap and ContrastStandardErrorMap'):
    #         raise Exception(self.my_execption)

    # '''Test03: Test availability of attributes needed to perform a meta-analysis as specified in use-case *2* at: http://wiki.incf.org/mediawiki/index.php/Queries'''
    # def test03_metaanalysis_usecase2(self):
    #     prefixInfo = """
    #     prefix prov: <http://www.w3.org/ns/prov#>
    #     prefix spm: <http://www.fil.ion.ucl.ac.uk/spm/ns/#>
    #     prefix nidm: <http://nidm.nidash.org/>

    #     """

    #     # Look for:
    #     # - "location" of "Contrast map",
    #     # - "prov:type" in "nidm" namespace of the analysis software.
    #     query = prefixInfo+"""
    #     SELECT ?cfile ?efile ?stype WHERE {
    #      ?aid a spm:contrast ;
    #           prov:wasAssociatedWith ?sid.
    #      ?sid a prov:Agent;
    #           a prov:SoftwareAgent;
    #           a ?stype . 
    #      FILTER regex(str(?stype), "nidm") 
    #      ?cid a nidm:contrastMap ;
    #           prov:wasGeneratedBy ?aid ;
    #           prov:atLocation ?cfile .
    #     }
    #     """

    #     if not self.successful_retreive(self.spmexport.query(query), 'ContrastMap and ContrastStandardErrorMap'):
    #         raise Exception(self.my_execption)

    # '''Test04: Test availability of attributes needed to perform a meta-analysis as specified in use-case *3* at: http://wiki.incf.org/mediawiki/index.php/Queries'''
    # def test04_metaanalysis_usecase3(self):
    #     prefixInfo = """
    #     prefix prov: <http://www.w3.org/ns/prov#>
    #     prefix spm: <http://www.fil.ion.ucl.ac.uk/spm/ns/#>
    #     prefix nidm: <http://nidm.nidash.org/>

    #     """

    #     # Look for:
    #     # - "location" of "Statistic Map",
    #     # - "nidm:errorDegreesOfFreedom" in "Statistic Map".
    #     query = prefixInfo+"""
    #     SELECT ?sfile ?dof WHERE {
    #      ?sid a nidm:statisticalMap ;
    #           prov:atLocation ?sfile ;
    #           nidm:errorDegreesOfFreedom ?dof .
    #     }
    #     """

    #     if not self.successful_retreive(self.spmexport.query(query), 'ContrastMap and ContrastStandardErrorMap'):
    #         raise Exception(self.my_execption)

    # '''Test05: Test availability of attributes needed to perform a meta-analysis as specified in use-case *4* at: http://wiki.incf.org/mediawiki/index.php/Queries'''
    # def test05_metaanalysis_usecase4(self):
    #     prefixInfo = """
    #     prefix prov: <http://www.w3.org/ns/prov#>
    #     prefix spm: <http://www.fil.ion.ucl.ac.uk/spm/ns/#>
    #     prefix nidm: <http://nidm.nidash.org/>

    #     """

    #     # Look for:
    #     # - For each "Peak" "equivZStat" and"coordinate1" (and optionally "coordinate2" and "coordinate3"),
    #     # - "clusterSizeInVoxels" of "height threshold"
    #     # - "value" of "extent threshold"
    #     query = prefixInfo+"""
    #     SELECT ?equivz ?coord1 ?coord2 ?coord3 ?ethresh ?hthresh WHERE {
    #      ?pid a spm:peakStatistic ;
    #         prov:atLocation ?cid ;
    #         nidm:equivalentZStatistic ?equivz ;
    #         prov:wasDerivedFrom ?clid .
    #      ?cid a nidm:coordinate;
    #         nidm:coordinate1 ?coord1 .
    #         OPTIONAL { ?cid nidm:coordinate2 ?coord2 }
    #         OPTIONAL { ?cid nidm:coordinate3 ?coord3 }
    #      ?iid a nidm:inference .
    #      ?esid a spm:excursionSet;
    #         prov:wasGeneratedBy ?iid .
    #      ?setid a spm:setStatistic;
    #         prov:wasDerivedFrom ?esid .
    #      ?clid a spm:clusterStatistic;
    #         prov:wasDerivedFrom ?setid .
    #      ?tid a nidm:extentThreshold ;
    #         nidm:clusterSizeInVoxels ?ethresh .
    #      ?htid a nidm:heightThreshold ;
    #         prov:value ?hthresh .
    #     }
    #     """

    #     if not self.successful_retreive(self.spmexport.query(query), 'ContrastMap and ContrastStandardErrorMap'):
    #         raise Exception(self.my_execption)



if __name__ == '__main__':
    unittest.main()
