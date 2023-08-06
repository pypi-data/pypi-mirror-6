#!/usr/bin/env python
"""
List Service Base

Provides simple JSON REST API on top of table-oriented storage (tstore).

API:
- GET /list/<type>?field=value... -- lookup matches
- POST /list/<type> -- add new entry
- GET /list/<type>/<id> -- get entry
- PATCH /list/<type>/<id> -- update entry
- DELETE /list/<type>/<id> -- delete entry (or should it be inactive?)
- GET /_status -- Returns service status information.

Headers:
- X-Auth-User: ID of caller

TODO: cache control

Define a service, e.g.:

    s = lsvc.Service('myservice', store, 'myservice')

or inherit from Service class.

"""

from tornadoutil import LoggingApplication, RequestHandler

ID = 'id'

class Service(LoggingApplication):
    """Our service class. Inherits from LoggingApplication so all
    requests get logged automatically.
    """
    def __init__(self, service_id, db, uri_prefix):
        """Create instance of service app.
        db should be compatible with TStore interface (tstore.py).
        """
        self.uri_prefix = uri_prefix
        self.db = db

        # Ordering matters! First match wins.
        handlers = [
            (r"/_status", StatusHandler),
            (r"/{}/(.+)/(.+)".format(uri_prefix), RecordHandler),
            (r"/{}/(.+)".format(uri_prefix), ContainerHandler)
        ]
        super(Service, self).__init__(service_id, handlers)



class BaseHandler(RequestHandler):
    """Our service's base handler. Provides helpers."""
    @property
    def db(self):
        """Return application db instance"""
        return self.application.db

    def record_url(self, cls, rid):
        """Return record URL"""
        return "{}/{}/{}/{}".format(
            self.appurl(), self.application.uri_prefix, cls, rid)

    def validate_record_type(self, cls):
        """Halt with 404 if invalid."""
        try:
            self.db.validate_record_type(cls)
        except ValueError:
            self.halt(404, 'Invalid record type "{}"'.format(cls))

    def as_record(self, cls, request):
        """Return request's body as a record of given class"""
        return self.db.as_record(cls, request.headers['content-type'],
                                 request.body)


class ContainerHandler(BaseHandler):
    """Handler for container requests: list (get) and add (post) records."""
    def get(self, cls):
        """Return matching records for given class.
        Parameters define what attributes should match."""
        self.validate_record_type(cls)
        request_args = self.request.arguments.iteritems()
        params = dict([(param, values[0]) for param, values in request_args])
        self.write(self.json(self.db.list(cls, params)))

    def post(self, cls):
        """Create new entry in given entity class. Body should have
        JSON-format record."""
        self.validate_record_type(cls)
        try:
            record = self.as_record(cls, self.request)
            self.db.create(cls, record)
            self.set_header('Location', self.record_url(cls, record[ID]))
            self.set_status(201)
        except KeyError as error:
            self.halt(403, str(error))
        except ValueError as error:
            self.halt(400, str(error))


class RecordHandler(BaseHandler):
    """Handler for record requests (get/patch/delete)"""

    def get(self, cls, rid):
        """GET request"""
        self.validate_record_type(cls)
        try:
            self.write(self.json(self.db.get(cls, rid)))
        except (ValueError, KeyError):
            self.halt(404)

    def patch(self, cls, rid):
        """PATCH request"""
        try:
            patch = self.db.deserialize(self.request.headers['content-type'],
                                        self.request.body)
            self.db.update(cls, rid, patch)
        except KeyError:
            self.halt(404)
        except ValueError as error:
            self.halt(400, str(error))
        self.set_status(204)

    def delete(self, cls, rid):
        """DELETE request"""
        try:
            self.db.delete(cls, rid, user=self.caller())
        except KeyError:
            self.halt(404)
        self.set_status(204)


class StatusHandler(BaseHandler):
    "Handler for status requests."

    def get(self):
        """Get service status.
        Checks upstream dependencies (db) and returns JSON object with stats.
        """
        try:
            self.db.ping()
            db_status = 'ok'
            db_error = None
        except Exception as error:
            db_status = 'error'
            db_error = str(error)

        response = {'status': db_status, 'db': db_status}
        if db_error:
            response['db_message'] = db_error
        self.write(response)
