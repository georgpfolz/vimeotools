# -*- coding: utf-8 -*-
"""
===========================
Vimeo Tools Showcase Module
===========================

This module contains the class VimeoShowcase.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Optional, List, Union, Any, Literal
import vimeo
import json
from vimeo_base import (
    VimeoItem,
    get_lines,
    transform_returning
)
from vimeo_constants import (
    GETTER_STR,
    SETTER_STR,
    PROPERTIES_BASE,
    PROPERTIES_SHOWCASE,
    SHOWCASE_ALLOWED_KEYS_TO_SET
)
from vimeo_video import VimeoVideo as VimeoVideo_

if TYPE_CHECKING:
    from vimeo_connection import VimeoConnection
    from vimeo_data import VimeoData
    from vimeo_video import VimeoVideo

class VimeoShowcase(VimeoItem):
    """
    A class to represent a Vimeo showcase.
    """
    BASE_URI = '/albums'
    API_URI = '/me/albums'
    USER_URI = '/users/{user_id}/albums'
    allowed_keys_to_set = SHOWCASE_ALLOWED_KEYS_TO_SET

    for key, val in PROPERTIES_SHOWCASE.items():
        exec(GETTER_STR.format(prop=key))
        if val['type'] == 'str' and val.get('setable'):
            set_key = val.get('set_key')
            if set_key is None:
                continue  # needs a special setter
            key = set_key
            exec(SETTER_STR.format(prop=set_key))

    def __init__(
        self,
        connection: VimeoConnection,
        code_or_uri: Optional[str] = None,
        name: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        data_object: Optional[VimeoData] = None,
        videos: List['VimeoVideo'] = [],
        creation_data: Optional[Dict[str, Any]] = {},  # for creation, must at least contain 'name'
    ):
        """
        Initialize a Vimeo showcase.
        :param client: Union[vimeo.VimeoClient, Dict[str, str]]
        :param code_or_uri: Optional[str]
        :param creation_data: Optional[Dict[str, Any]]
        """

        # init the parent class
        super().__init__(
            code_or_uri=code_or_uri,
            connection=connection,
            data=data,
            data_object=data_object
        )
        self._videos = videos

        if data:  # data provided, no request needed
            self._data = data
            return

        if name:
            creation_data['name'] = name  # type: ignore
        
        if not code_or_uri and not creation_data:
            raise ValueError('Either code_or_uri or data must be provided.')
        elif code_or_uri and creation_data:
            raise ValueError('Only one of code_or_uri or data must be provided.')
        elif creation_data:
            # create a new showcase
            response = self.client.post(self.API_URI, data=creation_data)
            if response.status_code == 201:  # success in creating a new showcase
                self._data = response.json()
                self._uri = self._data['uri']
                self._code = self._data['uri'].split('/')[-1]
            elif response.status_code == 400:
                raise ValueError('Invalid data.')
            elif response.status_code == 403:
                raise PermissionError('You do not have permission to create a showcase.')
            else:
                raise ValueError(f'Status code {response.status_code}. Unknown error.')
        
        for video in videos:
            self.add_video(video)
    
    def __str__(self) -> str:
        ignore_keys = ['user', 'metadata', 'pictures']
        
        lines = [f'Object: {VimeoShowcase.__repr__(self)}']
        
        for prop, meta in {**PROPERTIES_BASE, **PROPERTIES_SHOWCASE}.items():
            value = getattr(self, prop)

            if prop in ignore_keys:
                continue

            lines += get_lines(
                key=prop,
                value=value,
                bullet='-',
                indent=2
            )
        
        videos = self.videos or []
        lines.append(f'  - {len(videos)} Videos')
        if videos:
            for video in videos:
                lines.append(f'    - {video.name} ({video.code})') # type: ignore

        lines.append(f'  - more keys: ' + ', '.join(ignore_keys))
        return '\n'.join(lines)

    def add_logo(
        self,
        picture: str
    ):
        """
        Add a logo to the showcase.
        """
        raise NotImplementedError
    
    def add_thumbnail(
        self,
        picture: str
    ):
        """
        Add a thumbnail to the showcase.
        """
        raise NotImplementedError


    def add_video(
        self,
        video: Union[str, 'VimeoVideo']  # code or object
    ):
        """
        Add a video to the showcase.
        """
        if isinstance(video, VimeoVideo_):
            video = video.code # type: ignore

        # uri_base = self.USER_URI.format(user_id=self.user_id) 
        uri = f'{self.BASE_URI}/{self.code}/videos/{video}'
        print('uri', uri)
        
        response = self.client.put(uri)
        if response.status_code == 204:
            pass
        elif response.status_code == 403:
            raise PermissionError('You do not have permission to add a video to this showcase.')
        elif response.status_code == 404:
            raise ValueError('The showcase or video does not exist.')

    
    def delete(self):
        """
        Delete the showcase on Vimeo and also delete the object.
        """
        response = self.client.delete(f'{self.API_URI}/{self.code}')
        assert response.status_code == 204
        if response.status_code == 204:
            self._data = None
            self._videos = None
            self._showcases = None
            del self  # delete the object, since it no longer exists (I know this is not recommended practice)
        elif response.status_code == 403:
            raise PermissionError('You do not have permission to delete this showcase.')
        elif response.status_code == 404:
            raise ValueError('The showcase does not exist.')
        
    def delete_logo(
        self,
        logo_id: str
    ):
        """
        Delete the logo of the showcase.
        """
        raise NotImplementedError
    
    def get_logo(
        self,
        logo_id: str
    ):
        """
        Get the logo of the showcase.
        """
        raise NotImplementedError
    
    def get_videos(
        self,
        refresh: bool = False,
        returning: Literal[
            'code',
            'codes',
            'uri',
            'uris',
            'name',
            'names',
            'dict',
            'list',
            'object',
            'objects',
            'json'
        ] = 'object'
    ) -> Union[
            Dict[str, Any],
            List[Dict[str, Any]],
            List['VimeoVideo'],
            List[str],
            str
        ]:
        """
        Get the videos of the showcase.
        """
        returning = transform_returning(returning)
        
        if not refresh and self._videos:
            return self._videos
        
        uri = f'{self.API_URI}/{self.code}/videos'
        response = self.client.get(uri)

        if response.status_code == 200:
            # get all the videos
            videos = []
            data = response.json()
            videos.extend(data['data'])
            
            while 'next' in data['paging']:
                if not data['paging']['next']:
                    break
                response = self.client.get(data['paging']['next'])
                data = response.json()
                videos.extend(data['data'])
            
            self._videos = videos

            if returning == 'dict':
                return videos
            elif returning == 'list':
                return videos['data'] # type: ignore
            elif returning == 'object':
                return [
                    VimeoVideo_(
                        connection=self.connection,
                        code_or_uri=video['uri']
                    ) for video in videos
                ]
            elif returning == 'json':
                return json.dumps(videos)
            elif returning == 'code':
                return [video['uri'].split('/')[-1] for video in videos]
            elif returning in ('uri', 'name'):
                return [video[returning[:-1]] for video in videos]
            else:
                raise ValueError(f'Invalid value {returning} for returning.')
            
        elif response.status_code == 404:
            raise ValueError('The showcase does not exist.')  # should not happen
        
        return []
    
    def delete_thumbnail(
        self,
        thumbnail_id: str
    ):
        """
        Delete the thumbnail of the showcase.
        """
        raise NotImplementedError

    def get_thumbnail(
        self,
        thumbnail_id: str
    ):
        """
        Get the thumbnail of the showcase.
        """
        raise NotImplementedError
    
    def get_thumbnails(
        self
    ):
        """
        Get the thumbnails of the showcase.
        """
        raise NotImplementedError

    @property
    def logos(
        self
    ):
        """
        Get the logos of the showcase.
        """
        raise NotImplementedError
    
    @property
    def nb_videos(
        self
    ) -> int:
        """
        Get the number of videos in the showcase.
        """
        return self._data['metadata']['connections']['videos']['total']  # type: ignore

    def remove_video(
        self,
        video: str
    ):
        """
        Remove a video from the showcase.
        """
        try:
            video = video.get_code() # type: ignore
        except AttributeError:
            pass

        uri = f'{self.API_URI}/{self.code}/videos/{video}'
        response = self.client.delete(uri)
        if response.status_code == 204:
            pass
        elif response.status_code == 403:
            raise PermissionError('You do not have permission to remove a video from this showcase.')
        elif response.status_code == 404:
            raise ValueError('The showcase or video does not exist.')

    def replace_videos(
        self,
        videos: List[Union[str, 'VimeoVideo']]  # codes, uris or objects
    ):
        """
        Replace all the videos of the showcase.
        """
        uri = f'{self.API_URI}/{self.code}/videos'

        if isinstance(videos[0], str):
            if '/' in videos[0]:  # uri
                for video in videos:
                    if '/' not in video:
                        raise ValueError('All videos must be provided as codes or uris.')
            else:  # code
                for video in videos:
                    if '/' in video:
                        raise ValueError('All videos must be provided as codes or uris.')
        else:  # VimeoVideo objects or will throw an error
            videos = [video.get_uri() for video in videos] # type: ignore

        response = self.client.put(
            uri,
            data={'videos': ','.join([video for video in videos])}
        )
        if response.status_code == 204:
            pass
        elif response.status_code == 403:
            raise PermissionError('You do not have permission to replace the videos of this showcase.')
        elif response.status_code == 404:
            raise ValueError('The showcase or video does not exist.')

    def set_logo(
        self,
        picture: str
    ):
        """
        Replace the logo of the showcase.
        """
        raise NotImplementedError

    def set_featured_video(
        self,
        video_id: str
    ):
        """
        Set the featured video of the showcase.
        """
        raise NotImplementedError

    @property
    def videos(
        self
    ) -> List['VimeoVideo']:
        """
        Get the videos of the showcase.
        """
        return self.get_videos()  # no idea why this is should be an error
    