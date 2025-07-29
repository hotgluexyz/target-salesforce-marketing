"""SalesForceMarketing target class."""

from __future__ import annotations

from singer_sdk import typing as th
from singer_sdk.target_base import Target
from target_hotglue.target import TargetHotglue

from target_salesforce_marketing.sinks import (
    ContactsSink,
    FallbackSink,
)


class TargetSalesForceMarketing(Target, TargetHotglue):
    """Sample target for SalesForceMarketing."""

    name = "target-salesforce-marketing"

    def __init__(
        self,
        config=None,
        parse_env_config: bool = False,
        validate_config: bool = True,
    ) -> None:
        self.config_file = config[0]
        super().__init__(config, parse_env_config, validate_config)

    SINK_TYPES = [ContactsSink]
    MAX_PARALLELISM = 1
    config_jsonschema = th.PropertiesList(
        th.Property("client_id", th.StringType, required=True),
        th.Property("client_secret", th.StringType, required=True),
        th.Property("sub_domain", th.StringType, required=True),
    ).to_dict()

    def get_sink_class(self, stream_name: str):
        for sink_class in self.SINK_TYPES:
            if sink_class.name.lower() == stream_name.lower():
                return sink_class

        return FallbackSink


if __name__ == "__main__":
    TargetSalesForceMarketing.cli()
