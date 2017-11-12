# -*- coding: utf-8 -*-


abstract = """BACKGROUND:
The systematic, complete and correct reconstruction of genome-scale metabolic networks or metabolic pathways is one of 
the most challenging tasks in systems biology research. An essential requirement is the access to the complete 
biochemical knowledge - especially on the biochemical reactions. This knowledge is extracted from the scientific 
literature and collected in biological databases. Since the available databases differ in the number of biochemical 
reactions and the annotation of the reactions, an integrated knowledge resource would be of great value.

RESULTS:
We developed a comprehensive non-redundant reaction database containing known enzyme-catalyzed and spontaneous 
reactions. Currently, it comprises 18,172 unique biochemical reactions. As source databases the biochemical databases 
BRENDA, KEGG, and MetaCyc were used. Reactions of these databases were matched and integrated by aligning substrates 
and products. For the latter a two-step comparison using their structures (via InChIs) and names was performed. Each 
biochemical reaction given as a reaction equation occurring in at least one of the databases was included.

CONCLUSIONS:
An integrated non-redundant reaction database has been developed and is made available to users. The database can 
significantly facilitate and accelerate the construction of accurate biochemical models."""

url = 'http://bkm-react.tu-bs.de/download/Reactions_BKMS.tar.gz'
hgnc_lookup = 'http://www.genenames.org/cgi-bin/download?col=gd_app_sym&col=gd_enz_ids&status=Approved&status_opt=2&where=&order_by=gd_app_sym_sort&format=text&limit=&hgnc_dbtag=on&submit=submit'
pmid = 21824409
title = 'BKM-react, an integrated biochemical reaction database.'
description = """BKMS-react is an integrated and non-redundant biochemical reaction database containing known 
enzyme-catalyzed and spontaneous reactions. Biochemical reactions collected from BRENDA, KEGG, MetaCyc and SABIO-RK
 were matched and integrated by aligning substrates and products.""".replace('\n', '')
