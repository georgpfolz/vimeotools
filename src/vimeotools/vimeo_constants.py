# -*- coding: utf-8 -*-
"""
=====================
Vimeo Tools Constants
=====================

This module contains constants used by the Vimeo Tools package.
"""

GETTER_STR ="""
@property
def {prop}(self) -> str:
    return self.get_data()['{prop}']
"""

SETTER_STR = """
@{prop}.setter
def {prop}(self, value: str):
    self._data['{prop}'] = value
    self.set_property('{set_key}', value)
"""

# properties that are common to VimeoVideo, VimeoShowcase, VimeoFolder

PROPERTIES_BASE = {
    'name': {'type': str, 'setable': True},
    'created_time': {'type': str},
    'modified_time': {'type': str},
    'duration': {'type': int},
    'resource_key': {'type': str},
    'user': {'type': dict},
    'metadata': {'type': dict},
    'pictures': {'type': dict},
    'uri': {'type': str, 'init': True},
    'privacy': {'type': dict},
    'embed': {'type': dict},
    'link': {'type': str}
}

PROPERTIES_FOLDER = {
    'last_user_action_event_date': {'type': str},
    'pinned_on': {'type': str},
    'is_pinned': {'type': bool},
    'is_private_to_user': {'type': bool},
    'access_grant': {'type': dict}
}


PROPERTIES_VIDEO = {
    'description': {'type': str, 'setable': True},
    'content_rating': {'type': list},
    'stats': {'type': dict},
    'tags': {'type': list, 'setable': True, 'set_key': None},  # needs a special setter
    'categories': {'type': list},
    'status': {'type': str},
    'release_time': {'type': str},
    'is_playable': {'type': bool},
    'width': {'type': int},
    'upload': {'type': dict},
    'has_audio': {'type': bool},
    'files': {'type': list},
    'manage_link': {'type': str},
    'type': {'type': str},
    'content_rating_class': {'type': str},
    'last_user_action_event_date': {'type': str},
    'play': {'type': dict},
    'parent_folder': {'type': dict},
    'language': {'type': str, 'setable': True, 'set_key': 'locale'},
    'transcode': {'type': dict},
    'player_embed_url': {'type': str},
    'download': {'type': dict},
    'rating_mod_locked': {'type': bool},
    'height': {'type': int},
    'app': {'type': dict},
    'uploader': {'type': dict},
    'review_page': {'type': dict},
    'license': {'type': dict}
}

