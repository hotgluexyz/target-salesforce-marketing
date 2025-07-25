"""SalesForceMarketing target sink class, which handles writing streams."""

from __future__ import annotations

from __future__ import annotations

from target_salesforce_marketing.client import SalesForceMarketingSink

class ContactsSink(SalesForceMarketingSink):
    """SalesForceMarketing target sink class."""

    
    endpoint = "/contacts/v1/contacts"
    name = "Contacts"
    

    def preprocess_record(self, record: dict, context: dict) -> None:
        return record
    
    def upsert_record(self, record: dict, context: dict):
        state_updates = dict()

        if record:
            vendor = self.request_api(
                "POST", endpoint=self.endpoint, request_data=record
            )
            vendor_id = vendor.json()["contactID"]
            return vendor_id, True, state_updates # required, or the request will be considered as failed