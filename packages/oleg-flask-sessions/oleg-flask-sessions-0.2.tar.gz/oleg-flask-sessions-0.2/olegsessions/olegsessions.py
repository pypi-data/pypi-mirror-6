from flask.sessions import SessionInterface, SessionMixin
from werkzeug.datastructures import CallbackDict
import requests

from datetime import datetime
from uuid import uuid4
import msgpack, time


DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8080

class OlegDBSession(CallbackDict, SessionMixin):
    def __init__(self, initial=None, sid=None):
        super(OlegDBSession, self).__init__(initial)
        self.sid = sid
        self.modified = False

class OlegDBSessionInterface(SessionInterface):
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        self.host = host
        self.port = port

    def _build_host_str(self, app_name, sid):
        key = "{}{}".format(app_name, sid)
        connect_str = "http://{host}:{port}/{key}".format(
                host=self.host, port=self.port, key=key)
        return connect_str

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if sid:
            host_str = self._build_host_str(app.name, sid)
            stored_session = requests.get(host_str, stream=True)

            if stored_session.status_code == 200:
                stored_data = msgpack.unpackb(stored_session.raw.read(), encoding='utf-8')
                expiration = stored_data['expiration']
                if int(time.time()) < expiration:
                    return OlegDBSession(initial=stored_data['data'],
                        sid=stored_data['sid'])
                return OlegDBSession(sid=sid)
        sid = unicode(uuid4())
        return OlegDBSession(sid=sid)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        if not session:
            response.delete_cookie(app.session_cookie_name, domain=domain)
            return

        expiration = self.get_expiration_time(app, session)
        if not expiration:
            expiration = int(time.time()) + (60 * 60 * 24) # 24 hours
        else:
            expiration = int(time.time()) + int(app.config["PERMANENT_SESSION_LIFETIME"].total_seconds())

        data = { "sid": session.sid
               , "data": session
               , "expiration": expiration
               }

        connect_str = self._build_host_str(app.name, session.sid)
        packed = msgpack.packb(data, use_bin_type=True)
        resp = requests.post(connect_str, data=packed)

        response.set_cookie(app.session_cookie_name, session.sid,
            expires=self.get_expiration_time(app, session),
            httponly=True, domain=domain)
