#!/usr/bin/env python
#import base64
#from oic.oauth2.message import MissingRequiredAttribute
from oic.oauth2.message import ErrorResponse
from oic.oauth2.message import AuthorizationErrorResponse

__author__ = 'rohe0002'

import logging

from oic.utils.http_util import Response
from oic.utils.http_util import Redirect
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

    def _error_response(self, error, descr=None):
        logger.error("%s" % error)
        response = ErrorResponse(error=error, error_description=descr)
        return Response(response.to_json(), content="application/json",
                        status="400 Bad Request")

    def _error(self, error, descr=None):
        response = ErrorResponse(error=error, error_description=descr)
        return Response(response.to_json(), content="application/json",
                        status="400 Bad Request")

    def _authz_error(self, error, descr=None):

        response = AuthorizationErrorResponse(error=error)
        if descr:
            response["error_description"] = descr

        return Response(response.to_json(), content="application/json",
                        status="400 Bad Request")

    def _redirect_authz_error(self, error, redirect_uri, descr=None):
        err = ErrorResponse(error=error)
        if descr:
            err["error_description"] = descr
        location = err.request(redirect_uri)
        return Redirect(location)


class AuthorizationEndpoint(Endpoint):
    etype = "authorization"

    # def _call(self, request, *args, **kwargs):
    #     logger.debug("- authorization -")
    #     logger.debug("Query: '%s'" % request)
    #
    #     try:
    #         areq = self.srvmethod.parse_authorization_request(query=request)
    #     except MissingRequiredAttribute, err:
    #         return BadRequest("%s" % err)
    #     except Exception, err:
    #         return BadRequest("%s" % err)
    #
    #     #        if "redirect_uri" in areq:
    #     #            _redirect = areq["redirect_uri"]
    #     #        else:
    #     #            # A list, so pick one (==the first)
    #     #            _redirect = self.urlmap[areq["client_id"]][0]
    #
    #     sid = _sdb.create_authz_session("", areq)
    #     bsid = base64.b64encode(sid)
    #
    #     grant = _sdb[sid]["code"]
    #     logger.dbug("code: '%s'" % grant)
    #
    #     return self.function["authenticate"](bsid)


class TokenEndpoint(Endpoint):
    etype = "token"


