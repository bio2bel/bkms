# -*- coding: utf-8 -*-

"""Run this script with :code:`python3 -m bio2bel_bkms.to_bel`"""

from __future__ import print_function

import logging
import os

import pandas as pd

from pybel.resources.arty import get_latest_arty_namespace
from pybel.resources.defaults import CONFIDENCE
from pybel.utils import ensure_quotes
from pybel_tools.constants import PYBEL_RESOURCES_ENV, evidence_format
from pybel_tools.document_utils import write_boilerplate
from .constants import description, pmid, title, url

log = logging.getLogger(__name__)

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
        df = pd.read_csv(url, sep='\t', header=None, index_col=0, names=header, skiprows=3, compression='gzip')

    return df


class MissingDirection(ValueError):
    """Raised when can't figure out which way the reaction goes"""


def tokenize_reaction(reaction):
    try:
        if ' = ' in reaction:
            reactants, products = reaction.split(' = ')
            reversible = False
        elif ' <=> ' in reaction:
            reactants, products = reaction.split(' <=> ')
            reversible = True
        else:
            raise MissingDirection
    except MissingDirection:
        return None, None, None
    except:
        return None, None, None

    reactants = [reactant.strip() for reactant in reactants.strip().split(' + ')]
    products = [product.strip() for product in products.strip().split(' + ')]

    return reactants, products, reversible


def find_compound(compound_ids, ontology_id_name, ontology_alternate_id_map):
    for cid in compound_ids:

        if cid in ontology_id_name:
            return ontology_id_name[cid]

        if cid in ontology_alternate_id_map:
            return ontology_id_name[ontology_alternate_id_map[cid]]


def run(bkms_df, thesaurus_folded_name, thesaurus_name_ids, ontology_id_name, ontology_alternate_id_map):
    bkms_names = set()
    reactions_for_bel = []

    for _, ec, reaction in bkms_df[['EC Number', 'Reaction']].itertuples():

        reactants, products, reversible = tokenize_reaction(reaction)

        if reactants is None:
            continue

        for r in reactants:
            bkms_names.add(r)

        for r in products:
            bkms_names.add(r)

        if not (all(r.casefold() in thesaurus_folded_name for r in reactants) and
                    all(r.casefold() in thesaurus_folded_name for r in products)):
            continue

        reactants = [
            find_compound(thesaurus_name_ids[thesaurus_folded_name[reactant.casefold()]], ontology_id_name,
                          ontology_alternate_id_map)
            for reactant in reactants
        ]

        products = [
            find_compound(thesaurus_name_ids[thesaurus_folded_name[product.casefold()]], ontology_id_name,
                          ontology_alternate_id_map)
            for product in products
        ]

        reactions_for_bel.append((
            ec,
            reactants,
            products,
            reversible,
        ))


def print_reaction_helper(ec, reactants, products, file=None):
    if not ec or isinstance(ec, float) or ec.lower() in {'nan', 'spontaneous'}:
        print(
            'rxn(reactants({}), products({}))'.format(
                ', '.join('a(CHEBI:{})'.format(ensure_quotes(r)) for r in reactants),
                ', '.join('a(CHEBI:{})'.format(ensure_quotes(r)) for r in products),
            ),
            file=file
        )
    else:
        print(
            'act(p(EC:"{}")) => rxn(reactants({}), products({}))'.format(
                ec,
                ', '.join('a(CHEBI:{})'.format(ensure_quotes(r)) for r in reactants),
                ', '.join('a(CHEBI:{})'.format(ensure_quotes(r)) for r in products),
            ),
            file=file
        )


def print_reaction(ec, reactants, products, reversible=False, file=None):
    print_reaction_helper(ec, reactants, products, file=file)

    if reversible:
        print_reaction_helper(ec, reactants, products, file=file)


def write_bkms_boilerplate(file):
    write_boilerplate(
        name='BKMS-react',
        description=description,
        contact='charles.hoyt@scai.fraunhofer.de',
        authors='Charles Tapley Hoyt',
        licenses='Creative Commons by 4.0',
        copyright='Copyright (c) 2017 Charles Tapley Hoyt. All rights reserved',
        namespace_url={'CHEBI': get_latest_arty_namespace('chebi')},
        namespace_patterns={'EC': '.+'},
        annotation_url={'Confidence': CONFIDENCE},
        file=file
    )

    print('SET Citation = {{"{}", "{}"}}'.format(title, pmid), file=file)
    print(evidence_format.format('Serialized from BKMS-react'), file=file)
    print('SET Confidence = "Axiomatic"', file=file)


def write_reactions(df, file=None):
    key_errors, c = 0, 0
    for _, ec, reaction in df[['EC Number', 'Reaction']].itertuples():

        reactants, products, reversible = tokenize_reaction(reaction)

        if reactants is None and products is None:
            continue

        try:
            reactants = [
                r.strip().lower()
                for r in reactants
            ]

            products = [
                r.strip().lower()
                for r in products
            ]

            print_reaction(ec, reactants, products, reversible, file=file)

        except KeyError:
            key_errors += 1
            continue

        except Exception as e:
            log.exception('prob')
            continue

    log.info('Number key errors: %d', key_errors)
    log.info('Number problematic reactions: %d', c)


def write_bel(file):
    write_bkms_boilerplate(file)

    df = get_data()
    write_reactions(df)


def add_to_pybel_resources():
    if PYBEL_RESOURCES_ENV not in os.environ:
        raise ValueError('{} not in os.environ'.format(PYBEL_RESOURCES_ENV))

    with open(os.path.join(os.environ[PYBEL_RESOURCES_ENV], 'knowledge', 'brenda.bel'), 'w') as f:
        write_bel(f)
