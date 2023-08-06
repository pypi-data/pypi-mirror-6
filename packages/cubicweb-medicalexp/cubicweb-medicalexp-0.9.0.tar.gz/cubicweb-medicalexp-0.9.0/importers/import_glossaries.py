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

""" Import glossaries entities (e.g. Bodypart, Disease)
"""
import csv
from os import path as osp
from cubicweb.dataimport import SQLGenObjectStore, ucsvreader


HERE = osp.dirname(osp.abspath(__file__))
store = SQLGenObjectStore(session)


###############################################################################
### BODYLOCATION ##############################################################
###############################################################################
""" This come from the following sparql request on dbpedia.org
prefix dbpedia-owl:<http://dbpedia.org/ontology/>
prefix dbpprop:<http://dbpedia.org/property/>

select distinct ?u, ?t, ?n, ?a where
{?u a dbpedia-owl:AnatomicalStructure.
 ?u dbpprop:name ?t.
 OPTIONAL{?u dbpprop:meshnumber ?n.
          ?u dbpedia-owl:abstract ?a.
          FILTER (lang(?a)="en")}
  FILTER (lang(?t)="en")}"""
reader = ucsvreader(open(osp.join(HERE, 'bodylocation.csv')), separator='\t')
for identifier, name, mesh, descr in reader:
    store.create_entity('BodyLocation', identifier=identifier,
                        name=name, mesh_id=mesh, description=descr)


###############################################################################
### DISEASE ###################################################################
###############################################################################
"""This come from the following sparql request on dbpedia.org
prefix dbpedia-owl:<http://dbpedia.org/ontology/>
prefix dbpprop:<http://dbpedia.org/property/>

select distinct ?u, ?t, ?n, ?d, ?a where
{?u a dbpedia-owl:Disease.
 ?u dbpedia-owl:meshId ?n.
 ?u dbpedia-owl:icd10 ?d.
 ?u dbpedia-owl:abstract ?a.
 ?u rdfs:label ?t.
FILTER (lang(?t)="en" && lang(?a)="en")}"""
reader = ucsvreader(open(osp.join(HERE, 'disease.csv')), separator='\t')
for identifier, name, mesh, icd10, descr in reader:
    store.create_entity('Disease', identifier=identifier,
                        name=name, mesh_id=mesh, icd10=icd10[:64], description=descr)


###############################################################################
### DRUGS #####################################################################
###############################################################################
"""This come from the following sparql request on dbpedia.org
prefix dbpedia-owl:<http://dbpedia.org/ontology/>
prefix dbpprop:<http://dbpedia.org/property/>

select distinct ?u, ?t, ?pc, ?dg, ?fu, ?ca, ?iu, ?rd, ?m, ?a where
{?u a dbpedia-owl:Drug.
 ?u rdfs:label ?t.
 OPTIONAL{?u dbpedia-owl:pubchem ?pc.}
 OPTIONAL{?u dbpedia-owl:drugbank ?dg.}
 OPTIONAL{?u dbpedia-owl:fdaUniiCode ?fu.}
 OPTIONAL{?u dbpedia-owl:casNumber ?ca.}
 OPTIONAL{?u dbpedia-owl:iupcaName ?iu.}
 OPTIONAL{?u dbpprop:metabolism ?m.}
 OPTIONAL{?u dbpprop:routesOfAdministration ?rd.}
 OPTIONAL{?u dbpedia-owl:abstract ?a.
          FILTER (lang(?a)="en")}
  FILTER (lang(?t)="en")}"""
reader = ucsvreader(open(osp.join(HERE, 'drugs.csv')), separator='\t')
for identifier, name, pubchem, drugbank, fda, cas, iup, roa, met, descr in reader:
    store.create_entity('Drug', identifier=identifier, name=name,
                        pubchem_id=pubchem, drugbank_id=drugbank,
                        unii_id=fda, cas_number=cas, iupac_name=iup,
                        routes_of_administration=roa, metabolism=met, description=descr)


###############################################################################
### MEDICALTECHNIC ############################################################
###############################################################################
"""This come from the following sparql request on dbpedia.org
prefix dbpedia-owl:<http://dbpedia.org/ontology/>
prefix dbpprop:<http://dbpedia.org/property/>

select distinct ?u, ?t, ?a where
{?u dcterms:subject category:Laboratory_techniques.
 ?u rdfs:label ?t.
 OPTIONAL{?u dbpedia-owl:abstract ?a.
          FILTER (lang(?a)="en")}
  FILTER (lang(?t)="en")}

et


select distinct ?u, ?t, ?a where
{?u dcterms:subject category:Medical_tests.
 ?u rdfs:label ?t.
 OPTIONAL{?u dbpedia-owl:abstract ?a.
          FILTER (lang(?a)="en")}
  FILTER (lang(?t)="en")}"""
reader = ucsvreader(open(osp.join(HERE, 'medical_techs.csv')), separator='\t')
for identifier, name, descr in reader:
    store.create_entity('MedicalTechnique', identifier=identifier,
                        name=name, description=descr)


###############################################################################
### FLUSH AND COMMIT ##########################################################
###############################################################################
store.flush()
store.commit()
