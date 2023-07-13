# -*- coding: utf-8 -*-
"""
=========================
Vimeo Tools Folder Module
=========================

This module contains the class VimeoFolder, which represents a Vimeo folder
(projects).
"""
from typing import TYPE_CHECKING, List, Dict, Optional, Any, Union, Literal
from vimeo_connection import VimeoConnection
from vimeo_base import VimeoChild, VimeoItem, get_lines
from vimeo_video import VimeoVideo
from vimeo_constants import (
    PROPERTIES_BASE,
    PROPERTIES_FOLDER
)

if TYPE_CHECKING:
    from vimeo_data import VimeoData

class VimeoFolder(VimeoItem, VimeoChild):

    BASE_URI = '/me/projects'
    allowed_keys_to_set = ['name']

    def __init__(
        self,
        connection: VimeoConnection,
        code_or_uri: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        data_object: Optional['VimeoData'] = None,
        privacy: Literal['anybody', 'nobody', 'password', 'users'] = 'nobody',
        users: List[str] = [],
        parent_folder: Optional[Union[str, 'VimeoFolder']] = None,
        password: Optional[str] = None,
        sort: Literal['arrange', 'date', 'manual', 'name', 'plays', 'likes', 'comments', 'duration'] = 'date',
        layout: Literal['grid', 'player'] = 'grid',
        theme: Literal['dark', 'standard'] = 'standard'
    ):
        self.connection = connection
        self.client = connection.client

        self._data = None  # type: Optional[Dict[str, Any]]
        self._parent  = None  # type: Optional[VimeoFolder]
        self._videos = None  # type: Optional[List[VimeoVideo]]
        self._videos_data = None  # type: Optional[List[Dict[str, Any]]]

        
        if name and code_or_uri:
            raise ValueError(
                'Parameters: Either code_or_uri or name must be provided.'
            )

        if not name and data:
            name = data.get('name')

        if name:
            self._code = self._create(
                name=name,
                description=description,
                privacy=privacy,
                users=users,
                parent_folder=parent_folder,
                password=password,
                sort=sort,
                layout=layout,
                theme=theme
            )
        else:
            raise ValueError(
                'Parameters: Either code_or_uri or name must be provided.'
            )

        # init the parent class
        super(VimeoItem, self).__init__(
            code_or_uri=code_or_uri or self._code,
            connection=connection,
            data=data,
            data_object=data_object
        )

        super(VimeoChild, self).__init__() # type: ignore

    def __str__(self) -> str:
        ignore_keys = ['user', 'metadata', 'pictures']
        
        lines = [
            f'Object: {VimeoFolder.__repr__(self)}',
        ] + get_lines(key='code', value=self.code, bullet='-', indent=2)

        data = self.get_data()
        
        for prop, meta in {**PROPERTIES_BASE, **PROPERTIES_FOLDER}.items():
            value = data.get(prop)

            if prop in ignore_keys:
                continue

            lines += get_lines(
                key=prop,
                value=value,
                bullet='-',
                indent=2
            )
        
        lines.append(f'  - more keys: ' + ', '.join(ignore_keys))
        return '\n'.join(lines)
    
    def _create(
        self,
        name: str,
        description: Optional[str] = None,
        privacy: Literal['anybody', 'nobody', 'password', 'users'] = 'nobody',
        users: List[str] = [],
        parent_folder: Optional[Union[str, 'VimeoFolder']] = None,
        password: Optional[str] = None,
        sort: Literal['arrange', 'date', 'manual', 'name', 'plays', 'likes', 'comments', 'duration'] = 'date',
        layout: Literal['grid', 'player'] = 'grid',
        theme: Literal['dark', 'standard'] = 'standard'
    ) -> str: # type: ignore (Exceptions)
        """
        Create a new folder.

        :param name: The name of the folder.
        :param description: The description of the folder.
        :param privacy: The privacy level of the folder.
        :param users: The list of users that can access the folder.
        :param parent_folder: The parent folder.
        :param password: The password of the folder.
        :param sort: The sort order of the folder.
        :param layout: The layout of the folder.
        :param theme: The theme of the folder.
        :return: The new folder.
        """
        parent_folder_uri = None

        if parent_folder:
            if isinstance(parent_folder, VimeoFolder):
                parent_folder_uri = parent_folder.uri
            else:
                if '/' in parent_folder:  # uri
                    parent_folder_uri = parent_folder
                else:  # code
                    parent_folder_uri = f'{self.BASE_URI}/{parent_folder}'

        response = self.client.post(
            parent_folder_uri or self.BASE_URI,
            data={
                k:v for k,v in {
                    'name': name,
                    'description': description,
                    'privacy': privacy,
                    'password': password,
                    'sort': sort,
                    'layout': layout,
                    'theme': theme,
                    'users': users
                }.items()
                if v is not None
            }
        )
        if response.status_code == 201:
            self._data = response.json()
            self._data['code'] = self._data['uri'].split('/')[-1]
            return self._data['code']

        elif response.status_code == 400:
            raise Exception(f'Error creating folder: {response.text}')
        elif response.status_code == 401:
            raise Exception('The user credentials are invalid.')
        elif response.status_code == 403:
            raise Exception('The authenticated user does not have permission to create a folder.')
    
    def add_video(
        self,
        video: Union[str, 'VimeoVideo']
    ):
        """
        Add a video to the folder.
        :param video: Union[str, VimeoVideo]
        :return: None
        """
        raise NotImplementedError
    
    def add_videos(
        self,
        videos: List[Union[str, 'VimeoVideo']]
    ):
        """
        Add videos to the folder.
        :param videos: List[Union[str, VimeoVideo]]
        :return: None
        """
        raise NotImplementedError
    
    def get_videos(
        self,
        refresh: bool = False,
        returning: Literal['data', 'objects'] = 'objects'
    ) -> Union[List['VimeoVideo'], List[Dict[str, Any]]]:
        """
        Get the videos in the folder.
        :return: List[VimeoVideo]
        """
        if self._videos is None or refresh:
            self._videos = [
                VimeoVideo(
                    code_or_uri=video['uri'],
                    client=self.client
                )
                for video in self.get_videos_data(refresh=refresh)
            ]
        return self._videos
    
    def get_folders(
        self,
        refresh: bool = False,
        returning: Literal['data', 'objects'] = 'objects'
    ) -> Union[List['VimeoFolder'], List[Dict[str, Any]]]:
        """
        Get the folders in the folder.
        :return: List[VimeoFolder]
        """
        raise NotImplementedError
    
    def get_name(
        self,
        refresh: bool = False
    ) -> str:
        """
        Get the folder name.
        :return: str
        """
        return self.get_title(refresh=refresh)
    
    def get_items(
        self,
        refresh: bool = False,
        returning: Literal['data', 'objects'] = 'objects'
    ) -> Union[List[Union['VimeoVideo', 'VimeoFolder']], List[Dict[str, Any]]]:
        """
        Get the items in the folder.
        :return: List[Union[VimeoVideo, VimeoFolder]]
        """
        videos = self.get_videos(refresh=refresh)
        folders = self.get_folders(refresh=refresh)
        return videos + folders
    
    @property
    def nb_videos(
        self
    ) -> int:
        """
        Get the number of videos in the folder.
        :return: int
        """
        return self._data['metadata']['connections']['videos']['total']  # type: ignore

    def remove_video(
        self,
        video: Union[str, 'VimeoVideo']
    ):
        """
        Remove a video from the folder.
        :param video: Union[str, VimeoVideo]
        :return: None

        Note that this method does not delete the video from Vimeo.
        """
        raise NotImplementedError
    
    def remove_videos(
        self,
        videos: List[Union[str, VimeoVideo]]
    ):
        """
        Remove videos from the folder.
        :param videos: List[Union[str, VimeoVideo]]
        :return: None

        Note that this method does not delete the videos from Vimeo.
        """
        raise NotImplementedError
    