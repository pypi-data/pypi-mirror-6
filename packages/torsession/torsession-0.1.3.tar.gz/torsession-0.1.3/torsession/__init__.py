#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: lime
# @Date:   2013-10-27 09:08:34
# @Last Modified by:   lime
# @Last Modified time: 2013-11-25 11:23:14


'''An asynchronous session backend with mongodb for tornado'''

import pickle
import base64
import motor

from uuid import uuid1
from tornado import gen
from datetime import datetime, timedelta
from tornado.web import HTTPError

VERSION = (0, 1, 3)

def get_version():
    if isinstance(VERSION[-1], basestring):
        return '.'.join(map(str, VERSION[:-1])) + VERSION[-1]
    
    return '.'.join(map(str, VERSION))

__version__ = get_version()


class Session(object):

    LIFE_LENGTH = timedelta(days=3)
    REGENERATION_INTERVAL = timedelta(minutes=3)

    def __init__(self, collection):
        self.session_collection = collection
        self.life_length = Session.LIFE_LENGTH
        self.regeneration_interval = Session.REGENERATION_INTERVAL

    @gen.coroutine
    def get(self, key):
        '''Get a value'''

        assert self.session_id

        value = None
        session = yield self.session_collection.find_one(
            {'session_id': self.session_id})
        if session and key in session:
            value = pickle.loads(str(session[key]))
        raise gen.Return(value)

    @gen.coroutine
    def set(self, key, value):
        '''Set a value'''

        assert self.session_id

        result = yield self.session_collection.update(
            {'session_id': self.session_id},
            {'$set': {key: pickle.dumps(value)}})
        raise gen.Return(result)

    @gen.coroutine
    def delete(self, key):
        '''Delete a key'''

        assert self.session_id

        result = yield self.session_collection.update(
            {'session_id': self.session_id},
            {'$unset': {key: ''}})
        raise gen.Return(result)

    def generate_session_id(self):
        '''Generate a session id'''

        return base64.b64encode(str(uuid1()))

    @gen.coroutine
    def new_session(self):
        '''New session on server'''

        now = datetime.now()
        document = {}
        document['session_id'] = self.session_id
        document['expired_time'] = pickle.dumps(now + self.life_length)
        document['next_regeneration_time'] = pickle.dumps(
            now + self.regeneration_interval)
        result = yield self.session_collection.insert(document)
        raise gen.Return(result)

    @gen.coroutine
    def delete_session(self):
        '''Clear session when logout'''

        assert self.session_id

        result = yield self.session_collection.remove(
            {'session_id': self.session_id})
        self.session_id = None

        raise gen.Return(result)

    @gen.coroutine
    def refresh_session(self):
        '''Refresh session every other `regeneration_interval`'''

        assert self.session_id
        
        refresh_session_id = None
        # 如果到了更新session_id的时间
        next_regeneration_time = yield self.get('next_regeneration_time')

        now = datetime.now()
        if now  > next_regeneration_time:
            refresh_session_id = self.generate_session_id()
            result = yield self.session_collection.update(
                {'session_id': self.session_id},
                {'$set': {'session_id': refresh_session_id}})
            self.session_id = refresh_session_id

            # 重新设置下一次更新session_id的时间
            yield self.set('next_regeneration_time', now + self.regeneration_interval)

        raise gen.Return(refresh_session_id)

    @property
    def session_id(self):
        '''Get session id'''

        if not hasattr(self, '_session_id') or self._session_id is None:
            self._session_id = self.generate_session_id()
        return self._session_id

    @session_id.setter
    def session_id(self, value):
        '''Set session id'''

        self._session_id = value

    def set_life_length(self, value):
        '''Set `life_length`, default is `Session.LIFE_LENGTH`'''

        assert isinstance(value, timedelta)
        self.life_length = value

    def set_regeneration_interval(self, value):
        '''Set `regeneration_interval`, default is `Session.REGENERATION_INTERVAL`'''

        assert isinstance(value, timedelta)
        self.regeneration_interval = value

