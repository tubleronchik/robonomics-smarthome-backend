#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import APIRouter
from pydantic import BaseModel
import typing as tp
import ast
import json

from starlette.types import Message

router = APIRouter()


class Response(BaseModel):
    code: int
    message: str


@router.get("/devices", response_model=Response)
async def read_devices() -> Response:
    devices = []
    with open("config/device.py") as f:
        for device in f.readlines():
            device = ast.literal_eval(device)
            devices.append(
                {
                    "id": device["deviceId"],
                    "name": device["deviceName"],
                    "imgSrc": "/devicePlaceholder.jpeg",
                }
            )
    return Response(code=200, message=json.dumps(devices))
