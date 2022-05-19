#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from substrateinterface import Keypair, KeypairType
from fastapi import APIRouter
from pydantic import BaseModel
import nacl.secret
import robonomicsinterface as RI
import typing as tp
import ast
import json
import nacl.bindings
import nacl.public

router = APIRouter()


class Response(BaseModel):
    code: int
    message: str


def decrypt_message(
    message: str, user_keypair: Keypair, sensor_public_address: str
) -> bytes:
    private_key = nacl.bindings.crypto_sign_ed25519_sk_to_curve25519(
        user_keypair.private_key + user_keypair.public_key
    )
    recipient = nacl.public.PrivateKey(private_key)
    curve25519_public_key = nacl.bindings.crypto_sign_ed25519_pk_to_curve25519(
        sensor_public_address
    )
    sender = nacl.public.PublicKey(curve25519_public_key)
    return nacl.public.Box(recipient, sender).decrypt(message)


@router.get("/fetchDevice/{deviceID}", response_model=Response)
async def get_data_from_datalog(deviceID: str, decryptKey: str) -> Response:
    interface = RI.RobonomicsInterface()
    try:
        kp = Keypair.create_from_mnemonic(
            decryptKey,
            crypto_type=KeypairType.ED25519,
        )
    except ValueError:
        return Response(code=403, message="Wrong seed!")
    ids = []
    with open("config/device.py") as f:
        for device in f.readlines():
            device = ast.literal_eval(device)
            ids.append(device["deviceId"])
    record = interface.fetch_datalog(deviceID)
    try:
        decrypted_message = decrypt_message(message=record[1], keypair=kp)
        data = ast.literal_eval(decrypted_message)
        device = _get_device_from_list(deviceID)
        values = []
        if device:
            for param in device["deviceParams"]:
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
