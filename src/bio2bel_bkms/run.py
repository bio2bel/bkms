# -*- coding: utf-8 -*-

"""Run this script with :code:`python3 -m bio2bel_bkms.to_bel`"""

from __future__ import print_function

import logging
import os

from pybel.resources.arty import get_latest_arty_namespace
from pybel.resources.defaults import CONFIDENCE
from pybel.utils import ensure_quotes
from pybel_tools.constants import PYBEL_RESOURCES_ENV
from pybel_tools.document_utils import write_boilerplate
from .reference import description, pmid, title
from .parser import get_bkms_df

log = logging.getLogger(__name__)


class MissingDirection(ValueError):
    """Raised when can't figure out which way the reaction goes"""


def tokenize_reaction(reaction):
    """

    :param reaction:
    :rtype: tuple[list[str],list[str],str] or tuple[None, None, None]
    """
    try:
        if ' = ' in reaction:
            reactants, products = reaction.split(' = ')
            reversible = False
        elif ' <=> ' in reaction:
            reactants, products = reaction.split(' <=> ')
            reversible = True
        else:
            return None, None, None

    except Exception:
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
