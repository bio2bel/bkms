# -*- coding: utf-8 -*-

"""Run this script with :code:`python3 -m bio2owl_bkms.to_bel`"""

from __future__ import print_function

import logging
import os

import pandas as pd

import bio2owl_chebi.download
from pybel_tools.constants import evidence_format, PYBEL_RESOURCES_ENV, pubmed
from resources import EC_PATTERN
from pybel_tools.document_utils import write_boilerplate
from pybel_tools.resources import CONFIDENCE, CHEBI_IDS

log = logging.getLogger(__name__)

url = 'http://bkm-react.tu-bs.de/download/Reactions_BKMS.tar.gz'
hgnc_lookup = 'http://www.genenames.org/cgi-bin/download?col=gd_app_sym&col=gd_enz_ids&status=Approved&status_opt=2&where=&order_by=gd_app_sym_sort&format=text&limit=&hgnc_dbtag=on&submit=submit'
pmid = 21824409
title = 'BKM-react, an integrated biochemical reaction database.'
description = """BKMS-react is an integrated and non-redundant biochemical reaction database containing known 
enzyme-catalyzed and spontaneous reactions. Biochemical reactions collected from BRENDA, KEGG, MetaCyc and SABIO-RK
 were matched and integrated by aligning substrates and products.""".replace('\n', '')

header = [
    'EC Number',
    'Name',
    'Reaction',
    'Reaction ID BRENDA',
    'Reaction ID KEGG',
    'Reaction ID MetaCyc',
    'Reaction ID SABIO-RK',
    'BRENDA Pathway Name',
    'KEGG Pathway ID',
    'KEGG Pathway Name',
    'MetaCyc Pathway ID',
    'MetaCyc Pathway Name',
    'Stoichiometry Check',
    'Missing Substrate',
    'Missing Product',
    'Comment KEGG',
    'Comment MetaCyc',
    'Remark'
]

data_cache_dir = os.path.join(os.path.expanduser('~'), '.pybel', 'data', 'bio2bel', 'bkms')
if not os.path.exists(data_cache_dir):
    os.makedirs(data_cache_dir)


def get_data():
    log.info('getting data')
    cache_path = os.path.join(data_cache_dir, 'Reactions_BKMS.csv')

    if os.path.exists(cache_path):
        log.info('loading BKMS from cache')
        df = pd.read_csv(cache_path, sep='\t', header=None, index_col=0, names=header)
    else:
        log.info('downloading BKMS')
        df = pd.read_csv(url, sep='\t', header=None, index_col=0, names=header, compression='gzip')

    return df


def get_chebi_mapping():
    chebi_df = bio2owl_chebi.download.download_names()
    name_to_id = {}
    for _, chebi_id, name, ctype, source in chebi_df[['COMPOUND_ID', 'NAME', 'TYPE', 'SOURCE']].sort_values(
            'COMPOUND_ID').itertuples():

        try:
            name_to_id[name.lower()] = chebi_id
        except:
            log.info('%s %s %s %s', chebi_id, name, ctype, source)
    return name_to_id


def write_bel(file):
    df = get_data()
    chebi_map = get_chebi_mapping()

    write_boilerplate(
        document_name='BKMS-react',
        description=description,
        contact='charles.hoyt@scai.fraunhofer.de',
        authors='Charles Tapley Hoyt',
        licenses='Creative Commons by 4.0',
        copyright='Copyright (c) 2017 Charles Tapley Hoyt. All rights reserved',
        namespace_dict={'CHEBIID': CHEBI_IDS},
        namespace_patterns={'EC': EC_PATTERN},
        annotations_dict={'Confidence': CONFIDENCE},
        file=file
    )

    print(pubmed(title, pmid), file=file)
    print(evidence_format.format('Serialized from BKMS-react'), file=file)
    print('SET Confidence = "Axiomatic"', file=file)
    key_errors, c = 0, 0
    for _, ec, reaction in df[['EC Number', 'Reaction']].itertuples():

        try:
            reactants, products = [x.strip() for x in reaction.split(' = ')]
        except:
            continue

        reactants = [c.strip() for c in reactants.split(' + ')]
        products = [c.strip() for c in products.split(' + ')]

        try:
            reactants_chebi = [chebi_map[r.strip().lower()] for r in reactants]
            reactants = ['a(CHEBIID:{})'.format(r) for r in reactants_chebi]

            products_chebi = [chebi_map[r.strip().lower()] for r in products]
            products = ['a(CHEBIID:{})'.format(r) for r in products_chebi]
        except KeyError:
            key_errors += 1
            continue
        except Exception as e:
            log.exception('prob')
            continue
        try:
            print('act(p(EC:"{}")) => rxn(reactants({}), products({}))'.format(
                ec,
                ','.join(reactants),
                ','.join(products)), file=file
            )
        except:
            log.exception('problem printing')

    log.info('Number key errors: %d', key_errors)
    log.info('Number problematic reactions: %d', c)


FILE = 'brenda.bel'


def add_to_pybel_resources():
    if PYBEL_RESOURCES_ENV not in os.environ:
        raise ValueError('{} not in os.environ'.format(PYBEL_RESOURCES_ENV))

    with open(os.path.join(os.environ[PYBEL_RESOURCES_ENV], 'knowledge', FILE), 'w') as f:
        write_bel(f)


if __name__ == '__main__':
    logging.basicConfig(level=20)
    log.setLevel(20)
    add_to_pybel_resources()
