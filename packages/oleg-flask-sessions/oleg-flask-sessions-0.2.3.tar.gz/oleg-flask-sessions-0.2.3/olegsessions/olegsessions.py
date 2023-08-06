from flask.sessions import SessionInterface, SessionMixin
from werkzeug.datastructures import CallbackDict
import requests

from datetime import datetime
from olegdb import OlegDB, DEFAULT_HOST, DEFAULT_PORT
from uuid import uuid4
import msgpack, time


class OlegDBSession(CallbackDict, SessionMixin):
    def __init__(self, initial=None, sid=None):
        super(OlegDBSession, self).__init__(initial)
        self.sid = sid
        self.modified = False

class OlegDBSessionInterface(SessionInterface):
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        self.host = host
        self.port = port

    def _build_key(self, app_name, sid):
        return "{}{}".format(app_name, sid)

    def open_session(self, app, request):
        db = OlegDB(self.host, self.port)
        sid = request.cookies.get(app.session_cookie_name)
        if sid:
            host_str = self._build_key(app.name, sid)
            stored_session = db.get(host_str)

            if stored_session:
                return OlegDBSession(initial=stored_session['data'], sid=stored_session['sid'])
        sid = unicode(uuid4())
        return OlegDBSession(sid=sid)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        if not session:
            response.delete_cookie(app.session_cookie_name, domain=domain)
            return

        expiration = self.get_expiration_time(app, session)
        if not expiration:
            expiration = (60 * 60 * 24) # 24 hours
        else:
            expiration = int(app.config["PERMANENT_SESSION_LIFETIME"].total_seconds())

        data = { "sid": session.sid
               , "data": session
               }

        connect_str = self._build_key(app.name, session.sid)
        db = OlegDB(self.host, self.port)
        db.set(connect_str, data, timeout=expiration)

        response.set_cookie(app.session_cookie_name, session.sid,
            expires=self.get_expiration_time(app, session),
            httponly=True, domain=domain)
