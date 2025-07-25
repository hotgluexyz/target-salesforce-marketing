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
            contact = self.request_api(
                "POST", endpoint=self.endpoint, request_data=record
            )
            contact_id = contact.json()["contactID"]
            return contact_id, True, state_updates

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
        
        try:
            items = response.json()['items']
        except Exception as e:
            self.logger.error(f"Error getting data extension {self.name}: {e}")
            return {'error': f"Error getting data extension {self.name}: {e}"}

        if len(items) == 0:
            self.logger.error(f"Data extension {self.name} not found")
            return {'error': f"Data extension {self.name} not found"}
        
        item = items[0]
        if item.get('name') != self.name:
            self.logger.error(f"Data extension {self.name} not found")
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

        try:
            response_json = response.json()
            request_id = response_json.get("requestId")
        except Exception as e:
            self.logger.error(f"Error upserting record.", extra={"DEId": record["DEId"], "record": record, "error": e})
            return None, False, {'error': f"Error upserting record: {e}"}

        state_updates = dict()
        return request_id, True, state_updates