from fastapi import FastAPI, Depends, HTTPException
import etcd3
from pydantic import BaseModel, Field
from typing import Dict, Optional, List
import json
from enum import Enum
import os

ETCD_HOST = os.environ.get("ETCD_HOST", "localhost")
ETCD_PORT = os.environ.get("ETCD_PORT", 2379)

app = FastAPI(
    title="Schema Registry",
    description="Manages Schemata for Data Files backed by an etcd cluster",
)


class TypeEnum(str, Enum):
    str = "str"
    int = "int"
    float = "float"
    bool = "bool"


class SchemaField(BaseModel):
    name: str
    type: TypeEnum
    format: Optional[str]
    nullable: bool = Field(default=True)


class SchemaData(BaseModel):
    type: str
    fields: List[SchemaField]


class SchemaModel(BaseModel):
    name: str
    version: Optional[int]
    data: SchemaData


def get_db():
    client = etcd3.client(host=ETCD_HOST, port=ETCD_PORT)
    try:
        yield client
    finally:
        client.close()


@app.get(
    "/schema/{s}",
    response_model=SchemaModel,
    responses={"404": {"description": "Schema not found"}},
)
def get_schema(s: str, cl=Depends(get_db)):
    val, meta = cl.get(f"/schema/{s}")
    if val is None:
        raise HTTPException(status_code=404)
    return SchemaModel(name=s, version=meta.version, data=json.loads(val))


@app.post("/schema", status_code=201)
def put_schema(schema: SchemaModel, cl=Depends(get_db)):
    cl.put(f"/schema/{schema.name}", json.dumps(schema.data.dict()))
    return dict(result="OK")
