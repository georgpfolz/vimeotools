# -*- coding: utf-8 -*-
"""
=============================
Vimeo Tools Vimeo Base Module
=============================

This module contains the base classes VimeoChild and VimeoItem, as well as
functions used by the other classes.
"""

from typing import TYPE_CHECKING, Dict, Optional, List, Union, Any, Literal
import json
from vimeo_constants import (
    GETTER_STR,
    SETTER_STR,
    PROPERTIES_BASE,
    RETURNING_MAP,
    WHAT_MAP
)
if TYPE_CHECKING:
    from vimeo_folder import VimeoFolder
    from vimeo_connection import VimeoConnection
    from vimeo_data import VimeoData

def transform_returning(
    returning: str
) -> str:
    returning = returning.lower()

    try:
        return RETURNING_MAP[returning]
    except KeyError:
        raise ValueError(f'Unknown value for returning: {returning}')

def transform_what(
    what: str
) -> str:
    what = what.lower()

    try:
        return WHAT_MAP[what]
    except KeyError:
        raise ValueError(f'Unknown value for what: {what}')

def nested_value(
    data: Dict[str, Any],
    path: Union[List[str], str]
) -> Any:
    """
    Get a nested value from a dictionary using a list of keys as the path.
    """
    if isinstance(path, str):
        path = path.split('.')
    value = data
    if isinstance(value, (str, int, float)):
        return value
    
    for key in path:
        value = value[key]
    return value

def denest_key(
    key: str,
    value: Optional[Any] = None,
    data: Optional[Dict[str, Any]] = {}
) -> Dict[str, Any]:
    if value:
        if '.' not in key:
            return {key: value}
        else:
            keys = key.split('.')
            return {keys[0]: denest_key('.'.join(keys[1:]), value)}
    elif data:
        keys = key.split('.')  # could be only one key
        for key in keys:
            data = data[key] # type: ignore (data is not None here)
        
        return data
    else:
        return {}

def update_nested_data(
    data: Dict[str, Any],
    update_data: Dict[str, Any]
):
    """
    Update nested data in a dictionary using another dictionary with the same structure.
    """
    for key, value in update_data.items():
        if isinstance(value, dict):
            # Recursively update nested data
            data[key] = update_nested_data(data.get(key, {}), value)
        else:
            data[key] = value
    return data

def get_lines(
    key: str,
    value: Union[List[Any], Dict[str, Any]],
    bullet='*',
    indent: int = 0
):
    """
    Print a str, list or dict in a pretty way.
    :param key: str = '' # key name
    :param indent: int = 0 # number of spaces to indent
    :param bullet: str = '*' # bullet character
    :return: None
    """
    if isinstance(value, list):
        lines = [' ' * indent + f'{bullet} {key}:']
        for item in value:
            lines.extend(
                get_lines(
                    key='',
                    value=item,
                    bullet=bullet,
                    indent=indent + 2
                )
            )
        return lines
    elif isinstance(value, dict):
        lines = [' ' * indent + f'{bullet} {key}:']
        for k, v in value.items():
            lines.extend(
                get_lines(
                    key=k,
                    value=v,
                    bullet=bullet,
                    indent=indent + 2
                )
            )
        return lines
    else:
        return [' ' * indent + f'{bullet} {key}: {value}']


