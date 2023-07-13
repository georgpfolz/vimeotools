# -*- coding: utf-8 -*-
"""
=============================
Vimeo Tools Connection Module
=============================

This module contains the class VimeoConnection.

All instances of the other classes must be initialized with a VimeoConnection object,
which is used to connect to the Vimeo API. It contains the VimeoClient object
from the vimeo package and the base URI, which is used to build the
request URIs.
"""

from typing import TYPE_CHECKING, Dict, Optional, List, Any, Union, Literal
import vimeo
import json
from pathlib import Path
    

class VimeoConnection:

    def __init__(
        self,
        config_file: Optional[Union[str, Path]] = Path('vimeo_config.json'),
        token: Optional[str] = None,
        key: Optional[str] = None,
        secret: Optional[str] = None
    ):
        """
        Initialize the Vimeo client.

        Either token, key and secret or data_path must be provided.

        :param data_path: str, default: 'vimeo.json'
        :param token: str
        :param key: str
        :param secret: str
        """
        if token and key and secret:
            vimeo_client_data = {
                'token': token,
                'key': key,
                'secret': secret
            }
        elif config_file:
            with open(config_file, 'r') as f:
                vimeo_client_data = json.load(f)
        else:
            raise ValueError(
                'Parameters: Either token, key and secret or config_file must be provided.'
            )

        self.client = vimeo.VimeoClient(**vimeo_client_data)
        self.uri = '/me'