VIDEO_ALLOWED_KEYS_TO_SET = [
    'content_rating',  #            Array   A list of values describing the content in this video. For a full list of values, use the /contentratings endpoint.
    'custom_url',  #                String  The custom link of the video. This link doesn't include the base URL and the username or user ID of the video's owner.
    'description',  #   	        String	The description of the video. This field can hold a maximum of 5000 characters.
    'embed.buttons.embed',  #	    Boolean Whether to show the embed button on the embeddable player.
    'embed.buttons.fullscreen',  #	Boolean Whether to show the fullscreen button on the embeddable player.
    'embed.buttons.hd',  #       	Boolean	Whether to show the HD button on the embeddable player.
    'embed.buttons.like',  #     	Boolean	Whether to show the like button on the embeddable player.
    'embed.buttons.scaling',  #  	Boolean	Whether to show the scaling button on the embeddable player in fullscreen mode.
    'embed.buttons.share',  #    	Boolean	Whether to show the share button on the embeddable player.
    'embed.buttons.watchlater',  # 	Boolean	Whether to show the watch later button on the embeddable player.
    'embed.cards',  #            	Array	A collection of cards associated with the selected video.
    'embed.cards.display_time',  #   Number	The number of seconds for which the card appears.
    'embed.cards.headline',  #   	String	The title of the card.
    'embed.cards.id',  #         	String	The UUID of the card.
    'embed.cards.image_url',  #  	String	The URL of the thumbnail for the card.
    'embed.cards.teaser',  #     	String	The description of the card.
    'embed.cards.timecode',  #   	Number	The playback timestamp, given in seconds, when the card appears.
    'embed.cards.url',  #        	String	The URL of the card.
    'embed.color',  #            	String	The main color of the embeddable player.
    'embed.end_screen.type',  #  	String	The end screen type.
                                #       empty - The end screen is empty.
                                #       loop - The end screen loops the video playback.
                                #       share - The end screen includes sharing options.
                                #       thumbnail - The end screen includes the thumbnail of the video.
    'embed.logos.custom.active',  # Boolean	Whether to show the active custom logo on the embeddable player.
    'embed.logos.custom.id',  # 	Number	The ID of the custom logo that will show on the emeddable player.
    'embed.logos.custom.link',  #	String	The URL that loads when the user clicks the custom logo.
    'embed.logos.custom.sticky',  # Boolean	Whether the custom logo is always visible on the embeddable player (true) or whether the logo appears and disappears with the rest of the UI (false).
    'embed.logos.vimeo',  #     	Boolean	Whether to show the Vimeo logo on the embeddable player.
    'embed.playbar',  #         	Boolean	Whether to show the playbar on the embeddable player.
    'embed.title.name',  #      	String	How to handle the video title in the title bar of the embeddable player.
                                #       hide - Hide the video title.
                                #       show - Show the video title.
                                #       user - Enable the user to decide.
    'embed.title.owner',  #     	String	How to handle the owner information in the title bar of the embeddable player.
                                #       hide - Hide the owner info.
                                #       show - Show the owner info.
                                #       user - Enable the user to decide.
    'embed.title.portrait',  #  	String	How to handle the owner portrait in the title bar of the embeddable player.
                                #       hide - Hide the portrait.
                                #       show - Show the portrait.
                                #       user - Enable the user to decide.
    'embed.volume',  #      	Boolean	Whether to show the volume selector on the embeddable player.
    'embed_domains',  #     	Array	The complete list of domains the video can be embedded on. This field overwrites existing domains and requires that privacy_embed have the value whitelist.
    'embed_domains_add',  # 	Array	A list of domains intended to be added to an existing set of domains. This field requires that privacy_embed have the value whitelist.
    'embed_domains_delete',  #  Array	A list of domains intended to be removed from an existing set of domains. This field requires that privacy_embed have the value whitelist.
    'hide_from_vimeo',  #   	Boolean	Whether to hide the video from everyone except the video's owner. When the value is true, unlisted video links work only for the video's owner.
    'license',  #            	String	The Creative Commons license under which the video is offered.
                            #       by - The video is offered under CC BY, or the attibution-only license.
                            #       by-nc - The video is offered under CC BY-NC, or the Attribution-NonCommercial license.
                            #       by-nc-nd - The video is offered under CC BY-NC-ND, or the Attribution-NonCommercian-NoDerivs license.
                            #       by-nc-sa - The video is offered under CC BY-NC-SA, or the Attribution-NonCommercial-ShareAlike licence.
                            #       by-nd - The video is offered under CC BY-ND, or the Attribution-NoDerivs license.
                            #       by-sa - The video is offered under CC BY-SA, or the Attribution-ShareAlike license.
                            #       cc0 - The video is offered under CC0, or public domain, videos.
    'locale',  #         	String	The video's default language. For a full list of supported languages, use the /languages?filter=texttracks endpoint.
    'name',  #           	String	The title of the video. This field can hold a maximum of 128 characters.
    'password',  #      	String	The password. When you set privacy.view to password, you must provide the password as an additional parameter. This field can hold a maximum of 32 characters.
    'privacy.add',  #    	Boolean	Whether a user can add the video to a showcase, channel, or group.
    'privacy.comments',  #	String	The privacy level required to comment on the video.
                        #       anybody - Anyone can comment on the video.
                        #       contacts - Only the owner's contacts can comment on the video.
                        #       nobody - No one can comment on the video.
    'privacy.download',  #	Boolean	Whether a user can download the video. This field isn't available to Vimeo Free members.
    'privacy.embed',  #  	String	The video's embed setting. Specify the whitelist value to restrict embedding to a specific set of domains. For more information, see our Interacting with Videos guide.
                        #       private - The video can't be embedded.
                        #       public - The video can be embedded.
                        #       whitelist - The video can be embedded on the specified domains only.
    'privacy.view',  #   	String	The video's privacy setting. When this value is users, application/json is the only valid content type. Also, some privacy settings are unavailable to Vimeo Free members; for more information, see our Help Center.
                        #       anybody - Anyone can access the video. This privacy setting appears as Public on the Vimeo front end.
                        #       contacts - Only those who follow the owner on Vimeo can access the video. This field is deprecated.
                        #       disable - The video is embeddable, but it's hidden on Vimeo and can't be played. This privacy setting appears as Hide from Vimeo on the Vimeo front end. This field is deprecated.
                        #       nobody - No one except the owner can access the video. This privacy setting appears as Private on the Vimeo front end.
                        #       password - Only those with the password can access the video.
                        #       unlisted - Only those with the private link can access the video.
                        #       users - Only Vimeo members can access the video. This field is deprecated.
    'review_page.active',  #	 Boolean	Whether to enable video review.
    'spatial.director_timeline',  #	            Array	    An array representing the 360 director timeline.
    'spatial.director_timeline.pitch *',  #     Number	    The 360 director timeline pitch. This value must be between −90 and 90, and you must specify it only when spatial.director_timeline is defined.
    'spatial.director_timeline.roll',   #   	Number	    The 360 director timeline roll.
    'spatial.director_timeline.time_code *',  # Number      The 360 director timeline time code. This paramater is required only when spatial.director_timeline is defined.
    'spatial.director_timeline.yaw *',  #   	Number	    The 360 director timeline yaw. This value must be between 0 and 360, and you must specify it only when spatial.director_timeline is defined.
    'spatial.field_of_view',  #             	Number	The 360 field of view. This value must be between 30 and 90. The default is 50.
    'spatial.projection'  #                    	String	The 360 spatial projection.
                                            #       cubical - Use cubical projection.
                                            #       cylindrical - Use cylindrical projection.
                                            #       dome - Use dome projection.
                                            #       equirectangular - Use equirectangular projection.
                                            #       pyramid - Use pyramid projection.
    'spatial.stereo_format'  #    String	The 360 spatial stereo format.
                                #       left-right - Use left-right stereo.
                                #       mono - Use monaural audio.
                                #       top-bottom - Use top-bottom stereo.
]

