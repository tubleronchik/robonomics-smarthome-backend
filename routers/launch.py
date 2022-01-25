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


@router.post("/launchDevice", response_model=Response)
async def launch_device(request: Request) -> Response:
    body = await request.json()
    try:
        interface = RI.RobonomicsInterface(seed=body["seed"])
    except ValueError:
        return Response(code=403, message="Wrong seed!")
    status = body["status"].lower() == "true"
    interface.send_launch(target_address=body["id"], toggle=status)
    return Response(code=200, message="")
    
