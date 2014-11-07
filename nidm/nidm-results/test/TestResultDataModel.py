#!/usr/bin/env python
'''Common tests across-software for NI-DM export. 
The software-specific test classes must inherit from this class.

@author: Camille Maumet <c.m.j.maumet@warwick.ac.uk>, Satrajit Ghosh
@copyright: University of Warwick 2014
'''
import os
import rdflib

import logging
from Constants import *

logger = logging.getLogger(__name__)


def get_readable_name(graph, item):
    if isinstance(item, rdflib.term.Literal):
        if item.datatype:
            typeStr = graph.qname(item.datatype)
        else:
            typeStr = '(None)'
        name = typeStr+" '"+item+"'"
    elif isinstance(item, rdflib.term.URIRef):
        # Look for label
        # name = graph.label(item)
        name = graph.qname(item)
    else:
        name = "unsupported type: "+item
    return name

def get_alternatives(graph,s=None,p=None, o=None):
    found = ""
    
    for (s_in,  p_in, o_in) in graph.triples((s,  p, o)):
        if not o:  
            found += "; "+get_readable_name(graph, o_in)
        if not p:  
            found += "; "+get_readable_name(graph, p_in)
        if not s:  
            found += "; "+get_readable_name(graph, s_in)
    if len(found) > 200:
        found = '<many alternatives>'
    else:
        found = found[2:]
    return found

