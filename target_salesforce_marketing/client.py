"""SalesForceMarketing target sink class, which handles writing streams."""

from __future__ import annotations
from abc import abstractmethod

import backoff
import requests
from singer_sdk.exceptions import FatalAPIError, RetriableAPIError

from singer_sdk.sinks import RecordSink

from target_hotglue.client import HotglueSink


from target_salesforce_marketing.auth import SalesForceMarketingAuthenticator


class SalesForceMarketingSink(HotglueSink, RecordSink):
    """SalesForceMarketing target sink class."""

    @property
    def base_url(self) -> str:
        return self._config.get("rest_url")
    
    @property
    def authenticator(self):
        return SalesForceMarketingAuthenticator(self._target, dict())