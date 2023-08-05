#!/usr/bin/env python
import json
import traceback
import urllib
import sys
from saml2.saml import assertion_from_string
from oic.utils.time_util import utc_time_sans_frac
from oic.utils.keyio import KeyBundle, key_export

from requests import ConnectionError

from oic.oauth2.message import ErrorResponse, by_schema, MessageException
from oic.oic.message import AuthorizationRequest
from oic.oic.message import IdToken
from oic.oic.message import OpenIDSchema
from oic.oic.message import RegistrationResponse
from oic.oic.message import AuthorizationResponse
from oic.oic.message import AuthorizationErrorResponse
from oic.oic.message import OpenIDRequest
from oic.oic.message import AccessTokenResponse
from oic.oic.message import AuthnToken
from oic.oic.message import AccessTokenRequest
from oic.oic.message import TokenErrorResponse
from oic.oic.message import SCOPE2CLAIMS
from oic.oic.message import RegistrationRequest
from oic.oic.message import ClientRegistrationErrorResponse
from oic.oic.message import UserInfoClaim
from oic.oic.message import DiscoveryRequest
from oic.oic.message import ProviderConfigurationResponse
from oic.oic.message import DiscoveryResponse

from jwkest import jws, jwe
from jwkest.jws import alg2keytype

__author__ = 'rohe0002'

import random
import base64
import urlparse
import hmac
import time
import hashlib
import logging

from urlparse import parse_qs

from oic.oauth2.provider import Provider as AProvider

from oic.utils.http_util import Response
from oic.utils.http_util import Redirect
from oic.utils.http_util import BadRequest
from oic.utils.http_util import Unauthorized

from oic.oauth2 import MissingRequiredAttribute
from oic.oauth2 import rndstr

from oic.oic import Server
from oic.oic import SAML2_BEARER_ASSERTION_TYPE
from oic.oic import JWT_BEARER

from oic.oauth2.exception import *

logger = logging.getLogger(__name__)

SWD_ISSUER = "http://openid.net/specs/connect/1.0/issuer"
STR = 5 * "_"


class Cookie(object):
    def __init__(self):
        self.cookie_func = None
        self.cookie_name = "pyoidc"
        self.seed = ""
        self.cookie_ttl = 0

    def create(self, handle):
        (key, timestamp) = handle

        if key.startswith(STR) and key.endswith(STR):
            return self.cookie_func(self.cookie_name, key, self.seed,
                                    self.cookie_ttl)

        return None


def create_response(_response, headers, cookie_handler, handle=None):
    if handle:
        kaka = cookie_handler.create(handle)
        if kaka:
            headers.append(kaka)

    return Response(_response.to_json(), content="application/json",
                    headers=headers)


class Endpoint(object):
    etype = ""

    def __init__(self, baseurl, kakfunc):
        self.baseurl = baseurl
        self.cookie_func = kakfunc

    @property
    def name(self):
        return "%s_endpoint" % self.etype

    def __call__(self, handle, *args, **kwargs):
        resp = self._call(*args, **kwargs)
        return create_response(resp, self.cookie_func, handle)

    def _call(self, *args, **kwargs):
        raise NotImplementedError

    def input(self, **kwargs):
        # Support GET and POST
        try:
            return kwargs["query"]
        except KeyError:
            try:
                return kwargs["post"]
            except KeyError:
                raise MissingParameter("No input")


class AuthorizationEndpoint(Endpoint):
    etype = "authorization"

    def _call(self, *args, **kwargs):
        """ The AuthorizationRequest endpoint

        :param request: The client request
        """
        try:
            _log_debug = kwargs["logger"].debug
            _log_info = kwargs["logger"].info
        except KeyError:
            _log_debug = logger.debug
            _log_info = logger.info
        _sdb = self.sdb
        _srv = self.server

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
            client_info = self.cdb[areq["client_id"]]
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

        if openid_req:
            _log_info("Request: %s" % openid_req.to_dict())
            try:
                _max_age = openid_req["id_token"]["max_age"]
            except KeyError:
                _max_age = -1

            if _max_age >= 0:
                if "handle" in kwargs:
                    try:
                        (key, timestamp) = kwargs["handle"]
                        _log_info("key: %s" % key)
                        if key.startswith(STR) and key.endswith(STR):
                            pass
                        else:
                            _now = time.mktime(time.gmtime())
                            if (_now - int(timestamp)) <= _max_age:
                                _log_info("- SSO -")
                                _scode = base64.b64decode(key)
                                _log_debug("OLD session: %s" % _sdb[_scode])
                                user = self.sdb[_scode]["sub"]
                                _sdb.update(sid, "sub", user)
                                return self.authenticated(active_auth=_scode,
                                                          areq=areq, user=user)
                            else:
                                _log_info(
                                    "Authentication to old: %d>%d" % (
                                        _now - int(timestamp), _max_age))
                    except ValueError:
                        pass
        else:
            if "handle" in kwargs and kwargs["handle"]:
                (key, timestamp) = kwargs["handle"]
                if key.startswith(STR) and key.endswith(STR):
                    cookie = self.cookie_func(self.cookie_name, key,
                                              self.seed, self.cookie_ttl)
                else:
                    try:
                        _log_info("- SSO -")
                        _scode = base64.b64decode(key)
                        user = self.sdb[_scode]["sub"]
                        _sdb.update(sid, "sub", user)
                        # This happens if a valid cookie is presented
                        return self.authenticated(active_auth=_scode,
                                                  areq=areq, user=user)
                    except ValueError:
                        pass

        # DEFAULT: start the authentication process
        kwa = {"cookie": cookie}
        for item in ["policy_uri", "logo_uri"]:
            try:
                kwa[item] = client_info[item]
            except KeyError:
                pass

        _log_info("KWA: %s" % kwa)
        return self.function["authenticate"](bsid, **kwa)