class VimeoChild:
    """
    A class to represent a Vimeo Child. This is a base class of the
    VimeoVideo and VimeoFolder classes.
    """
    def __init__(self):
        self._parent = None  # the object
    
    def get_parent_folder(
        self,
        refresh: bool = False
    ) -> 'VimeoFolder':
        """
        Get the parent folder of this item.
        :param refresh: bool
        :return: VimeoFolder
        """
        if not refresh and self._parent:
            return self._parent

        parent_uri = self.get_data(refresh=refresh)['parent']['uri'] # type: ignore
        
        parent_folder = VimeoFolder(
            code_or_uri=parent_uri,
            client=self.client # type: ignore
        )
        self._parent = parent_folder
        return parent_folder

    def get_parent_folder_data(
        self,
        keys: Optional[List[str]] = None,
        refresh: bool = False
    ) -> Dict[str, Any]:
        if not refresh and self._parent:
            return self._parent.get_data(refresh=False)
        
        folder_data = self.get_data(refresh=refresh).get('parent_folder', {}) # type: ignore

        if not keys:
            return folder_data
        else:
            return {k: folder_data[k] for k in keys if k in folder_data}
    
    def get_parent_folder_uri(
        self,
        refresh: bool = False
    ) -> str:
        return self.get_parent_folder_data(refresh=refresh).get('uri', '')
    
    def get_parent_folder_code(
        self,
        refresh: bool = False
    ) -> str:
        return self.get_parent_folder_uri(refresh=refresh).split('/')[-1]
    
    def get_parent_folder_name(
        self,
        refresh: bool = False
    ) -> str:
        return self.get_parent_folder_data(refresh=refresh).get('name', '')
    
    def get_parent_folder_link(
        self,
        refresh: bool = False
    ) -> str:
        return self.get_parent_folder_data(refresh=refresh).get('link', '')
    
    def get_parent_folder_privacy(
        self,
        refresh: bool = False
    ) -> str:
        return self.get_parent_folder_data(refresh=refresh).get('privacy', {})
    
    def get_parent_folder_privacy_view(
        self,
        refresh: bool = False
    ) -> str:
        return self.get_parent_folder_data(refresh=refresh).get('privacy', {}).get('view', '')
    
    def get_parent_folder_user_data(
        self,
        refresh: bool = False
    ) -> Dict[str, Any]:
        return self.get_parent_folder_data(refresh=refresh).get('user', {})
    
    def get_parent_folder_user(
        self,
        refresh: bool = False
    ) -> str:
        return self.get_parent_folder_user_data(refresh=refresh).get('name', '')
    
    def get_parent_folder_user_uri(
        self,
        refresh: bool = False
    ) -> str:
        return self.get_parent_folder_user_data(refresh=refresh).get('uri', '')


