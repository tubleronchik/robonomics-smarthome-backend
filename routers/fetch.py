#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
        if deviceID == KEYS["temperature"]:
            response = {
                "id": deviceID,
                "name": "Aquara temperature & humidity sensor",
                "values": [
                    {
                        "name": "Temperature",
                        "value": data["sensor.temperature_sensor_temperature"],
                        "units": "°C",
                    },
                    {
                        "name": "Humidity",
                        "value": data["sensor.temperature_sensor_humidity"],
                        "units": "%",
                    }
                ],
                "recentlyAdded": "false",
                "imgSrc": "/devicePlaceholder.jpeg",
                "isManageable": "false",
            }
        elif deviceID == KEYS["vacuum"]:
            response = {
                "id": deviceID,
                "name": "Robot Vacuum",
                "values": [
                    {"name": "State", "value": data["vacuum.robot_vacuum"], "units": ""}
                ],
                "recentlyAdded": "false",
                "imgSrc": "/devicePlaceholder.jpeg",
                "isManageable": "true",
            }
        elif deviceID == KEYS["lightbulb"]:
            response = {
                "id": deviceID,
                "name": "Lightbulb",
                "values": [
                    {"name": "State", "value": data["light.lightbulb"], "units": ""}
                ],
                "recentlyAdded": "false",
                "imgSrc": "/devicePlaceholder.jpeg",
                "isManageable": "true",
            }
        elif any(deviceID for id in ids):
            with open("config/device.py") as f:
                for device in f.readlines():
                    device = ast.literal_eval(device)
                    if device["deviceId"] == deviceID:
                        break
                values = []
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
                    "isManageable": "false",
                }

        return Response(code=200, message=json.dumps(response))

    except Exception as e:
        print(f"Error during decription {e}")
        return Response(code=102, message="Could not load data")
