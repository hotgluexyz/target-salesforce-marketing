"""SalesForceMarketing target sink class, which handles writing streams."""

from target_hotglue.client import HotglueSink
from target_salesforce_marketing.auth import SalesForceMarketingAuthenticator


class SalesForceMarketingSink(HotglueSink):
    """SalesForceMarketing target sink class."""

    @property
    def base_url(self) -> str:
        return f"https://{self._config['sub_domain']}.rest.marketingcloudapis.com"
    
    @property
    def authenticator(self):
        return SalesForceMarketingAuthenticator(self._target, dict())