PROPERTIES_SHOWCASE = {
    'description': {'type': str, 'setable': True},
    'loop': {'type': bool},
    'domain_certificate_state': {'type': str},
    'hide_upcoming': {'type': bool},
    'hide_from_vimeo': {'type': bool},
    'allow_downloads': {'type': bool},
    'brand_color': {'type': str},
    'hide_nav': {'type': bool},
    'autoplay': {'type': bool},
    'roku_provider_name': {'type': str},
    'roku_language': {'type': str},
    'custom_logo': {'type': str},
    'share_link': {'type': str},
    'review_mode': {'type': str},
    'sort': {'type': str},
    'use_custom_domain': {'type': bool},
    'has_chosen_thumbnail': {'type': bool},
    'theme': {'type': str},
    'layout': {'type': str},
    'domain': {'type': str},
    'hide_vimeo_logo': {'type': bool},
    'seo_title': {'type': str},
    'allow_share': {'type': bool},
    'seo_allow_indexed': {'type': bool},
    'roku_genres': {'type': list},
    'url': {'type': str},
    'web_custom_logo': {'type': str},
    'allow_continuous_play': {'type': bool},
    'seo_keywords': {'type': str},
    'seo_description': {'type': str},
    'web_brand_color': {'type': str},
    'embed_brand_color': {'type': str},
    'embed_custom_logo': {'type': str}
}