class VimeoBaseItem:
    """
    An abstract class to represent a Vimeo Item. This is the base of the
    VimeoFolder, VimeoVideo and VimeoShowcase classes.

    One key method is get_data(), which not only returns the item's data
    but also stores it in the object for future use. If the refresh parameter
    is not set to True, the data will not be fetched again from the API in
    subsequent calls to get_data().
    """
    BASE_URI = '/me'
    
    @property
    def uri(self) -> str:
        return self._uri
    
    @property
    def code(self) -> str:
        return self._code
    
    @property
    def temp_data(self) -> Dict[str, Any]:
        return self._temp_data
    
    @temp_data.setter
    def temp_data(self, value: Dict[str, Any]) -> None:
        self._temp_data = value

    for key, val in PROPERTIES_BASE.items():
        exec(GETTER_STR.format(prop=key))
        if val['type'] == 'str' and val.get('setable'):
            key = val.get('set_key', key)
            exec(SETTER_STR.format(prop=key))

    def __init__(
        self,
        connection: 'VimeoConnection',
        code_or_uri: Optional[str] = None,
        live: bool = False,  # live mode
        data: Optional[Dict[str, Any]] = None,
        data_object: Optional['VimeoData'] = None
    ):
        self.connection = connection
        self.client = connection.client
        self._live = live
        self._temp_data = {}  # temporary data storage for the object
        data_object = data_object

        if data_object and not data:
            data = data_object._data

        if data:
            self._data = data
        else:
            self._data = None  # initialize data as hidden attribute: method get_data() has to be used

        if code_or_uri:
            if '/' in code_or_uri:  # assume it's a uri
                self._uri = code_or_uri
                self._code = code_or_uri.split('/')[-1]
            else:  # assume it's a code
                self._code = code_or_uri
                self._uri = f'{self.BASE_URI}/{code_or_uri}'
    
    def _keys_is_allowed_to_set(
        self,
        key: str
    ) -> bool:
        key = key.split(' ')[0]  # some keys can include a number after the key name
        allowed_keys = [key.split(' ')[0] for key in self.allowed_keys_to_set] # type: ignore (in child class)

        if key in allowed_keys:
            return True
        
        return False

    def set_property(
        self,
        key: str,
        value: Any
    ):
        """
        Set a property of the item. The property must be setable.

        :param key: The key can be provided in dotted notation, e.g. "privacy.view"
        :param value: The value to set
        """
        if not self._keys_is_allowed_to_set(key=key):
            raise ValueError(
                f'Invalid key "{key}". Allowed keys are: {self.allowed_keys_to_set}' # type: ignore (in child class)
            )
        
        uri = self.uri  # from the child class
        update_data = denest_key(key, value)
        
        # client also comes from the child class
        response = self.client.patch(
            uri,
            data=update_data
        )
        
        if response.status_code == 200:
            self._data = response.json()
        elif response.status_code == 403:
            raise Exception("You don't have permission to update this item.")
        elif response.status_code == 400:
            raise Exception("A parameter is invalid.")
        else:
            raise Exception("Something went wrong.")

    def get_data(
        self,
        refresh: bool = False
    ) -> Dict:
        refresh = refresh or self._live

        if self._data and not refresh:
            return self._data
        
        data = self.client.get(
            self._uri
        ).json()
        self._data = data  # store to avoid unnecessary requests
        return data
    
    def get_property(
        self,
        property: str,
        refresh: bool = False
    ) -> Any:
        refresh = refresh or self._live

        if not refresh:
            value = denest_key(
                key=property,
                data=self._data
            )
            if value:
                return value
            
        original_property = property
        if 'code' in property:
            property = property.replace('code', 'uri')            
        
        response = self.client.get(
            f'{self.uri}/?fields={property}'  # dot notation allowed!
        )
        if response.status_code != 200:
            raise Exception(f'Error getting {self}: {response.text}')
            
        data = response.json()  # only the requested property is returned

        if isinstance(data, dict):        
            update_nested_data(
                data=self._data, # type: ignore
                update_data=data
            )
            property_value = nested_value(
                data=data,
                path=property
            )
        else:
            raise Exception(f'Error getting property {original_property}: data is not a dict')

        if original_property != property:  # code
            property_value = property_value.split('/')[-1]
        
        return property_value

    def get_user(self) -> str:
        return self.get_user_name()

    def get_user_data(
        self
    ) -> Dict[str, Any]:
        return self.get_property(
            property='user'
        )
    
    def get_user_link(self) -> str:
        return self.get_user_data()['link']
    
    @property
    def user_uri(self) -> str:
        return self.get_user_data()['uri']
    
    @property
    def user_id(self) -> str:
        return self.user_uri.split('/')[-1]

    @property
    def user_name(self) -> str:
        return self.get_user_data()['name']

    def get_user_uri(self) -> str:
        return self.get_user_data()['uri']

    def get_user_name(
        self
    ) -> str:
        return self.get_user_data()['name']
    
    def refresh(self):
        data = self.client.get(
            self._uri
        ).json()
        self._data = data  # store to avoid unnecessary requests
    
    @property
    def live(self) -> bool:
        return self._live
    
    @live.setter
    def live(self, value: bool):
        if value:
            self._live = True
        else:
            self._live = False

    @property
    def name(self):
        return self.get_property('name')

    @name.setter
    def name(self, value: str):
        self.set_property('name', value)

    @property
    def description(self):
        return self.get_property('description')
    
    @description.setter
    def description(self, value: str):
        self.set_property('description', value)

    def store_json(
        self,
        path: Optional[str] = None,
        refresh: bool = False
    ):
        """
        Store data as a json file.
        :param path: str
        :return: None
        """
        refresh = refresh or self._live

        if not path: 
            path = f'{self.__class__.__name__.lower()}.json'

        data = self.get_data(refresh=refresh)
        
        with open(path, 'w') as f:
            json.dump(
                obj=data,
                fp=f,
                indent=4
            )
        
        self._data = data


class VimeoItem(VimeoBaseItem):  # videos and showcases
    """
    An abstract class to represent a Vimeo Item. This is the base of the
    Video and Showcase classes.
    """

    def __init__(
        self,
        connection: 'VimeoConnection',
        code_or_uri: str,
        data: Optional[Dict[str, Any]] = None,
        data_object: Optional['VimeoData'] = None
    ):
        """
        Initialize the VimeoItem object.

        :param code_or_uri: str
        :param client: vimeo.VimeoClient, or a Vimeo instance's 
                       (from this module) client attribute
        """
        super().__init__(
            connection=connection,
            code_or_uri=code_or_uri,
            data=data,
            data_object=data_object
        )

    def get_description(
        self,
        refresh: bool = False
    ) -> str:
        return self.get_property('description', refresh=refresh)
