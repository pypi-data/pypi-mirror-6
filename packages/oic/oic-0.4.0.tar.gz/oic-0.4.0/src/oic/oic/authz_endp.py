import base64
import logging
import sys
import traceback
import urllib
import urlparse
from requests import ConnectionError
import time
from oic.utils.http_util import BadRequest
from oic.oauth2.exception import RedirectURIError, UnknownClient, ParameterError, URIError
from oic.oic.message import AuthorizationRequest, OpenIDRequest
from oic.oauth2.endpoint import Endpoint
from oic.oauth2.message import MissingRequiredAttribute

logger = logging.getLogger(__name__)
STR = 5 * "_"


def construct_uri(item):
    (base_url, query) = item
    if query:
        return "%s?%s" % (base_url, urllib.urlencode(query))
    else:
        return base_url


class AuthorizationEndpoint(Endpoint):
    etype = "authorization"

    def __init__(self, cli):
        self.cli = cli

    def get_redirect_uri(self, areq):
        """ verify that the redirect URI is reasonable
        :param areq: The Authorization request
        :return: Tuple of (redirect_uri, Response instance)
            Response instance is not None of matching redirect_uri failed
        """
        if 'redirect_uri' in areq:
            self._verify_redirect_uri(areq)
            uri = areq["redirect_uri"]
        else:  # pick the one registered
            ruris = self.cli.cdb[areq["client_id"]]["redirect_uris"]
            if len(ruris) == 1:
                uri = construct_uri(ruris[0])
            else:
                raise ParameterError(
                    "Missing redirect_uri and more than one registered")

        return uri

    def _verify_redirect_uri(self, areq):
        """
        MUST NOT contain a fragment
        MAY contain query component

        :return: An error response if the redirect URI is faulty otherwise
            None
        """
        try:
            _redirect_uri = urlparse.unquote(areq["redirect_uri"])

            part = urlparse.urlparse(_redirect_uri)
            if part.fragment:
                raise URIError("Contains fragment")

            (_base, _query) = urllib.splitquery(_redirect_uri)
            if _query:
                _query = urlparse.parse_qs(_query)

            match = False
            for regbase, rquery in self.cli.cdb[areq["client_id"]][
                    "redirect_uris"]:
                if _base == regbase or _redirect_uri.startswith(regbase):
                    # every registered query component must exist in the
                    # redirect_uri
                    if rquery:
                        for key, vals in rquery.items():
                            assert key in _query
                            for val in vals:
                                assert val in _query[key]
                    match = True
                    break
            if not match:
                raise RedirectURIError("Doesn't match any registered uris")
                # ignore query components that are not registered
            return None
        except Exception, err:
            logger.error("Faulty redirect_uri: %s" % areq["redirect_uri"])
            _cinfo = self.cli.cdb[areq["client_id"]]
            logger.info("Registered redirect_uris: %s" % _cinfo)
            raise RedirectURIError("Faulty redirect_uri: %s" % err)

    def _parse_openid_request(self, request):
        return OpenIDRequest().from_jwt(request, keyjar=self.cli.keyjar)

    def _sso(self, openid_req, sid, **kwargs):

        if openid_req:
            logger.info("Request: %s" % openid_req.to_dict())
            try:
                _max_age = openid_req["id_token"]["max_age"]
            except KeyError:
                _max_age = -1

            if _max_age >= 0:
                if "handle" in kwargs:
                    try:
                        (key, timestamp) = kwargs["handle"]
                        logger.info("key: %s" % key)
                        if key.startswith(STR) and key.endswith(STR):
                            pass
                        else:
                            _now = time.mktime(time.gmtime())
                            _sdb = self.cli.sdb

                            if (_now - int(timestamp)) <= _max_age:
                                logger.info("- SSO -")
                                _scode = base64.b64decode(key)
                                logger.debug("OLD session: %s" % _sdb[_scode])
                                user = _sdb[_scode]["sub"]
                                _sdb.update(sid, "sub", user)
                                return user, _scode,
                            else:
                                logger.info(
                                    "Authentication to old: %d>%d" % (
                                        _now - int(timestamp), _max_age))
                    except ValueError:
                        pass
        else:
            if "handle" in kwargs and kwargs["handle"]:
                (key, timestamp) = kwargs["handle"]
                if key.startswith(STR) and key.endswith(STR):
                    pass
                else:
                    _sdb = self.cli.sdb
                    try:
                        logger.info("- SSO -")
                        _scode = base64.b64decode(key)
                        user = _sdb[_scode]["sub"]
                        _sdb.update(sid, "sub", user)
                        # This happens if a valid cookie is presented
                        return user, _scode
                    except ValueError:
                        pass
        return None

    def _call(self, request, *args, **kwargs):
        """ The AuthorizationRequest endpoint

        :param request: The client request
        """
        try:
            _log_debug = kwargs["logger"].debug
            _log_info = kwargs["logger"].info
        except KeyError:
            _log_debug = logger.debug
            _log_info = logger.info
        _sdb = self.cli.sdb
        _srv = self.cli.server

        _log_debug("request: %s" % request)

        # Same serialization used for GET and POST
        try:
            areq = _srv.parse_authorization_request(query=request)
        except (MissingRequiredAttribute, KeyError):
            areq = AuthorizationRequest().deserialize(request, "urlencoded")
            # verify the redirect_uri
            try:
                self.get_redirect_uri(areq)
            except RedirectURIError, err:
                return self._error("invalid_request", "%s" % err)
        except Exception, err:
            message = traceback.format_exception(*sys.exc_info())
            logger.error(message)
            _log_debug("Bad request: %s (%s)" % (err, err.__class__.__name__))
            return BadRequest("%s" % err)

        try:
            redirect_uri = self.get_redirect_uri(areq)
        except RedirectURIError, err:
            return self._error("invalid_request", "%s" % err)

        try:
            client_info = self.cli.cdb[areq["client_id"]]
        except KeyError:
            _log_info("Unknown client: %s" % areq["client_id"])
            raise UnknownClient(areq["client_id"])

        if "request_uri" in areq:
            # Do a HTTP get
            try:
                _req = _srv.http_request(areq["request_uri"])
            except ConnectionError:
                return self._authz_error("invalid_request_uri")

            if not _req:
                return self._authz_error("invalid_request_uri")

            try:
                resq = self._parse_openid_request(_req.text)
            except Exception:
                return self._redirect_authz_error(
                    "invalid_openid_request_object", redirect_uri)

            areq["request"] = resq

        try:
            openid_req = areq["request"]
        except KeyError:
            openid_req = None

        if openid_req:
            try:
                user = openid_req["id_token"]["claims"]["sub"]["value"]
            except KeyError:
                user = ""
        elif "id_token" in areq:
            user = areq["id_token"]["sub"]
        else:
            user = ""

        if user:
            try:
                sid = _sdb.get_sid_from_userid(user)
            except KeyError:
                logger.error("Unknown user id '%s'" % user)
                logger.debug("uid2sid: %s" % _sdb.uid2sid)
                sid = ""

            if sid:
                return self.authenticated(active_auth=sid,
                                          areq=areq, user=user)

        if "prompt" in areq:
            _log_debug("Prompt: '%s'" % areq["prompt"])

            if "none" in areq["prompt"]:
                return self._redirect_authz_error("login_required",
                                                  redirect_uri)
            elif "login" in areq["prompt"]:
                # force re-authentication, remove link to SSO history
                try:
                    del kwargs["handle"]
                except KeyError:
                    pass

        _log_debug("AREQ keys: %s" % areq.keys())

        sid = _sdb.create_authz_session(user, areq, oidreq=openid_req)

        _log_debug("session: %s" % _sdb[sid])

        bsid = base64.b64encode(sid)

        cookie = None

        if self.authn_as:
            sub = self.authn_as
            _log_debug("Implicit authenticated as %s" % sub)
            _sdb.update(sid, "local_sub", sub)
            (redirect_uri, reply) = self.get_redirect_uri(areq)
            client_info = self.cdb[areq["client_id"]]
            sector_id = self.get_sector_id(redirect_uri, client_info)

            try:
                preferred_id_type = client_info["preferred_id_type"]
            except KeyError:
                preferred_id_type = self.preferred_id_type

            self.sdb.do_userid(sid, sub, sector_id, preferred_id_type)
            _log_debug("session: %s" % _sdb[sid])
            _log_debug("uid2sid: %s" % _sdb.uid2sid)
            return self.authenticated(active_auth=sid, areq=areq, user=sub)

        try:
            user, _scode = self._sso(openid_req, sid, **kwargs)
            return self.authenticated(active_auth=_scode, areq=areq, user=user)
        except TypeError:
            if "handle" in kwargs and kwargs["handle"]:
                (key, timestamp) = kwargs["handle"]
                if key.startswith(STR) and key.endswith(STR):
                    cookie = self.cookie_func(self.cookie_name, key,
                                              self.seed, self.cookie_ttl)

        # DEFAULT: start the authentication process
        kwa = {"cookie": cookie}
        for item in ["policy_uri", "logo_uri"]:
            try:
                kwa[item] = client_info[item]
            except KeyError:
                pass

        _log_info("KWA: %s" % kwa)
        return self.function["authenticate"](bsid, **kwa)

