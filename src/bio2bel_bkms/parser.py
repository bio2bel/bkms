# -*- coding: utf-8 -*-

import logging
import os
from urllib.request import urlretrieve

import pandas as pd

from .constants import BKMS_DATA_PATH, BKMS_DATA_URL, header

log = logging.getLogger(__name__)


def download_bkms(force_download=False):
    """Downloads the bkms data

    :param bool force_download: If true, overwrites a previously cached file
    :rtype: str
    """
    if os.path.exists(BKMS_DATA_URL) and not force_download:
        log.info('using cached data at %s', BKMS_DATA_PATH)
    else:
        log.info('downloading %s to %s', BKMS_DATA_URL, BKMS_DATA_PATH)
        urlretrieve(BKMS_DATA_URL, BKMS_DATA_PATH)

    return BKMS_DATA_PATH


def get_bkms_df(url=None, cache=True, force_download=False):
    """Gets the BKMS file

    :param Optional[str] url: The URL (or file path) to download. Defaults to the ChEBI data.
    :param bool cache: If true, the data is downloaded to the file system, else it is loaded from the internet
    :param bool force_download: If true, overwrites a previously cached file
    :rtype: pandas.DataFrame
    """
    if url is None and cache:
        url = download_bkms(force_download=force_download)

    return pd.read_csv(
        url or BKMS_DATA_URL,
        sep='\t',
        names=header,
        skiprows=3,
        compression='gzip'
    )