class TokenEndpoint(Endpoint):
    etype = "token"


class UserinfoEndpoint(Endpoint):
    etype = "userinfo"


class RegistrationEndpoint(Endpoint) :
    etype = "registration"


class DiscoveryEndpoint(Endpoint):

    def _call(self, handle, *args, **kwargs):
        _log_debug = logger.debug

        _log_debug("@discovery_endpoint")

        try:
            query = self.input(**kwargs)
        except MissingParameter:
            return BadRequest("Missing input")

        request = DiscoveryRequest().deserialize(query, "urlencoded")
        _log_debug("discovery_request:%s" % (request.to_dict(),))

        try:
            assert request["service"] == SWD_ISSUER
        except AssertionError:
            return BadRequest("Unsupported service")

        # verify that the principal is one of mine

        _response = DiscoveryResponse(locations=[self.baseurl])

        _log_debug("discovery_response:%s" % (_response.to_dict(),))

        headers = [("Cache-Control", "no-store")]

        return _response, headers


class ProviderinfoEndpoint(Endpoint):
    
    def _call(self, jwks_uri="", endpoints=None, *args, **kwargs):
        _log_info = logger.info
    
        _response = ProviderConfigurationResponse(
            issuer=self.baseurl,
            token_endpoint_auth_methods_supported=[
                "client_secret_post", "client_secret_basic",
                "client_secret_jwt", "private_key_jwt"],
            scopes_supported=["openid"],
            response_types_supported=["code", "token", "id_token",
                                      "code token", "code id_token",
                                      "token id_token",
                                      "code token id_token"],
            subject_types_supported=["public", "pairwise"],
            grant_types_supported=[
                "authorization_code", "implicit",
                "urn:ietf:params:oauth:grant-type:jwt-bearer"],
            claim_types_supported=["normal", "aggregated", "distributed"],
            claims_supported=SCOPE2CLAIMS.keys(),
            claims_parameter_supported="true",
            request_parameter_supported="true",
            request_uri_parameter_supported="true",
            #request_object_algs_supported=["HS256"]
        )

        sign_algs = jws.SIGNER_ALGS.keys()

        for typ in ["userinfo", "id_token", "request_object",
                    "token_endpoint_auth"]:
            _response["%s_signing_alg_values_supported" % typ] = sign_algs

        algs = jwe.SUPPORTED["alg"]
        for typ in ["userinfo", "id_token", "request_object"]:
            _response["%s_encryption_alg_values_supported" % typ] = algs

        encs = jwe.SUPPORTED["enc"]
        for typ in ["userinfo", "id_token", "request_object"]:
            _response["%s_encryption_enc_values_supported" % typ] = encs

        if not self.baseurl.endswith("/"):
            self.baseurl += "/"

        #keys = self.keyjar.keys_by_owner(owner=".")
        if jwks_uri:
            _response["jwks_uri"] = jwks_uri

        #_log_info("endpoints: %s" % self.endpoints)
        for endp in endpoints:
            #_log_info("# %s, %s" % (endp, endp.name))
            _response[endp.name] = "%s%s" % (self.baseurl, endp.etype)

        _log_info("provider_info_response: %s" % (_response.to_dict(),))

        headers = [("Cache-Control", "no-store"), ("x-ffo", "bar")]

        return resp, headers


        # except Exception, err:
        # message = traceback.format_exception(*sys.exc_info())
        # logger.error(message)
        # resp = Response(message, content="html/text")
