from __future__ import unicode_literals

import logging

from gmusicapi import Mobileclient, Webclient, CallFailure

logger = logging.getLogger(__name__)


class GMusicSession(object):

    def __init__(self):
        super(GMusicSession, self).__init__()
        logger.info('Mopidy uses Google Music')
        self.api = Mobileclient()

    def login(self, username, password, deviceid):
        if self.api.is_authenticated():
            self.api.logout()
        try:
            self.api.login(username, password)
        except CallFailure as error:
            logger.error(u'Failed to login as "%s": %s', username, error)
        if self.api.is_authenticated():
            if deviceid is None:
                self.deviceid = self.get_deviceid(username, password)
            else:
                self.deviceid = deviceid
        else:
            return False

    def logout(self):
        if self.api.is_authenticated():
            return self.api.logout()
        else:
            return True

    def get_all_songs(self):
        if self.api.is_authenticated():
            return self.api.get_all_songs()
        else:
            return {}

    def get_stream_url(self, song_id):
        if self.api.is_authenticated():
            try:
                return self.api.get_stream_url(song_id, self.deviceid)
            except CallFailure as error:
                logger.error(u'Failed to lookup "%s": %s', song_id, error)

    def get_all_user_playlist_contents(self):
        if self.api.is_authenticated():
            return self.api.get_all_user_playlist_contents()
        else:
            return {}

    def get_shared_playlist_contents(self, shareToken):
        if self.api.is_authenticated():
            return self.api.get_shared_playlist_contents(shareToken)
        else:
            return {}

    def get_all_playlists(self):
        if self.api.is_authenticated():
            return self.api.get_all_playlists()
        else:
            return {}

    def get_deviceid(self, username, password):
        logger.warning(u'No mobile device ID configured. '
                       u'Trying to detect one.')
        webapi = Webclient(validate=False)
        webapi.login(username, password)
        devices = webapi.get_registered_devices()
        deviceid = None
        for device in devices:
            if device['type'] == 'PHONE' and device['id'][0:2] == u'0x':
                # Omit the '0x' prefix
                deviceid = device['id'][2:]
                break
        webapi.logout()
        if deviceid is None:
            logger.error(u'No valid mobile device ID found. '
                         u'Playing songs will not work.')
        else:
            logger.info(u'Using mobile device ID %s', deviceid)
        return deviceid

    def get_track_info(self, store_track_id):
        if self.api.is_authenticated():
            try:
                return self.api.get_track_info(store_track_id)
            except CallFailure as error:
                logger.error(u'Failed to get All Access track info: %s', error)

    def get_album_info(self, albumid, include_tracks=True):
        if self.api.is_authenticated():
            try:
                return self.api.get_album_info(albumid, include_tracks)
            except CallFailure as error:
                logger.error(u'Failed to get All Access album info: %s', error)
