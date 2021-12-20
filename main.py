#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from config import KEYS
from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from substrateinterface import SubstrateInterface, Keypair
import nacl.secret
import base64
import robonomicsinterface as RI
import typing as tp
import ast


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def datalog_update(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})


@app.get("/fetchDevice/{deviceID}")
async def get_data_from_datalog(deviceID: str, decryptKey: str) -> tp.Dict[str, tp.Any]:
    interface = RI.RobonomicsInterface()
    print(decryptKey)
    mnemonic = decryptKey

    kp = Keypair.create_from_mnemonic(mnemonic, ss58_format=32)
    seed = kp.seed_hex
    b = bytes(seed[0:32], "utf8")
    box = nacl.secret.SecretBox(b)
    pub_key = deviceID
    record = interface.fetch_datalog(pub_key)
    try:
        decrypted = box.decrypt(base64.b64decode(record["payload"]))
        data = ast.literal_eval(decrypted)
        if deviceID == KEYS["temperature"]:
            response = {
                "id": deviceID,
                "name": "Aquara temperature & humidity sensor",
                "values": [
                    {
                        "name": "Temperature",
                        "value": data["temperature_sensor_temperature"],
                        "units": "°C",
                    },
                    {
                        "name": "Humidity",
                        "value": data["temperature_sensor_humidity"],
                        "units": "%",
                    },
                    {
                        "name": "Battery",
                        "value": data["temperature_sensor_battery"],
                        "units": "%",
                    },
                ],
                "recentlyAdded": "false",
                "imgSrc": "/devicePlaceholder.jpeg",
                "isManageable": "false",
            }
        elif deviceID == "4Hd5Zkcu1qubGBi6Lxn59eoZ88osfN53TzxXTVTKUBaEeAuM":
            response = {
                "id": deviceID,
                "name": "Robot Vacuum",
                "values": [{"name": "State", "value": data["state"], "units": ""}],
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
        print(response)
        return response

    except Exception as e:
        print(f"Error during decription {e}")


@app.get("/updateDevice/{deviceID}")
async def send_to_datalog(deviceID: str, decryptKey: str, value: str) -> tp.Optional[str]:
    interface = RI.RobonomicsInterface()
    mnemonic = decryptKey
    kp = Keypair.create_from_mnemonic(mnemonic, ss58_format=32)
    seed = kp.seed_hex
    b = bytes(seed[0:32], "utf8")
    box = nacl.secret.SecretBox(b)

    if deviceID == KEYS["vacuum"]:
        if value == "start" or value == "pause":
            data = {"agent": f"robot_vacuum_{value}"}
        elif value == "home":
            data = {"agent": "robot_vacuum_return_to base"}
        else:
            return "Wrong command!"
    elif deviceID == KEYS["lightbulb"]:
        if value == "off" or value == "on":
            data = {"agent": f"lightbulb_turn_{value}"}
        else:
            try:
                command = int(value)
                data = {"agent": "lightbulb_brightness", "brightness": f"{value}"}
            except ValueError:
                return "Wrong command!"

    encrypted = box.encrypt(bytes(str(data), encoding="utf8"))
    encrypted = base64.b64encode(encrypted).decode("ascii")
    interface.record_datalog(f"{encrypted}")
