#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import APIRouter, Request
from pydantic import BaseModel
from substrateinterface import SubstrateInterface, Keypair
import robonomicsinterface as RI
import typing as tp

router = APIRouter()

class Response(BaseModel):
    code: int
    message: str

@router.post("/addNewDevice/", response_model=Response)
async def add_device(request: Request) -> None:
    body = await request.json()
    print(body)
    with open("config/device.py", "a") as f:
        f.write(f"{body} \n")
    return Response(code=200, message="")
    
    
    
    



"""
{
  "deviceID": "yourDeviceId",
  "deviceName": "simpleDeviceName",
  "deviceParams": [
    {
      "key": "Humidity",
      "units": "%"
    }
  ]
}
"""
