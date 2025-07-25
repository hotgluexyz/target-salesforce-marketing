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
            return vendor_id, True, state_updates

class FallbackSink(SalesForceMarketingSink):
    """SalesForceMarketing target sink class."""

    @property
    def name(self):
        return self.stream_name
    
    def preprocess_record(self, record: dict, context: dict) -> None:
        response = self.request_api(
            "GET",
            endpoint="/data/v1/customobjects",
            params={"$search": self.name, "$pagesize": 1}
        )
        
        items = response.json()['items']

        if len(items) == 0:
            return {'error': f"Data extension {self.name} not found"}
        
        item = items[0]
        if item.get('name') != self.name:
            return {'error': f"Data extension {self.name} not found"}
        
        return {
            "DEId": item.get('key'),
            "payload": record,
        }
    
    def upsert_record(self, record: dict, context: dict):
        if "error" in record:
            return None, False, record.get('error')
        
        payload = {
            "items": [
                record.get('payload')
            ]
        }

        # Construct the endpoint using the externalId from the record
        endpoint = f"/data/v1/async/dataextensions/key:{record['DEId']}/rows"

        # Make the API request using self.request_api
        response = self.request_api(
            "PUT",
            endpoint=endpoint,
            request_data=payload,
            headers={"content-type": "application/json"}
        )

        response_json = response.json()
        request_id = response_json.get("requestId")

        state_updates = dict()
        return request_id, True, state_updates