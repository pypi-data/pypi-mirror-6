from kirrupt_tv.models import UserShow, Episode, Show
import datetime
import email
import pytz


class ResponseParser:

    def __init__(self, client):
        self.client = client

    def _object_from_json(self, classname, obj, fields=[], date_fields=[],
                          date_string_fields=[]):
        o = classname()

        for f in date_fields:
            value = None

            if f in obj:
                value = obj[f]

            setattr(o, f, self._parse_date(value))

        for f in date_string_fields:
            value = None

            if f in obj:
                value = obj[f]

            setattr(o, '%s_string' % (f), value)

        for f in fields:
            value = None

            if f in obj:
                value = obj[f]

            setattr(o, f, value)

        return o

    def _parse_date(self, x):
        try:
            date = datetime.datetime.fromtimestamp(
                email.utils.mktime_tz(email.utils.parsedate_tz(x)), pytz.utc)
        except:
            return None

        return date

    def watched_episodes_changes_for_user(
            self, since=None, watched_episodes=None):
        try:
            response = self.client.watched_episodes_changes_for_user(
                since=since, watched_episodes=watched_episodes)
        except:
            return None

        class WatchedEpisodesChangesForUser:

            def __init__(self):
                self.date_string = None
                self.since_string = None

                self.date = None
                self.since = None
                self.user_shows = []

        we = WatchedEpisodesChangesForUser()

        try:
            we = self._object_from_json(
                WatchedEpisodesChangesForUser,
                response,
                date_fields=['date', 'since'],
                date_string_fields=['date', 'since'])

            for obj in response['user_shows']:
                us = UserShow()

                us.ignored = obj['ignored']
                us.modified = obj['modified']
                us.show_id = obj['show_id']

                we.user_shows.append(us)
        except:
            return None

        return we

    def episodes_changes_for_user(
            self, since=None):
        try:
            response = self.client.episodes_changes_for_user(
                since=since)
        except:
            return None

        class EpisodesChangesForUser:

            def __init__(self):
                self.date_string = None
                self.since_string = None
                self.sync_date_string = None

                self.date = None
                self.since = None
                self.sync_date = None
                self.episodes = []
                self.shows = []

        we = EpisodesChangesForUser()

        try:
            if 'date' in response:
                we.date = self._parse_date(response['date'])
                we.date_string = response['date']

            if 'since' in response:
                we.since = self._parse_date(response['since'])
                we.since_string = response['since']

            if 'sync_date' in response:
                we.sync_date = self._parse_date(response['sync_date'])
                we.sync_date_string = response['sync_date']

            if 'episodes' in response:
                for obj in response['episodes']:
                    date_fields = ['added', 'airdate']

                    fields = ['episode', 'id', 'screencap', 'season',
                              'show_id', 'summary', 'title', 'tvrage_url']

                    we.episodes.append(
                        self._object_from_json(Episode, obj,
                                               fields=fields,
                                               date_fields=date_fields))

            if 'shows' in response:
                for obj in response['shows']:
                    date_fields = ['ended', 'started']

                    fields = ['airday', 'airtime', 'fixed_background',
                              'fixed_banner', 'fixed_thumb', 'id', 'name',
                              'origin_country', 'picture_url', 'runtime',
                              'status', 'summary', 'thumbnail_url',
                              'timezone', 'tvrage_id', 'tvrage_url', 'url',
                              'year']

                    we.shows.append(
                        self._object_from_json(Show, obj,
                                               fields=fields,
                                               date_fields=date_fields))

        except:
            return None

        return we
