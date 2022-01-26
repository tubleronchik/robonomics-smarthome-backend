#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from email import message
from config.config import KEYS
from fastapi import APIRouter
from pydantic import BaseModel
from substrateinterface import SubstrateInterface, Keypair
import nacl.secret
import base64
import robonomicsinterface as RI
import typing as tp
import ast
import json

router = APIRouter()


class Response(BaseModel):
    code: int
    message: str


@router.get("/fetchDevice/{deviceID}", response_model=Response)
async def get_data_from_datalog(deviceID: str, decryptKey: str) -> Response:
    interface = RI.RobonomicsInterface()
    mnemonic = decryptKey
    try:
        kp = Keypair.create_from_mnemonic(mnemonic, ss58_format=32)
    except ValueError:
        return Response(code=403, message="Wrong seed!")
    seed = kp.seed_hex
    b = bytes(seed[0:32], "utf8")
    box = nacl.secret.SecretBox(b)
    ids = []
    with open("config/device.py") as f:
        for device in f.readlines():
            device = ast.literal_eval(device)
            ids.append(device["deviceId"])
    record = interface.fetch_datalog(deviceID)
    try:
        decrypted = box.decrypt(base64.b64decode(record[1])).decode()
        data = ast.literal_eval(decrypted)
        device = _get_device_from_list(deviceID)
        values = []
        if device:
            for param in device["deviceParams"]:
                print(param)
                values.append(
                    {
                        "name": param["key"],
                        "value": data[param["key"]],
                        "units": param["units"],
                    }
                )
            response = {
                "id": deviceID,
                "name": device["deviceName"],
                "values": values,
                "recentlyAdded": "false",
                "imgSrc": "/devicePlaceholder.jpeg",
                "isManageable": device["isManageable"],
            }
            return Response(code=200, message=json.dumps(response))
        else:
            return Response(code=102, message="No device with such id")

    except Exception as e:
        print(f"Error during decription {e}")
        return Response(code=102, message="Could not load data")


def _get_device_from_list(id) -> tp.Optional[dict]:
    with open("config/device.py") as f:
        for device in f.readlines():
            device = ast.literal_eval(device)
            if device["deviceId"] == id:
                return device
