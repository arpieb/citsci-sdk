"""Base model shared by all CitSci-native models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

# A related resource may arrive either as an IRI string (e.g. "/projects/42") or, when the
# API embeds it, as a nested object. We keep both shapes verbatim rather than forcing a
# fetch, so writes can echo back exactly what the server expects (an IRI).
Reference = str | dict[str, Any]


class CitSciModel(BaseModel):
    """Pydantic base configured for the CitSci API's JSON conventions.

    * camelCase wire names are aliased to snake_case Python attributes;
    * models can be built from either alias or attribute name;
    * unknown/related fields are preserved (``extra="allow"``) so the SDK keeps working
      as the API grows new fields.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="allow",
        ser_json_timedelta="float",
    )

    def to_api_payload(self, *, exclude_none: bool = True) -> dict[str, Any]:
        """Serialize to a dict using the API's camelCase field names.

        Suitable for POST/PUT/PATCH request bodies.
        """
        return self.model_dump(by_alias=True, exclude_none=exclude_none, mode="json")
