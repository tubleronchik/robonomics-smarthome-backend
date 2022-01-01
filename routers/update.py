#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from config import KEYS
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

@router.get("/updateDevice/{deviceID}", response_model=Response)
async def send_to_datalog(deviceID: str, decryptKey: str, value: str) -> Response:
    interface = RI.RobonomicsInterface(seed=decryptKey)
    mnemonic = decryptKey
    try:
        kp = Keypair.create_from_mnemonic(mnemonic, ss58_format=32)
    except ValueError:
        return Response(code=403, message="Wrong seed!")
    kp = Keypair.create_from_mnemonic(mnemonic, ss58_format=32)
    seed = kp.seed_hex
    b = bytes(seed[0:32], "utf8")
    box = nacl.secret.SecretBox(b)
    if deviceID == KEYS["vacuum"]:
        if value == "start" or value == "pause":
            data = {"agent": f"robot_vacuum_{value}"}
        elif value == "home":
            data = {"agent": "robot_vacuum_return_to_base"}
        else:
            return "Wrong command!"
    elif deviceID == KEYS["lightbulb"]:
        if value == "off" or value == "on":
            data = {"agent": f"lightbulb_turn_{value}"}
        else:
            try:
                command = int(value)
                data = {"agent": "lightbulb_brightness", "brightness": f"{command}"}
            except ValueError:
                return "Wrong command!"
    encrypted = box.encrypt(bytes(json.dumps(data), encoding="utf8"))
    encrypted = base64.b64encode(encrypted).decode("ascii")
    interface.record_datalog(f"{encrypted}")
    return Response(code=200, message="")