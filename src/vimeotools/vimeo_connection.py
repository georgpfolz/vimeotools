# -*- coding: utf-8 -*-
"""
===========
Vimeo Tools
===========
"""

from typing import TYPE_CHECKING, Dict, Optional, List, Any, Union, Literal
import vimeo
import json
    

class VimeoConnection:

    def __init__(
        self,
        config_file: Optional[str] = 'vimeo_config.json',
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