# FIXME: Extend tests to more than one dataset (group analysis, ...)
'''Tests based on the analysis of single-subject auditory data based on test01_spm_batch.m using SPM12b r5918.

@author: Camille Maumet <c.m.j.maumet@warwick.ac.uk>, Satrajit Ghosh
@copyright: University of Warwick 2014
'''
class TestResultDataModel(object):
    def setUp(self):
        self.ground_truth_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        self.my_execption = ""

        # # Current script directory is test directory (containing test data)
        # self.test_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

    def print_results(self, res):
        '''Print the results query 'res' to the console'''
        for idx, row in enumerate(res.bindings):
            rowfmt = []
            print "Item %d" % idx
            for key, val in sorted(row.items()):
                rowfmt.append('%s-->%s' % (key, val.decode()))
            print '\n'.join(rowfmt)

    def successful_retreive(self, res, info_str=""):
        '''Check if the results query 'res' contains a value for each field'''
        if not res.bindings:
            self.my_execption = info_str+""": Empty query results"""
            return False
        for idx, row in enumerate(res.bindings):
            for key, val in sorted(row.items()):
                logging.debug('%s-->%s' % (key, val.decode()))
                if not val.decode():
                    self.my_execption += "\nMissing: \t %s" % (key)
                    return False
        return True

        # if not self.successful_retreive(self.spmexport.query(query), 'ContrastMap and ContrastStandardErrorMap'):
        #     raise Exception(self.my_execption)

    def _reconcile_graphs(self, graph1, graph2, recursive=10):
        """Reconcile: if two entities have exactly the same attributes: they
        are considered to be the same (set the same id for both)
        """
        reconciled = set()
        for r in range(0, recursive):
            subs = set(graph1.subjects())-reconciled
            for s in subs:
                gt_subjects = None
                for p, o in graph1.predicate_objects(s):
                    if gt_subjects is None:
                        gt_subjects = set(graph2.subjects(p, o))
                    else:
                        gt_subjects = gt_subjects.intersection(\
                            set(graph2.subjects(p, o)))

                if gt_subjects:
                    # We found an URI in gt with the same predicates and objects
                    for gt_s in gt_subjects:
                        identical = True
                        # Check that all (predicate, object) pairs are in s
                        for p, o in graph2.predicate_objects(s):
                            if not (s,p,o) in graph1:
                                identical = False
                                break;

                        if identical:
                            break;

                    if identical:
                        reconciled.add(gt_s)
                        if not s==gt_s:
                            logging.debug(str(s)+" identical to "+str(gt_s))
                            for p, o in graph1.predicate_objects(s):
                                graph1.remove((s,p,o))
                                graph1.add((gt_s,p,o))
                            o=s
                            for s,p in graph1.subject_predicates(o):
                                graph1.remove((s,p,o))
                                graph1.add((s,p,gt_s))                                
                            
        return graph1


    def compare_full_graphs(self, gt_graph, other_graph):
        ''' Compare gt_graph and other_graph '''

        other_graph = self._reconcile_graphs(other_graph, gt_graph)

        # Check for predicates which are not in common to both graphs (XOR)
        diff_graph =  gt_graph ^ other_graph

        # FIXME: There is probably something better than using os.path.basename to remove namespaces
        exlude = list()
        missing_s = list()

        exc_wrong = ""
        exc_wrong_literal = ""
        exc_added = ""
        exc_missing = ""

        for s,p,o in diff_graph.triples( (None,  None, None) ):
            # If triple is found in other_graph
            if (s,  p, o) in other_graph:
                # If subject is *not* found in gt_graph
                if (s,  None, None) not in gt_graph:
                    if not s in exlude:
                        if not isinstance(s, rdflib.term.BNode):
                            exc_added += "\nAdded s:\t'%s'"%(get_readable_name(other_graph,s))
                            exlude.append(s)
                # If predicate p is *not* found in gt_graph
                elif (None,  p, None) not in gt_graph:
                    if not p in exlude:
                        exc_added += "\nAdded p:\t'%s'"%(get_readable_name(other_graph,p))
                        exlude.append(p)
                # If subject and predicate found in gt_graph, then object is wrong
                elif (s,  p, None) in gt_graph:
                    if isinstance(o, rdflib.term.Literal):
                        exc_wrong_literal += "\nWrong literal o:\t p('%s') of s('%s') is o(%s) but should be o(%s)."%(get_readable_name(other_graph, p),get_readable_name(other_graph, s),get_readable_name(other_graph, o),get_alternatives(gt_graph,s=s,p=p))
                    elif not isinstance(o, rdflib.term.BNode):
                        exc_wrong += "\nWrong o:\ts('%s') p('%s') o('%s') not in gold std, o should be o(%s)?)"%(get_readable_name(other_graph, s),get_readable_name(other_graph, p),get_readable_name(other_graph, o),get_alternatives(gt_graph,s=s,p=p))
                                # If object o is *not* found in gt_graph (and o is a URI, i.e. not the value of an attribute)
                elif (None,  None, o) not in gt_graph and isinstance(o, rdflib.term.URIRef):
                    if not o in exlude:
                        exc_added += "\nAdded o:\t'%s'"%(get_readable_name(other_graph,o))
                        exlude.append(o)
                # If subject and object found in gt_graph, then predicate is wrong
                elif (s,  None, o) in gt_graph:
                    exc_wrong += "\nWrong p:\tBetween '%s' and '%s' is '%s' (should be '%s'?)"%(get_readable_name(other_graph,s),get_readable_name(other_graph,o),get_readable_name(other_graph,p),get_alternatives(gt_graph,s=s,o=o))
                # If predicate and object found in gt_graph, then subject is wrong
                elif (None,  p, o) in gt_graph:
                    if not (s, None, None) in gt_graph:
                        if not s in exlude:
                            exc_added += "\nAdded:\t'%s'"%(s)
                            exlude.append(s)
                    else:
                        exc_wrong += "\nWrong s:\ts('%s') p('%s') o('%s') not in gold std (should be s: '%s'?)"%(get_readable_name(other_graph, s),get_readable_name(other_graph, p),get_readable_name(other_graph, o),get_alternatives(gt_graph,p=p,o=o))
                        # exc_wrong += "\nWrong s:\t'%s' \tto '%s' \tis '%s' (instead of %s)."%(os.path.basename(p),get_readable_name(other_graph, o),os.path.basename(s),found_subject)
                # If only subject found in gt_graph
                elif (s,  None, None) in gt_graph:
                    # gt_graph_possible_value = ""
                    # for (s_gt_graph,  p_gt_graph, o_gt_graph) in gt_graph.triples((s,  p, None)):
                    #     gt_graph_possible_value += "; "+os.path.basename(p_gt_graph)
                    exc_added += "\nAdded:\tin '%s', '%s' \t ('%s')."%(get_readable_name(gt_graph, s),get_readable_name(other_graph, p),get_readable_name(other_graph, o))
                else:
                    exc_added += "\nAdded:\tin '%s', '%s' \t ('%s')."%(get_readable_name(gt_graph, s),get_readable_name(other_graph, p),get_readable_name(other_graph, o))
                
            # If subject and predicate are found in gt_graph 
            elif (s,  p, o) in gt_graph:
                # This has already been taken into account as "Wrong o" or "Wrong literal o"
                if not (s,  p, None) in other_graph:
                #     if isinstance(o, rdflib.term.Literal):
                #         if (not exc_wrong_literal):
                #             exc_wrong_literal += "\nWrong literal o:\t p('%s') of s('%s') is ('%s') (instead o: '%s'?)"%(get_readable_name(gt_graph, p),get_readable_name(gt_graph, s),get_readable_name(gt_graph, o),get_alternatives(other_graph,s=s,p=p))
                # else:
                #     if (not exc_missing):
                #         exc_missing += "\nMissing o (%s):\tp('%s') o('%s') \ton '%s'"%(type(o), get_readable_name(gt_graph,p),get_readable_name(gt_graph,o),get_readable_name(gt_graph,s))
                    # If subject found in other_graph
                    if (s,  None, None) in other_graph:
                        exc_missing += "\nMissing p:\tp('%s') \ton '%s' (o('%s'))"%(get_readable_name(gt_graph,p),get_readable_name(gt_graph,s),get_readable_name(gt_graph,o))
                    # If subject is *not* found in other_graph
                    else:
                        if not s in missing_s:
                            if not isinstance(s, rdflib.term.BNode):
                                exc_missing += "\nMissing s:\t'%s' "%(get_readable_name(gt_graph,s))
                                missing_s.append(s)

        self.my_execption += exc_missing+exc_added+exc_wrong+exc_wrong_literal