from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from plugins.base import Plugin


class RecordsInput(BaseModel):
    records: List[Dict[str, Any]] = Field(default_factory=list)


class PickFieldInput(BaseModel):
    records: List[Dict[str, Any]]
    field: str


class PickFieldOutput(BaseModel):
    values: List[Any]


class PickFieldPlugin(Plugin):
    name = "records.pick_field"
    version = "1.0.0"
    description = "Extracts a field from each record."
    input_model = PickFieldInput
    output_model = PickFieldOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        field = payload["field"]
        return {"values": [record.get(field) for record in payload["records"]]}


class FilterRecordsInput(BaseModel):
    records: List[Dict[str, Any]]
    field: str
    equals: Any


class FilterRecordsOutput(BaseModel):
    records: List[Dict[str, Any]]


class FilterRecordsPlugin(Plugin):
    name = "records.filter_equals"
    version = "1.0.0"
    description = "Keeps records where field equals a value."
    input_model = FilterRecordsInput
    output_model = FilterRecordsOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        field = payload["field"]
        expected = payload["equals"]
        kept = [record for record in payload["records"] if record.get(field) == expected]
        return {"records": kept}


class SortRecordsInput(BaseModel):
    records: List[Dict[str, Any]]
    field: str
    descending: bool = False


class SortRecordsPlugin(Plugin):
    name = "records.sort_by"
    version = "1.0.0"
    description = "Sorts records by a field."
    input_model = SortRecordsInput
    output_model = FilterRecordsOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        field = payload["field"]
        sorted_records = sorted(
            payload["records"],
            key=lambda record: record.get(field),
            reverse=payload.get("descending", False),
        )
        return {"records": sorted_records}


class ProjectInput(BaseModel):
    records: List[Dict[str, Any]]
    fields: List[str]


class ProjectOutput(BaseModel):
    records: List[Dict[str, Any]]


class ProjectPlugin(Plugin):
    name = "records.project"
    version = "1.0.0"
    description = "Projects records to a subset of fields."
    input_model = ProjectInput
    output_model = ProjectOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        fields = payload["fields"]
        projected = [{field: record.get(field) for field in fields} for record in payload["records"]]
        return {"records": projected}


class GroupRecordsInput(BaseModel):
    records: List[Dict[str, Any]]
    field: str


class GroupRecordsOutput(BaseModel):
    groups: Dict[str, List[Dict[str, Any]]]


class GroupRecordsPlugin(Plugin):
    name = "records.group_by"
    version = "1.0.0"
    description = "Groups records by a field value."
    input_model = GroupRecordsInput
    output_model = GroupRecordsOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        groups: Dict[str, List[Dict[str, Any]]] = {}
        for record in payload["records"]:
            key = str(record.get(payload["field"], "unknown"))
            groups.setdefault(key, []).append(record)
        return {"groups": groups}


class CoalesceInput(BaseModel):
    record: Dict[str, Any]
    fields: List[str]
    default: Optional[Any] = None


class CoalesceOutput(BaseModel):
    value: Any


class CoalescePlugin(Plugin):
    name = "records.coalesce"
    version = "1.0.0"
    description = "Returns the first non-null field value."
    input_model = CoalesceInput
    output_model = CoalesceOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        record = payload["record"]
        for field in payload["fields"]:
            if field in record and record[field] is not None:
                return {"value": record[field]}
        return {"value": payload.get("default")}


def register_record_plugins(registry) -> None:
    registry.register(PickFieldPlugin(), capabilities=["records:pick"])
    registry.register(FilterRecordsPlugin(), capabilities=["records:filter"])
    registry.register(SortRecordsPlugin(), capabilities=["records:sort"])
    registry.register(ProjectPlugin(), capabilities=["records:project"])
    registry.register(GroupRecordsPlugin(), capabilities=["records:group"])
    registry.register(CoalescePlugin(), capabilities=["records:coalesce"])
