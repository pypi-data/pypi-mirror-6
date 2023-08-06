"""View helpers."""
import sys
import collections
import json

import contracts
from bson.objectid import ObjectId
from bson.dbref import DBRef
from flask.views import View as BaseView, http_method_funcs
from flask import request, abort, g, current_app, session

from werkzeug import http, Response
from werkzeug.wrappers import BaseResponse
from werkzeug.exceptions import HTTPException, BadRequest


def authorize(token):
    """
    Authorizes the token and returns the object meant to be stored into g.user.

    Returns None if authorization failed, else the user object.

    You must monkey patch this method to make use of the View.
    """
    raise NotImplementedError()


FLASK_BABEL_USED = False
try:
    import speaklater
    FLASK_BABEL_USED = True
except ImportError:
    pass


def convert_mongo_document_to_api_dict(obj):
    """Converts a mongo document object to the api dict that can be used for json conversion"""
    dict_ = obj.to_mongo()
    dict_.update({'id': str(dict_['_id'])})
    result = dict_.copy()  # cannot change a dict while iterating
    for k, _ in dict_.iteritems():
        if any((k.startswith('_'), k.startswith('password'))):
            del result[k]

    # next make sure we have all the fields:
    missing_fields = set(obj._fields.keys()) - set(result.keys())
    for field in missing_fields:
        result[field] = None
    return result


def _json_handler(obj):
    """Handles objects that are not JSON serializable by default."""

    # lazy gettext strings must be cast to unicode before they can be serialized
    if FLASK_BABEL_USED and isinstance(obj, speaklater._LazyString):
        return unicode(obj)

    # dates have isoformat() and should be returned as such, without microseconds and using a space as seperator
    if hasattr(obj, 'isoformat'):
        return obj.replace(microsecond=0).isoformat(' ')

    # mongo ObjectIds are cast to strings
    elif type(obj) == ObjectId:
        return str(obj)

    # mongo db references are handled as object ids.
    elif type(obj) == DBRef:
        return str(obj.id)

    # all mongo documents have to_mongo() and are returned by invoking that
    elif hasattr(obj, 'to_mongo'):
        return convert_mongo_document_to_api_dict(obj)
    elif isinstance(obj, collections.Iterable):
        return map(_json_handler, obj)
    else:
        raise TypeError('Object of type %s with value of %s '
                        'is not JSON serializable' % (type(obj), repr(obj)))


def json_dumps(obj):
    """Dump object to json with a custom json handler."""
    return json.dumps(obj, default=_json_handler)


ENCODERS = {'application/json': json_dumps,  # most API users
            'text/html': str,  # browser, coming from redirect from OAuth
            }


class ViewType(type):
    """View meta class."""
    def __new__(cls, name, bases, attrs):
        """Ensure that created class will have `methods` attribute which is a list of supported HTTP methods for
        creating view class."""
        rv = type.__new__(cls, name, bases, attrs)
        if 'methods' not in attrs:
            methods = set(rv.methods or [])
            for key in attrs:
                if key in http_method_funcs:
                    methods.add(key.upper())
            # if we have no method at all in there we don't want to
            # add a method list.  (This is for instance the case for
            # the baseclass or another subclass of a base method view
            # that does not introduce new methods).
            if methods:
                rv.methods = sorted(methods)
        return rv