SHOWCASE_ALLOWED_KEYS_TO_SET = [
    'brand_color',  #	    String	The hexadecimal code for the color of the player buttons and showcase controls.
    'description',  #	    String	The description of the showcase.
    'domain',  #    	    String	The custom domain of the showcase.
    'hide_nav',  #  	    Boolean	Whether to hide Vimeo navigation when displaying the showcase.
    'hide_upcoming',  #     Boolean	Whether to include the upcoming live event in the showcase.
    'layout',  #    	    String	The type of layout for presenting the showcase.
                    #           grid - The videos appear in a grid.
                    #           player - The videos appear in the player.
                    #           name	String	The name of the showcase.
                    #           password	String	The showcase's password. This field is required only when privacy is password.
    'name',  #      	    String	The name of the showcase.
    'privacy',  #    	    String	The privacy level of the showcase.
                    #           anybody - Anyone can access the showcase, either on Vimeo or through an embed.
                    #           embed_only - The showcase doesn't appear on Vimeo, but it can be embedded on other sites.
                    #           nobody - No one can access the showcase, including the authenticated user.
                    #           password - Only people with the password can access the showcase.
                    #           team - Only members of the authenticated user's team can access the showcase.
                    #           unlisted - The showcase can't be accessed if the URL omits its unlisted hash.
    'review_mode',  #  	    Boolean	Whether showcase videos use the review mode URL.
    'sort',  #      	    String	The default sort order of the videos as they appear in the showcase.
                    #           added_first - The videos appear according to when they were added to the showcase, with the most recently added first.
                    #           added_last - The videos appear according to when they were added to the showcase, with the most recently added last.
                    #           alphabetical - The videos appear alphabetically by their title.
                    #           arranged - The videos appear as arranged by the owner of the showcase.
                    #           comments - The videos appear according to their number of comments.
                    #           likes - The videos appear according to their number of likes.
                    #           newest - The videos appear in chronological order with the newest first.
                    #           oldest - The videos appear in chronological order with the oldest first.
                    #           plays - The videos appear according to their number of plays.
    'theme',  #     	    String	The color theme of the showcase.
                    #          dark - The showcase uses the dark theme.
                    #           standard - The showcase uses the standard theme.
    'url'  #        	    String	The custom Vimeo URL of the showcase.
    'use_custom_domain'  #	Boolean	Whether the user has opted for a custom domain for their showcase.
]

# keys to ignore when showing account data in the "min" mode
ACCOUNT_MIN_IGNORE = [
    'resource_key',
    'bio',
    'skills',
    'content_filter',
    'modified_time',
    'websites',
    'languages',
    'metadata',
    'pictures',
    'preferences',
    'location_details',
    'available_for_hire',
    'can_work_remotely',
    'capabilities',
    'short_bio'
]

# keys to ignore when showing video data in the "min" mode
VIDEOS_MIN_IGNORE = [
    'resource_key',
    'bio',
    'skills',
    'content_filter',
    'modified_time',
    'websites',
    'languages',
    'metadata',
    'pictures',
    'preferences',
    'location_details',
    'available_for_hire',
    'can_work_remotely',
    'capabilities',
    'short_bio'
]

# keys to ignore when showing showcase data in the "min" mode
SHOWCASES_MIN_IGNORE = [
    'resource_key',
    'bio',
    'skills',
    'content_filter',
    'modified_time',
    'websites',
    'languages',
    'metadata',
    'pictures',
    'preferences',
    'location_details',
    'available_for_hire',
    'can_work_remotely',
    'capabilities',
    'short_bio'
]

# keys to ignore when showing folder data in the "min" mode
FOLDER_MIN_IGNORE = [
    'resource_key',
    'bio',
    'skills',
    'content_filter',
    'modified_time',
    'websites',
    'languages',
    'metadata',
    'pictures',
    'preferences',
    'location_details',
    'available_for_hire',
    'can_work_remotely',
    'capabilities',
    'short_bio'
]

MIN_KEYS = {
    'account': ACCOUNT_MIN_IGNORE,
    'videos': VIDEOS_MIN_IGNORE,
    'albums': SHOWCASES_MIN_IGNORE,
    'projects': FOLDER_MIN_IGNORE
}

WHAT_MAP = {
    'account': 'account',
    'video': 'videos',
    'videos': 'videos',
    'album': 'albums',
    'albums': 'albums',
    'showcase': 'albums',
    'showcases': 'albums',
    'project': 'projects',
    'projects': 'projects',
    'folder': 'projects',
    'folders': 'projects'
}

RETURNING_MAP = {
    'str': 'str',
    'string': 'str',
    'dict': 'dict',
    'dictionary': 'dict',
    'list': 'list',
    'object': 'object',
    'objects': 'object',
    'video': 'object',
    'videos': 'object',
    'album': 'object',
    'albums': 'object',
    'showcase': 'object',
    'showcases': 'object',
    'project': 'object',
    'projects': 'object',
    'folder': 'object',
    'folders': 'object',
    'account': 'object',
    'code': 'code',
    'codes': 'code',
    'uri': 'uri',
    'uris': 'uri',
    'json': 'json',
    'lines': 'lines'
}