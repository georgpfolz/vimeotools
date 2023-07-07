# -*- coding: utf-8 -*-
"""
=============================================================
VimeoChild, VimeoItem, VimeoVideo, VimeoShowcase, VimeoFolder
=============================================================

This module contains the classes VimeoVideo, VimeoShowcase, VimeoFolder,
as well as their bases classes VimeoChild and VimeoItem.

All instances must be initialized with a VimeoConnection object
"""

from typing import TYPE_CHECKING, Dict, Optional, List, Union, Any, Literal

from vimeo_base import (
    VimeoChild,
    VimeoItem,
    get_lines
)
from vimeo_constants import (
    GETTER_STR,
    SETTER_STR,
    PROPERTIES_BASE,
    PROPERTIES_VIDEO,
    VIDEO_ALLOWED_KEYS_TO_SET
)

if TYPE_CHECKING:
    from vimeo_connection import VimeoConnection
    from vimeo_showcase import VimeoShowcase
    from vimeo_folder import VimeoFolder

class VimeoVideo(VimeoItem, VimeoChild):
    """
    A class to represent a Vimeo video.
    """
    BASE_URI = '/videos'
    allowed_keys_to_set = VIDEO_ALLOWED_KEYS_TO_SET

    for key, val in PROPERTIES_VIDEO.items():
        exec(GETTER_STR.format(prop=key))
        if val['type'] == 'str' and val.get('setable'):
            set_key = val.get('set_key')
            if set_key is None:
                continue  # needs a special setter
            key = set_key
            exec(SETTER_STR.format(prop=set_key))
    
    @property
    def tags(self) -> List[str]:
        return [tag['name'] for tag in self.get_property('tags')]
    
    @property
    def tags_data(self) -> List[Dict[str, Any]]:
        return self.get_data()['tags']

    def __init__(
        self,
        connection: 'VimeoConnection',
        code_or_uri: str
    ):
        # init the parent class
        super(VimeoItem, self).__init__(
            connection=connection,
            code_or_uri=code_or_uri
        )

        super(VimeoChild, self).__init__() # type: ignore

        self._parent = None        
        self._showcases = None
        self._parent_folder = None
    
    def __str__(self) -> str:
        ignore_keys = [
            'user',
            'metadata',
            'pictures',
            'embed',
            'files',
            'play',
            'download',
            'uploader',
            'parent_folder'
        ]
        
        lines = [f'Object: {VimeoVideo.__repr__(self)}']
        
        for prop, meta in {**PROPERTIES_BASE, **PROPERTIES_VIDEO}.items():
            try:
                value = getattr(self, prop)
            except KeyError:
                continue

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
    
    def add_domain(
        self,
        domain: str
    ):
        """
        Add a domain to the whitelist of the video.
        :param domain: str
        :return: None
        """
        raise NotImplementedError

    def add_to_folder(
        self,
        folder: Union[str, 'VimeoFolder']
    ):
        """
        Add the video to a folder.
        :param folder: str
        :return: None
        """
        raise NotImplementedError
    
    def delete(self):
        response = self.client.delete(self.uri)
        if response.status_code == 204:  # success
            del self
        elif response.status_code == 403:
            raise Exception((
                '403: Forbidden, you are not allowed to delete this video.'
                'You may not have the permission or the video is not owned by you.'
            ))
        else:
            raise Exception(f'Error: {response.status_code}')

    def get_chapter(
        self,
        chapter_id: str,
        refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Get the video chapter.
        :param chapter_id: str
        :param refresh: bool
        :return: Dict[str, Any]
        """
        refresh = refresh or self._live
        raise NotImplementedError
    
    @property
    def chapters(
        self,
        refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get the video chapters.
        :param refresh: bool
        :return: List[Dict[str, Any]]
        """
        refresh = refresh or self._live
        raise NotImplementedError
    
    @property
    def content_ratings(
        self,
        refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get the video content ratings.
        :param refresh: bool
        :return: List[Dict[str, Any]]
        """
        refresh = refresh or self._live
        raise NotImplementedError

    @property
    def dimensions(
        self
    ) -> Dict[str, int]:
        """
        Get the video dimensions.
        :return: Dict[str, int]
        """
        return {
            'width': self.get_property('width'),
            'height': self.get_property('height')
        }

    @property
    def hash(
        self
    ) -> int:
        """
        Get the video hash.
        :return: str
        """
        return self.__hash__()
    
    @property
    def privacy(
        self,
        refresh: bool = False,
        key: Optional[str] = None
    ) -> Dict[str, Union[str, bool]]:
        """
        Get the video privacy settings.
        :return: Dict[str, Union[str, bool]]
        """
        refresh = refresh or self._live
        privacy = self.get_data(refresh=refresh)['privacy']
        if key:
            if not key in ['view, embed, download, add, comments']:
                raise ValueError(f'Invalid privacy key: {key}')
            return privacy[key]
        else:
            return privacy

    def get_showcases(
        self,
        returning: Literal['obj', 'list', 'dict', 'names', 'codes', 'uris'] = 'obj',
        refresh: bool = False
    ) -> Union[List[str], Dict[str, Any], List['VimeoShowcase']]:
        """
        Get the showcases the video is in.
        :param returning: str
        :param refresh: bool
        :return: Union[List[str], Dict[str, Any]]
        """
        if self._showcases is None or refresh:
            response = self.client.get(f'/videos/{self.code}/albums')
            assert response.status_code == 200
            videos_d = response.json()
            self._showcases = videos_d
        else:
            videos_d = self._showcases

        if returning == 'obj':
            return [
                VimeoShowcase(
                    showcase['uri'].split('/')[-1],
                    self.client
                )
                for showcase
                in videos_d['data']
            ]
        elif returning == 'dict':
            return videos_d
        elif returning == 'list':
            return videos_d['data']
        elif returning == 'names':
            return [video['name'] for video in videos_d['data']]
        elif returning == 'codes':
            return [video['uri'].split('/')[-1] for video in videos_d['data']]
        elif returning == 'uris':
            return [video['uri'] for video in videos_d['data']]
        else:
            raise ValueError(f'Invalid returning value: {returning}')
    
    @property
    def status(
        self
    ) -> str:
        """
        Get the video status.
        :return: str
        """
        return self.get_property(property='transcode.status')

    def remove_domain(
        self,
        domain: str
    ):
        """
        Remove a domain from the video's whitelist.
        :param domain: str
        :return: None
        """
        raise NotImplementedError
    
    def remove_from_folder(
        self,
        folder: str
    ):
        """
        Remove the video from a folder.
        :param folder: str
        :return: None
        """
        raise NotImplementedError
    
    def upload(self):
        raise NotImplementedError
    
    def upload_picture(self):
        pass