class View(BaseView):
    """View class."""
    __metaclass__ = ViewType

    def dispatch_request(self, **kwargs):

        method_name = request.method.lower()

        # import this here to be sure of correct settings
        # and the existance of a request (to use current_app)
        from pltk.flask_utils.limit import inject_x_rate_headers

        # only check rate limits when not debugging
        if current_app.debug:
            # mimick class RateLimit
            g._view_rate_limit = type('object',
                                      (),
                                      dict(send_x_headers=True,
                                           remaining=sys.maxint,
                                           limit=sys.maxint,
                                           reset=sys.maxint,
                                           ),
                                      )

        else:
            # import this here to be sure of correct settings
            # and the existance of a request (to use current_app)
            from pltk.flask_utils.limit import(
                RateLimit,
                on_limit_reached)

            key = 'rate-limit/%s/%s/%s/' % (
                request.endpoint,
                method_name,
                request.remote_addr)

            limit = g.redis.get_config('DEFAULT_RATE_LIMIT')
            per = g.redis.get_config('DEFAULT_RATE_PER')
            exp = g.redis.get_config('DEFAULT_RATE_EXP_WINDOW')

            config_key = '%s.%s' % (request.endpoint, method_name)

            custom_rate_limit = g.redis.get_config('CUSTOM_RATE_LIMIT')

            if config_key in custom_rate_limit:
                limit, per, exp = custom_rate_limit[config_key]

            rlimit = RateLimit(g.redis, key, limit, per, True, exp)

            g._view_rate_limit = rlimit

            if rlimit.over_limit:
                return on_limit_reached(rlimit)

        meth = getattr(self, method_name)

        # require auth by default
        needs_auth = getattr(meth, 'needs_auth', True)
        # session_token might be provided in the header...
        session_token = request.headers.get('Authorization')
        # ...as a querystring parameter instead...
        if not session_token:
            session_token = request.args.get('session_token', None)
        # ...or in the browser session (in a cookie)
        if not session_token:
            session_token = session.get('session_token', None)
        if needs_auth and not session_token:
            abort(401, 'Unauthorized access')
        if session_token:
            g.user = authorize(session_token)
        else:
            g.user = None

        if needs_auth and g.user is None:
            abort(403, 'Authentication token is invalid')

        encoder, self.encoding = get_encoder()

        if request.method == 'GET':
            # .update(request.args) will have lists of values
            kwargs.update((k, v) for k, v in request.args.iteritems())
        else:
            # FIXME: only supports application/json content type right now. In
            # case of need, upgrade to DECODERS or rely on Werkzeug's ability
            # to decode content types
            # This method will never raise ValueError exception since this
            # exception will be catched before
            try:
                kwargs.update(request.json or {})
            except (BadRequest, ValueError):
                kwargs.update({})

        # FIX unicode dictionary keys to strings for older pythons
        if sys.version_info < (2, 7):  # pragma: no cover
            kwargs = self.dict_keys_to_string(kwargs)

        try:
            try:
                result = meth(**kwargs)
            except (contracts.ContractException) as e:
                abort(400, str(e))
        except HTTPException as e:
            result = Response({"code": e.code, "error": unicode(e.description)}, e.code, mimetype=self.encoding)

        if isinstance(result, BaseResponse):
            response = result
        else:
            if not isinstance(result, basestring):
                result = encoder(result)
            response = Response(result, 200, mimetype=self.encoding)

        return inject_x_rate_headers(response)

    def dict_keys_to_string(self, kwargs):
        """Convert passed dict keys to strings.

        ..warning:: On failure returns the passed dictionary.

        :param dict kwargs: a dictionary whose keys will be replaced
                            to strings.

        :return: A new dict where keys are replaced to strings.

        """
        try:
            skwargs = dict()
            for k, v in kwargs.iteritems():
                skwargs[str(k)] = v
            return skwargs
        except:
            return kwargs

    def get_ok_message(self):
        """Generate OK message."""
        return {'message': 'ok'}


def get_encoder(default='application/json'):
    """Get the encoder from the headers."""
    try:
        accept = request.headers['Accept']
    except KeyError:
        return ENCODERS[default], default
    try:
        for encoding, _ in http.parse_accept_header(accept):
            if encoding == '*/*':
                return ENCODERS[default], default
            elif encoding in ENCODERS:
                return ENCODERS[encoding], encoding
    except TypeError:
        # The encoder doesn't exist
        pass
    abort(400, 'Unsupported return encoding')


def public(func):
    """Do not require authentication on given view method."""
    msg = "*Does not require authentication*\n"
    doc = func.__doc__
    prefix = doc[:len(doc) - len(doc.lstrip())]
    func.__doc__ = prefix + msg + doc
    func.needs_auth = False
    return func
