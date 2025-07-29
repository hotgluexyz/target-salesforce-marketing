import json
import logging
import requests
import time
from typing import Any, Dict

from target_hotglue.auth import Authenticator

class SalesForceMarketingAuthenticator(Authenticator):
    """API Authenticator for OAuth 2.0 client credentials flow."""

    def __init__(self, target, state):
        super().__init__(target, state)
        # Fallback logger if not present on target
        self.logger = getattr(target, 'logger', logging.getLogger(__name__))
        self._config_file_path = getattr(target, '_config_file_path', None)

    @property
    def auth_headers(self) -> dict:
        if not self.is_token_valid():
            self.update_access_token()
        result = {}
        result["Authorization"] = f"Bearer {self._config.get('access_token')}"
        return result

    def is_token_valid(self) -> bool:
        access_token = self._config.get("access_token")
        expires_at = self._config.get("access_token_expires_at")
        if not access_token or not expires_at:
            return False
        now = int(time.time())
        # Consider token valid if it expires in more than 2 minutes
        return (int(expires_at) - now) > 120

    def update_access_token(self) -> None:
        token_url = f"https://{self._config['sub_domain']}.auth.marketingcloudapis.com/v2/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": self._config["client_id"],
            "client_secret": self._config["client_secret"],
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        self.logger.info(f"Requesting new access token from {token_url}")
        response = requests.post(token_url, data=payload, headers=headers)
        try:
            response.raise_for_status()
            token_json = response.json()
            access_token = token_json["access_token"]
            expires_in = int(token_json.get("expires_in", 3600))
            expires_at = int(time.time()) + expires_in
            self._config["access_token"] = access_token
            self._config["access_token_expires_at"] = expires_at
            # Persist to config file if possible
            if self._config_file_path:
                with open(self._config_file_path, "w") as outfile:
                    json.dump(self._config, outfile, indent=4)
            self.logger.info("Successfully obtained new access token.")
        except Exception as ex:
            self.logger.error(f"Failed to obtain access token: {response.text}")
            raise RuntimeError(f"Failed to obtain access token: {response.text}") from ex