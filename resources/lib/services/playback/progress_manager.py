# -*- coding: utf-8 -*-
"""
    Copyright (C) 2017 Sebastian Golasch (plugin.video.netflix)
    Copyright (C) 2019 Stefano Gottardo - @CastagnaIT (original implementation module)
    Manages events to send to the netflix service for the progress of the played video

    SPDX-License-Identifier: MIT
    See LICENSES/MIT.md for more information.
"""
from __future__ import absolute_import, division, unicode_literals

import resources.lib.common as common

from .action_manager import PlaybackActionManager
from resources.lib.services.msl.events_handler import (EVENT_START, EVENT_STOP, EVENT_KEEP_ALIVE)


class ProgressManager(PlaybackActionManager):
    """Detect the progress of the played video and send the data to the netflix service"""

    def __init__(self):  # pylint: disable=super-on-old-class
        super(ProgressManager, self).__init__()
        self.current_videoid = None
        self.tick_elapsed = 0
        self.last_tick_count = 0
        self.last_player_state = {}
        self.is_video_started = False
        self.is_delay_start_performed = False
        self.event_data = {}

    def _initialize(self, data):
        videoid = common.VideoId.from_dict(data['videoid'])
        if videoid.mediatype not in [common.VideoId.MOVIE, common.VideoId.EPISODE]:
            self.enabled = False
            return
        self.current_videoid = videoid \
            if videoid.mediatype == common.VideoId.MOVIE \
            else videoid.derive_parent(0)
        self.event_data = data['event_data']

    def _on_playback_started(self, player_state):
        # Todo: safe clear queue events
        self.tick_elapsed = 0
        self.start_event_requested = False
        self.is_delay_start_performed = False
        self.is_video_started = True

    def _on_tick(self, player_state):
        if not self.is_video_started:
            return
        if not self.start_event_requested and self.tick_elapsed == 2:
            # Before request 'start' event we have to wait a possible values changed
            # by stream_continuity, so is needed to wait at least 2 seconds
            self._send_event(EVENT_START, player_state)
            self.start_event_requested = True
        elif not self.is_delay_start_performed and self.tick_elapsed == 7:
            # Wait at least 5 second before send other event request after 'start' event
            self.is_delay_start_performed = True
        elif self.is_delay_start_performed and (self.tick_elapsed - self.last_tick_count) >= 2:
            # Send event requests to Netflix service every n seconds (min 1 sec)
            if (self.tick_elapsed - self.last_tick_count) >= 2:
                # Todo: identify a possible fast forward / rewind
                self._send_event(EVENT_KEEP_ALIVE, player_state)
                self.last_tick_count = self.tick_elapsed
        self.last_player_state = player_state
        self.tick_elapsed += 1  # One tick is one second

    def _on_playback_stopped(self):
        self._send_event(EVENT_STOP, self.last_player_state)

    def _send_event(self, event_type, player_state):
        """Send an event request"""
        # Todo: send event
        pass
