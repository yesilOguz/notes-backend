from pydantic import BaseModel, ConfigDict
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from pydantic_core.core_schema import ValidationInfo

from bson.errors import InvalidId
from bson import ObjectId
from typing import Any


class ObjectIdPydanticAnnotation:
    @classmethod
    def validate_object_id(cls, v: Any, handler) -> ObjectId:
        if isinstance(v, ObjectId):
            return v

        s = handler(v)
        if ObjectId.is_valid(s):
            return ObjectId(s)
        else:
            raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, _handler) -> core_schema.CoreSchema:
        assert source_type is ObjectId
        return core_schema.no_info_wrap_validator_function(
            cls.validate_object_id,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema, handler) -> JsonSchemaValue:
        return handler(core_schema.str_schema())


class OID(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, info: ValidationInfo):
        try:
            return ObjectId(str(v))
        except InvalidId:
            raise ValueError("Not a valid ObjectId")


class NotesBaseModel(BaseModel):
    model_config = ConfigDict(
        use_enum_values=True,
        arbitrary_types_allowed=True,
        json_encoders={
            ObjectId: lambda oid: str(oid),
        })

    @classmethod
    def from_mongo(cls, data: dict):
        if not data:
            return data

        id = data.pop('_id', None)

        return cls(**dict(data, id=id))

    @classmethod
    def from_json(cls, data: dict):
        if not data:
            return data

        return cls(**dict(data, id=id))

    def to_mongo(self, **kwargs):
        exclude_unset = kwargs.pop('exclude_unset', True)
        by_alias = kwargs.pop('by_alias', True)
        exclude_none = kwargs.pop('exclude_none', False)

        parsed = self.model_dump(
            exclude_unset=exclude_unset,
            by_alias=by_alias,
            exclude_none=exclude_none,
            **kwargs,
        )

        if '_id' not in parsed and 'id' in parsed:
            parsed['_id'] = parsed.pop('id')

        return parsed

    def to_json(self):
        return self.model_dump(mode='json')
