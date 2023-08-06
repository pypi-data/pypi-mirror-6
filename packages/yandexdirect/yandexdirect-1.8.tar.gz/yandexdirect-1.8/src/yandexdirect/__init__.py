# encoding=utf-8

"""Yandex.Direct bindings for Python.

Implements API v4.

http://api.yandex.ru/direct/doc/concepts/About.xml
"""

import json
import time
import urllib
import urllib2


__author__ = "Justin Forest <hex@umonkey.net>"
__license__ = "GNU LGPL"


class Error(Exception):
    pass


class AuthError(Error):
    pass


class BadCampaignError(Error):
    pass


class Client(object):
    """Contains functions to access the Yandex API."""
    def __init__(self, application_id, login, auth_token, sandbox=False, password=None, timeout=3600, logger=None):
        self.application_id = application_id
        self.application_password = password
        self.login = login
        self.auth_token = auth_token
        self.sandbox = sandbox
        self.timeout = timeout
        self.logger = logger
        self.request_count = 0

    def call_method(self, method, param=None):
        """Calls an API method."""
        for attempt in range(10):
            delay = 5 * (attempt + 1)

            try:
                payload = {"method": method, "application_id": self.application_id,
                    "login": self.login, "token": self.auth_token}
                if param is not None:
                    payload["param"] = param

                data = json.loads(self._fetch(self._get_api_root(method), json.dumps(payload)))
                if type(data) != dict:
                    self.logger.error("Got %s instead of a dict: %s" % (type(data), data))
                    enigma.error(500, "Could not interpret a Yandex.API response.")

                if "error_code" in data:
                    if data["error_code"] == 53:
                        raise AuthError(data["error_str"])
                    elif data["error_code"] == 1:
                        raise BadCampaignError(data["error_str"])
                    elif data["error_code"] == 52:  # login temporary unavailable
                        delay = 30
                        raise RuntimeError(data["error_str"])

                    message = data["error_detail"]
                    if data["error_str"]:
                        if message:
                            message += "; "
                        message += data["error_str"]
                    raise Error("Error %s calling method %s: %s" % (data["error_code"], method, message))

                if "data" not in data:
                    raise Error("Yandex.API response has no \"data\" block.")

                return data["data"]
            except Error:
                raise
            except Exception, e:
                self.logger.exception("Error, will retry in %u seconds: %s" % (delay, e))
                time.sleep(delay)

        raise e

    def _get_api_root(self, method):
        """Returns the API URL for the specified method."""
        # GetClientsList is very slow in v4 API for some reason.
        if self.sandbox:
            return "https://api-sandbox.direct.yandex.ru/json-api/v4/"
        return "https://soap.direct.yandex.ru/json-api/v4/"

    def _fetch(self, url, args):
        """Performs a POST request, returns the response body.  Uses App Engine's urlfetch where available to disable
        SSL certificate checking (which doesn't work with this API because Yandex has 'Yandex Direct' as the CNAME."""
        ts = time.time()
        try:
            self.request_count += 1
            return urllib2.urlopen(url, args, self.timeout).read()
        finally:
            if self.logger:
                self.logger.debug("Fetching %s, args: %s, request=%u, took %.2f seconds." \
                    % (url, args, self.request_count, time.time() - ts))

    def __repr__(self):
        return "<yandexdirect.Client application_id=%s login=%s>" % (self.application_id, self.login)

    def get_auth_url(self, state=None):
        return "https://oauth.yandex.ru/authorize?response_type=code&client_id=%s&state=%s" % (self.application_id, urllib.quote(state or ""))

    def get_token_by_code(self, code):
        """Used during OAuth authentication."""
        payload = "grant_type=authorization_code&code=%s&client_id=%s" % (code, self.application_id)
        if self.application_password is not None:
            payload += "&client_secret=" + self.application_password
        response = self._fetch("https://oauth.yandex.ru/token", payload)

        data = json.loads(response)
        if "access_token" not in data:
            self.logger.debug("OAuth response: %s" % data)
            raise AuthError("OAuth server replied with no access token (see the debug log).")
        return data["access_token"]

    def GetVersion(self):
        """Returns the API version number."""
        return self.call_method("GetVersion")

    def Ping(self, login=None, token=None):
        """Pings the API server, must return 1 on success."""
        old_login = self.login
        old_token = self.auth_token
        try:
            if login is not None:
                self.login = login
            if token is not None:
                self.auth_token = token
            return self.call_method("PingAPI") == 1
        except Exception, e:
            self.logger.error("Could not ping the API: %s" % e)
            return False
        finally:
            self.login = old_login
            self.auth_token = old_token

    def GetBanners(self, campaign_ids=None, banner_ids=None, archive=None):
        _filter = {}
        if archive == True:
            _filter["StatusArchive"] = ["Yes"]
        elif archive == False:
            _filter["StatusArchive"] = ["No"]

        if banner_ids is not None:
            return self.call_method("GetBanners", {
                "BannerIDS": banner_ids,
                "GetPhrases": "No",
                "Filter": _filter,
            })

        banners = []
        campaign_ids = list(campaign_ids)
        while campaign_ids:
            banners.extend(self.call_method("GetBanners", {
                "CampaignIDS": campaign_ids[:10],
                "GetPhrases": "WithPrices",
                "Filter": _filter,
            }))
            del campaign_ids[:10]

        return banners

    def GetBannerPhrases(self, banner_ids):
        phrases = []
        while banner_ids:
            phrases.extend(self.call_method("GetBannerPhrases",
                banner_ids[:1000]))
            del banner_ids[:1000]
        return phrases

    def GetClientInfo(self, names):
        return self.call_method("GetClientInfo", names)

    def GetClientsList(self, archive=False):
        StatusArch = "No"
        if archive:
            StatusArch = "Yes"
        return self.call_method("GetClientsList", {
            "Filter": {
                "StatusArch": StatusArch,
            }
        })

    def GetSubClients(self, client, archive=None):
        _filter = {"Login": client}
        if archive == True:
            _filter["Filter"] = {"StatusArch": True}
        elif archive == False:
            _filter["Filter"] = {"StatusArch": False}
        return self.call_method("GetSubClients", _filter)

    def GetCampaignsParams(self, ids):
        if not isinstance(ids, list):
            raise TypeError("ids must be a list of integers")
        return self.call_method("GetCampaignsParams", {
            "CampaignIDS": ids,
        })

    def GetCampaignsList(self, clients=None, with_archived=False, with_client_info=False):
        """Возвращает описания кампаний указанных клиентов.  Если клиенты не указаны, возвращает описания всех кампаний
        (выполняет более одного запроса)."""

        all_clients = None
        if clients is None:
            all_clients = dict([(client["Login"], client) for client in self.GetClientsList()])
            clients = all_clients.keys()

        if not isinstance(clients, list):
            raise ValueError("clients must be a list")

        campaigns = []
        while clients:
            campaigns.extend(self.call_method("GetCampaignsList", clients[:100]))
            del clients[:100]

        if with_client_info and all_clients is not None:
            for idx, campaign in enumerate(campaigns):
                campaigns[idx]["Login_details"] = all_clients[campaign["Login"]]

        if not with_archived:
            campaigns = filter(lambda c: c["StatusArchive"] == "No", campaigns)

        return campaigns

    def UpdatePrices(self, updates, step=100):
        if not isinstance(updates, (list, tuple)):
            raise Exception('update_phrases() expects a list.')
        while updates:
            payload = updates[:step]
            del updates[:step]
            self.call_method("UpdatePrices", payload)

    def StopCampaign(self, CampaignID):
        self.logger.info("Stopping campaign %s" % CampaignID)
        self.call_method("StopCampaign", {"CampaignID": CampaignID})

    def ResumeCampaign(self, CampaignID):
        self.logger.info("Resuming campaign %s" % CampaignID)
        self.call_method("ResumeCampaign", {"CampaignID": CampaignID})

    def GetCampaignParams(self, CampaignID):
        return self.call_method("GetCampaignParams", {"CampaignID": CampaignID})
