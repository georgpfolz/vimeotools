# -*- coding: utf-8 -*-
"""
=====================
Vimeo Tools VimeoData
=====================

This module contains the class VimeoData, which is used to display
information about a Vimeo account and its videos, folders and albums.
"""
from typing import TYPE_CHECKING, Dict, Optional, List, Union, Any, Literal
from pathlib import Path
import json
import pickle
from vimeo_constants import (
    MIN_KEYS
)
from vimeo_base import (
    get_lines,
    nested_value,
    transform_returning,
    transform_what
)
from vimeo_connection import VimeoConnection
from vimeo_video import VimeoVideo
from vimeo_folder import VimeoFolder
from vimeo_showcase import VimeoShowcase

class VimeoData:

    def __init__(
        self,
        connection: VimeoConnection,
        data_file: Optional[str] = None
    ):
        """
        Class for displaying information about a Vimeo account:
        - Account data
        - Videos
        - Folders
        - Showcases (Albums)
        """
        self.connection = connection
        self.client = connection.client
        self.uri = connection.uri

        if data_file:
            self.load(
                file=data_file
            )
        else:
            # initialize
            self._account_data = None
            self._videos_data = None
            self._folders_data = None
            self._albums_data = None
        
        self._videos = None
        self._folders = None
        self._albums = None
    
    def _print(
            self,
            data: Dict[str, Any],
            ignore_keys: List[str] = [],
            indent: int = 0,
            returning: Literal['str', 'lines'] = 'str'
    ) -> Union[str, List[str]]:
        lines = [
            '\n'.join(
                get_lines(
                    key=key,
                    value=data[key],
                    bullet='-',
                    indent=indent
                )
            )
            for key
            in data.keys()
            if key not in ignore_keys
        ]
        # lines.append(' ' * indent + f'- more keys: ' + ', '.join(ignore_keys))

        if returning == 'lines':
            return lines
        else:
            return '\n'.join(lines)

    def _data_stored(
        self,
        what: Literal['videos', 'albums', 'projects']
    ) -> Optional[Dict[str, Any]]:
        if what == 'videos' and self._videos_data:
            return self._videos_data
        elif what == 'albums' and self._albums_data:
            return self._albums_data
        elif what == 'projects' and self._folders_data:
            return self._folders_data

    def _get_account_data(
        self,
        returning: Literal['dict', 'json'] = 'dict',
        keys: Optional[List[str]] = None,
        refresh: bool = False
    ) -> Union[dict, str]:
        """
        Get account infos.
        :return: dict
        """
        if not refresh and self._account_data:
            data = self._account_data
        else:
            uri = self.uri
            response = self.client.get(uri)
            assert response.status_code == 200, f'Error: {response.status_code}'
            data = response.json()
            data['code'] = data.get('uri').split('/')[-1]  # add vimeo code to data
            self._account_data = data

        if returning == 'json':
            return json.dumps(data, indent=4)
        else:  # returning == 'dict'
            if keys:
                return {
                    key: data[key]
                    for key
                    in keys
                }
            else:
                return data      

    def _items_stored(
        self,
        what: Literal['videos', 'albums', 'projects']
    ) -> Optional[
            Union[
                List[VimeoVideo],
                List[VimeoShowcase],
                List[VimeoFolder]
            ]
         ]:
        if what == 'videos' and self._videos:
            return self._videos
        elif what == 'albums' and self._albums:
            return self._albums
        elif what == 'projects' and self._folders:
            return self._folders

    def _get_items(
        self,
        what: Literal['videos', 'albums', 'projects'],
        returning: Literal[
            'object',
            'objects',
            'dict',
            'list',
            'json',
            'code',
            'codes',
            'uri',
            'uris',
            'None',
            None
        ] = None,
        refresh: bool = False
    ) -> Union[
            Dict[str, Any],
            List[Dict[str, Any]], List[VimeoVideo], List[VimeoShowcase],
            str,
            None  # ValueError
        ]:
        """
        Fetch videos from Vimeo.
        :param what: What to fetch. Either 'videos' or 'albums' (=='showcases').
        :param localpath: If it exists, fetches data from local file.
        :param returning:
        - If 'dict', returns the video data as a dict, as provided by Vimeo.
        - If 'list', returns a list of dicts (one dict per video, as in the 'data' key of the Vimeo response)
        - If 'json', returns a json string.
        """
        # set returning to singular
        returning = transform_returning(returning=returning)  # type: ignore

        data = {'data': []}

        data_stored = self._data_stored(what=what)
        items_stored = self._items_stored(what=what)
        
        if not refresh:
            if returning == 'dict' and data_stored:
                return data_stored
            elif returning == 'object' and items_stored:

                return items_stored

        if not refresh:
            if what == 'videos' and self._videos_data:
                data['data'] = self._videos_data.get('data', [])
            elif what == 'albums' and self._albums_data:
                data['data'] = self._albums_data.get('data', [])
            elif what == 'projects' and self._folders_data:
                data['data'] = self._folders_data.get('data', [])
        
        if not data.get('data'):
            # no refresh or first time
            items_list = []
            page = 1
            while True:
                response = self.client.get(
                    f'/me/{what}',
                    params={
                        'page': page,
                        'per_page': 100
                    }
                )
                if response.status_code != 200:
                    raise Exception(f'Error getting {what}: {response.text}')
                
                # we don't care if data is overwritten!
                # this way we end with the last page number
                # and the items_list is added thereafter anyway
                data = response.json()

                for item in data['data']:
                    item['code'] = item.get('uri').split('/')[-1]  # add vimeo code to data

                items_list.extend(data['data'])
                if data['paging']['next'] is None:
                    break
                page += 1

            data['data'] = items_list

        # at this point, data must be a dict
        if what == 'videos':
            self._videos_data = data
        elif what == 'albums':
            self._albums_data = data
        elif what == 'projects':
            self._folders_data = data

        if returning == 'dict':
            return data
        elif returning == 'object':
            if what == 'videos':
                videos = [
                    VimeoVideo(
                        code_or_uri=video['uri'],
                        connection=self.connection,
                        data_object=self,
                        data=video
                    )
                    for video
                    in data['data']
                ]
                self._videos = videos
                return videos
            elif what == 'albums':
                albums = [
                    VimeoShowcase(
                        code_or_uri=album['uri'],
                        connection=self.connection,
                        data_object=self,
                        data=album
                    )
                    for album
                    in data['data']
                ]
                self._albums = albums
                return albums
            elif what == 'projects':
                folders = [
                    VimeoFolder(
                        code_or_uri=folder['uri'],
                        connection=self.connection,
                        data_object=self,
                        data=folder
                    )
                    for folder
                    in data['data']
                ]
                self._folders = folders
                return folders
        elif returning in ('code', 'uri'):
            return [item[returning] for item in data['data']]
        elif returning == 'list':
            return data['data']
        elif returning == 'json':
            return json.dumps(data, indent=4)
        else:
            # will never happen, we keep it for the return type check
            raise ValueError(f'Unknown returning value: {returning}')

    def _show_data(
        self,
        what: Literal[
            'videos',
            'video',
            'album',
            'albums',
            'showcase',
            'showcases',
            'folder',
            'folders',
            'project',
            'projects',
            'account'
        ],
        mode: str = 'default',
        ignore_keys: List[str] = [],
        show_keys: List[str] = [],
        indent: int = 0,
        refresh: bool = False,
        returning: Literal['str', 'lines'] = 'str'
    ) -> Union[str, List[str]]:
        what = transform_what(what) # type: ignore

        data = {}

        if what == 'account':
            data = self._get_account_data(
                returning='dict',
                refresh=refresh
            )
        elif what in ('videos', 'albums'):
            data = self._get_items(
                what=what,  # type: ignore (-> transform_what)
                returning='dict',
                refresh=refresh
            )
        elif what == 'projects':
            data = self.get_folders(
                returning='dict',
                refresh=refresh
            )
        else:
            raise ValueError(f'Unknown value for what: {what}')
        
        if show_keys:
            ignore_keys = [
                key
                for key
                in data.keys() # type: ignore (impossible that it's not a dict)
                if key not in show_keys
            ]
        elif not ignore_keys:  # use mode only if no ignore_keys and no show_keys
            if mode == 'default':
                ignore_keys = ['pictures', 'metadata']
            elif mode == 'minimal':
                ignore_keys += MIN_KEYS[what]
            elif mode == 'max':
                ignore_keys = []
        
        return self._print(
            data=data, # type: ignore (impossible that it's not a dict)
            ignore_keys=ignore_keys,
            indent=indent,
            returning=returning
        )
    
    @property
    def account(
        self
    ) -> dict:
        """
        Get account infos.
        :return: dict
        """
        return self.account_data

    @property
    def account_data(
        self
    ) -> dict:
        """
        Get account infos.
        :return: dict
        """
        return self._get_account_data(
            returning='dict'
        ) # type: ignore
    
    @property
    def account_json(
        self
    ) -> str:
        """
        Get account infos.
        :return: str (json)
        """
        return self._get_account_data(
            returning='json'
        ) # type: ignore

    def get_count(
        self,
        what: Literal['videos', 'albums', 'projects'],
        refresh: bool = False
    ) -> int:
        """
        Get the number of items (videos or albums).
        :param what: What to fetch. Either 'videos' or 'albums' (=='showcases').
        """
        if not refresh:
            if what == 'videos' and self._videos_data:
                return self._videos_data['total']  # why is that an error? It should be a dict.
            elif what == 'albums' and self._albums_data:
                return self._albums_data['total']
            elif what == 'projects' and self._folders_data:
                return self._folders_data['total']

        response = self.client.get(
            f'/me/{what}',
            params={
                'page': 1,
                'per_page': 1
            }
        )
        if response.status_code != 200:
            raise Exception(f'Error getting {what}: {response.text}')

        return response.json()['total']

    def get_folders(
        self,
        returning: Literal[
            'objects',  # alias for 'object'
            'object',
            'folder',  # alias for 'object'
            'folders',  # alias for 'objects'
            'dict',
            'list',
            'code',
            'codes',
            'uri',
            'uris',
            'json'
        ] = 'objects',
        refresh: bool = False
    ) -> Union[
            Dict[str, Any],
            List[Dict[str, Any]],
            List[VimeoFolder], str
        ]:
        """
        Get all folders.
        :return: list of VimeoFolder objects
        """
        returning = transform_returning(returning) # type: ignore

        return self._get_items(
            what='projects',
            returning=returning, # type: ignore
            refresh=refresh
        ) # type: ignore
        
    def get_showcases(
        self,
        returning: Literal[
            'objects',
            'object',
            'showcase',  # alias for 'object'
            'showcases',  # alias for 'objects'
            'album',  # alias for 'object'
            'albums',  # alias for 'objects'
            'dict',
            'list',
            'code',
            'codes',
            'uri',
            'uris',
            'json'
        ] = 'objects',
        refresh: bool = False
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], List[VimeoShowcase], str]:
        """
        Fetch albums from Vimeo.
        returns a list of VimeoShowcase objects by default

        :param returning: str, default: 'item'
                          - 'object', 'objects, 'album' or 'albums': returns a list of VimeoVideo objects
                          - 'dict': returns a dict as provided by the Vimeo API
                          - 'list': returns a list of dict as provided by the Vimeo API in the 'data' key
                          - 'json': returns a json string
        
        Obviously, returning the list of VimeoShowcase objects takes more time than returning the list of dicts.
        """
        returning = transform_returning(returning) # type: ignore

        return self._get_items(
            what='albums',
            returning=returning,  # type: ignore
            refresh=refresh
        ) # type: ignore

    def get_videos(
        self,
        returning: Literal[
            'object',
            'objects',
            'video',
            'videos',
            'code',
            'codes',
            'uri',
            'uris',
            'dict',
            'list',
            'json'
        ] = 'objects',
        refresh: bool = False
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], List[VimeoVideo], str]:
        """
        Fetch videos from Vimeo.
        returns a list of VimeoVideo objects by default

        :param returning: str, default: 'item'
                          - 'item', 'items, 'video' or 'videos': returns a list of VimeoVideo objects
                          - 'dict': returns a dict as provided by the Vimeo API
                          - 'list': returns a list of dict as provided by the Vimeo API in the 'data' key
                          - 'json': returns a json string
        
        Obviously, returning the list of VimeoVideo objects takes more time than returning the list of dicts.
        """
        returning = transform_returning(returning) # type: ignore

        return self._get_items(
            what='videos',
            returning=returning,  # type: ignore
            refresh=refresh
        ) # type: ignore

    def get_videos_from_showcase(
        self,
        showcase: Union[str, VimeoShowcase],
        returning: Literal[
            'object',
            'objects',
            'dict',
            'list',
            'json',
            'code',
            'codes',
            'uri',
            'uris'
        ] = 'objects'
    ) -> Union[List[Dict[str, Any]], List[str], List[VimeoVideo], str]:
        """
        Fetch the videos from an album.

        This method should be obsolete,
        as it is now possible to get the videos from an album directly from the VimeoShowcase object.

        :param album_code: str
        :param returning: str, default: 'dict'
        :return: list of dict

        Example:
        vimeo_client.get_videos_from_album(album='123456', returning='list')
        """
        returning = transform_returning(returning) # type: ignore

        try:
            return showcase.get_videos(  # type: ignore
                returning=returning
            )
        except AttributeError:
            """
            Maybe it would be better to get rid of this code altogether
            and create a showcase object instead.
            """
            response = self.client.get(f'/albums/{showcase}/videos')
            assert response.status_code == 200, f'Error: {response.status_code}'
            album_data = response.json()

            for video in album_data['data']:
                video['code'] = video['uri'].split('/')[-1]

            if returning == 'object':
                return [
                    VimeoVideo(
                        code_or_uri=video['uri'],
                        connection=self
                    )
                    for video
                    in album_data['data']
                ]
            elif returning == 'dict':
                return album_data
            if 'code' in returning:
                return [
                    video['code']
                    for video
                    in album_data['data']
                ]
            elif returning == 'uri':
                return [
                    video['uri']
                    for video
                    in album_data['data']
                ]
            elif returning == 'list':
                return album_data['data']
            elif returning == 'json':
                return json.dumps(album_data)
            else:
                raise ValueError(
                    f'Invalid value for returning: {returning}'
                )
            
    def get_videos_with_tag(
        self,
        tag: str,
        returning: Literal[
            'object',
            'objects',
            'dict',
            'list',
            'json',
            'code',
            'codes',
            'uri',
            'uris'
        ] = 'objects',
        refresh: bool = False
    ) -> Union[VimeoVideo, List[Dict[str, Any]], List[str], str]:
        returning = transform_returning(returning) # type: ignore
        
        if not refresh and self._videos_data is not None:
            video = [
                video
                for video
                in self._videos_data['data']
                if tag in video['tags']['tag']
            ][0]
            video_uri = video['uri']
        else:
            response = self.client.get(f'/tags/{tag}/videos')
            assert response.status_code == 200, f'Error: {response.status_code}'
            video = response.json()
            video_uri = video['data'][0]['uri']
        
        if returning =='object':
            return VimeoVideo(
                code_or_uri=video_uri,
                client=self.client
            )
        elif returning == 'dict':
            return video
        elif returning == 'list':
            return video['data']
        elif returning == 'code':
            return [
                video['uri'].split('/')[-1]
                for video
                in video['data']
            ]
        elif returning =='uri':
            return [
                video['uri']
                for video
                in video['data']
            ]
        elif returning == 'json':
            return json.dumps(video, indent=4)
        else:
            raise ValueError(f'Unknown returning value: {returning}')
        
    def info(
        self
    ) -> str:
        """
        Return a string with information about the account and
        informations about the videos, folders and albums.

        Be warned that this method will make a lot of requests to the
        Vimeo API, so it may take a while to complete.

        :return: str
        """
        lines = [
            f'Object: {VimeoConnection.__repr__(self)}',
            f'  - Account:'
        ]
        lines += self.show_account(
            mode='minimal',
            indent=4,
            returning='lines'
        )
        lines += self.show_videos(
            mode='minimal',
            indent=4,
            returning='lines'
        )
        lines += self.show_folders(
            mode='minimal',
            indent=4,
            returning='lines'
        )
        lines += self.show_showcases(
            mode='minimal',
            indent=4,
            returning='lines'
        )

        lines.append(f'  - {self.get_count(what="videos")} Videos')
        lines.append(f'  - {self.get_count(what="projects")} Folders')
        lines.append(f'  - {self.get_count(what="albums")} Showcases')

        return '\n'.join(lines)  
    
    def items_property(
        self,
        property: str,
        what: Literal['videos', 'albums', 'projects'] = 'videos',
        refresh: bool = False
    ) -> List[str]:
        """
        Fetch the property of the items specified in 'what'.

        :param property: This parameter supports the same dot notation as the Vimeo API.
        :param refresh: bool
        :return: list of str
        """
        stored_data = self._data_stored(what=what)
        stored_items = self._items_stored(what=what)

        if not refresh and stored_data is not None:
            data_base = stored_data['data']
            
            if '.' in property:
                for key in property.split('.'):
                    data_base = data_base[key]

            return [
                item[property]
                for item
                in data_base
            ]
        elif not refresh and stored_items is not None:
            return [
                item.items_property(property)  # refresh implicitely False
                for item
                in stored_items
            ]
        else:
            original_property = property
            if property == 'code':
                property = 'uri'
                original_property = 'code'
            
            uri = f'{self.uri}/{what}?fields={property}'  # dot notation allowed!
            property_list = []
            page = 1
            while True:
                response = self.client.get(
                    uri,
                    params={
                        'page': page,
                        'per_page': 100
                    }
                )
                if response.status_code != 200:
                    raise Exception(f'Error getting {what}: {response.text}')      
                
                data = response.json()
                
                property_list.extend([
                    nested_value(data=item, path=property) for item in data['data']
                ])

                if data['paging']['next'] is None:
                    break
                
                page += 1

            if original_property:
                property_list = [
                    item.split('/')[-1]
                    for item
                    in property_list
                ]
            return property_list

    def load(
        self,
        file: Union[Path, str] = Path('vimeo_data.json'),
        format: Optional[Literal['json', 'pickle']] = None,
        refresh: bool = False
    ) -> None:
        if isinstance(file, str):
            file = Path(file)

        if not file.exists():
            raise FileNotFoundError(f'File not found: {file}')
        
        if not format:
            format = file.suffix[1:]  # type: ignore

        if format == 'json':
            with open(file, 'r') as f:
                data = json.load(f)
        elif format == 'pickle':
            with open(file, 'rb') as f:
                data = pickle.load(f)
        else:
            raise ValueError(f'Unknown format: {format}')
        
        if not data:
            raise ValueError(f'No data in {file}')

        self._data = data

        # redundant!
        self._account_data = data['account']
        self._videos_data = data['videos']
        self._folders_data = data['projects']
        self._albums_data = data['albums']
        
    @property
    def nb_folders(
        self
    ) -> int:
        """
        Get the number of folders.
        """
        return self.get_count(
            what = 'projects'
        ) # type: ignore

    @property
    def nb_showcases(
        self
    ) -> int:
        """
        Get the number of showcases.
        :return: int
        """
        return self.get_count(
            what='albums'
        )

    @property
    def nb_videos(
        self
    ) -> int:
        """
        Get the number of videos.
        :param refresh: bool
        :return: int
        """
        return self.get_count(
            what='videos'
        )
    
    def refresh(
        self,
        what: Literal[
            'videos',
            'albums',
            'showcases',
            'account',
            'all'
        ] = 'all'
    ) -> None:
        """
        Refresh data.
        """
        what = transform_what(what) # type: ignore

        if what in ('account', 'all'):
            self._get_account_data(
                refresh=True
            )
        if what in ('albums', 'all'):
            self._get_items(
                what='albums',
                refresh=True
            )
        if what in ('videos', 'all'):
            self._get_items(
                what='videos',
                refresh=True
            )

    @property
    def showcases(
        self
    ) -> List[VimeoShowcase]:
        """
        Get all showcases.
        :return: list of VimeoShowcase objects

        This property is always refreshed.
        """
        return self.get_showcases(
            returning='objects'
        ) # type: ignore
    
    @property
    def showcase_codes(
        self,
        refresh: bool = False
    ) -> List[str]:
        """
        Fetch the codes of all videos.
        :param refresh: bool
        :return: list of str
        """
        if not refresh and self._albums_data is not None:  # fastest way
            return [
                album['code']
                for album
                in self._albums_data['data']
            ]
        elif not refresh and self._albums is not None:
            return [
                album.get_code()  # refresh implicitely False
                for album
                in self._albums
            ]
        else:
            return [
                uri.split('/')[-1]
                for uri
                in self.showcase_uris
            ]

    @property
    def showcase_uris(
        self,
        refresh: bool = False
    ) -> List[str]:
        """
        Fetch the uris of all videos.
        :param refresh: bool
        :return: list of str
        """
        if not refresh and self._albums_data is not None:
            return [
                album['uri']
                for album
                in self._albums_data['data']
            ]
        elif not refresh and self._albums is not None:
            return [
                album.get_uri()  # refresh implicitely False
                for album
                in self._albums
            ]
        else:
            return self.items_property(
                property='uri',
                what='albums',
                refresh=refresh
            )

    @property
    def video_codes(
        self,
        refresh: bool = False
    ) -> List[str]:
        """
        Fetch the codes of all videos.
        :param refresh: bool
        :return: list of str
        """
        if not refresh and self._videos_data is not None:  # fastest way
            return [
                video['code']
                for video
                in self._videos_data['data']
            ]
        elif not refresh and self._videos is not None:
            return [
                video.get_code()  # refresh implicitely False
                for video
                in self._videos
            ]
        else:
            return [
                uri.split('/')[-1]
                for uri
                in self.video_uris
            ]
    
    @property
    def video_uris(
        self,
        refresh: bool = False
    ) -> List[str]:
        """
        Fetch the uris of all videos.
        :param refresh: bool
        :return: list of str
        """
        if not refresh and self._videos_data is not None:
            return [
                video['uri']
                for video
                in self._videos_data['data']
            ]
        elif not refresh and self._videos is not None:
            return [
                video.get_uri()  # refresh implicitely False
                for video
                in self._videos
            ]
        else:
            return self.items_property(
                property='uri',
                what='videos',
                refresh=refresh
            )
        
    @property
    def videos(
        self
    ) -> List[VimeoVideo]:
        """
        Get all videos.
        :return: list of VimeoVideo objects

        Refresh is implicitely False.
        """
        return self.get_videos(
            returning='objects'
        ) # type: ignore

    def save(
        self,
        file: Union[Path, str] = Path('vimeo_data.json'),
        format: Optional[Literal['json', 'pickle']] = None,
        refresh: bool = False
    ) -> None:
        if isinstance(file, str):
            file = Path(file)
        
        if not format:
            format = file.suffix[1:]  # type: ignore (impossible that it's not a Path)

        data_to_save = {
            'account': self._get_account_data(
                returning='dict',
                refresh=refresh
            ),
            'videos': self._get_items(
                what='videos',
                returning='dict',
                refresh=refresh
            ),
            'albums': self._get_items(
                what='albums',
                returning='dict',
                refresh=refresh
            ),
            'projects': self.get_folders(
                returning='dict',
                refresh=refresh
            )
        }

        print(f'Saving data to {file}...')
        
        if format == 'json':
            with open(file, 'w') as f:
                json.dump(data_to_save, f, indent=4)
        elif format == 'pickle':
            with open(file, 'wb') as f:
                pickle.dump(data_to_save, f)
        else:
            raise ValueError(f'Unknown format: {format}')

    def show_account(
        self,
        mode: str = 'default',
        ignore_keys: List[str] = [],
        show_keys: List[str] = [],
        indent: int = 0,
        refresh: bool = False,
        returning: Literal['str', 'lines'] = 'str'
    ) -> Union[str, List[str]]:
        return self._show_data(
            what='account',
            mode=mode,
            ignore_keys=ignore_keys,
            show_keys=show_keys,
            indent=indent,
            refresh=refresh,
            returning=returning
        )

    def show_videos(
        self,
        mode: str = 'default',
        ignore_keys: List[str] = [],
        show_keys: List[str] = [],
        indent: int = 0,
        refresh: bool = False,
        returning: Literal['str', 'lines'] = 'str'
    ) -> Union[str, List[str]]:
        return self._show_data(
            what='videos',
            mode=mode,
            ignore_keys=ignore_keys,
            show_keys=show_keys,
            indent=indent,
            refresh=refresh,
            returning=returning
        )

    def show_showcases(
        self,
        mode: str = 'default',
        ignore_keys: List[str] = [],
        show_keys: List[str] = [],
        indent: int = 0,
        refresh: bool = False,
        returning: Literal['str', 'lines'] = 'str'
    ) -> Union[str, List[str]]:
        return self._show_data(
            what='albums',
            mode=mode,
            ignore_keys=ignore_keys,
            show_keys=show_keys,
            indent=indent,
            refresh=refresh,
            returning=returning
        )

    def show_folders(
        self,
        mode: str = 'default',
        ignore_keys: List[str] = [],
        show_keys: List[str] = [],
        indent: int = 0,
        refresh: bool = False,
        returning: Literal['str', 'lines'] = 'str'
    ) -> Union[str, List[str]]:
        return self._show_data(
            what='projects',
            mode=mode,
            ignore_keys=ignore_keys,
            show_keys=show_keys,
            indent=indent,
            refresh=refresh,
            returning=returning
        )

    def update_data(
        self,
        what: Literal['account', 'videos', 'albums', 'projects'],
        data: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> None:
        """
        Update data in the VimeoData object
        """
        map_what = {
            'account': self._account_data,
            'videos': self._videos_data,
            'albums': self._albums_data,
            'projects': self._folders_data
        }

        if isinstance(data, list):
            """
            find the item(s) in the list by uri or code and update them
            or append them if they don't exist
            """
            pass
        elif isinstance(data, dict):
            map_what[what] = data
