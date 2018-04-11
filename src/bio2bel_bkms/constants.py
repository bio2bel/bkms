# -*- coding: utf-8 -*-

import os

from bio2bel.utils import get_data_dir

MODULE_NAME = 'bkms'
DATA_DIR = get_data_dir(MODULE_NAME)

BKMS_DATA_URL = 'http://bkm-react.tu-bs.de/download/Reactions_BKMS.tar.gz'
BKMS_DATA_PATH = os.path.join(DATA_DIR, 'Reactions_BKMS.tar.gz')

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

hgnc_lookup = 'http://www.genenames.org/cgi-bin/download?col=gd_app_sym&col=gd_enz_ids&status=Approved&status_opt=2&where=&order_by=gd_app_sym_sort&format=text&limit=&hgnc_dbtag=on&submit=submit'
