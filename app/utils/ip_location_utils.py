import os

import ipinfo
import requests
from dotenv import load_dotenv
from starlette.requests import Request

load_dotenv()

token = os.getenv("token")


def get_location(ip_address: str):
    handler = ipinfo.getHandler(access_token=token)

    location = handler.getDetails(ip_address)

    if location:
        return {
            "city": location.city,
            "country": location.country_name,
            "location": location.loc
        }

    return {"city": None, "country": None, "location": None}


def get_client_ip(request: Request):
    forwarded = request.headers.get("x-forwarded-for")

    if forwarded:
        ip = forwarded.split(",")[0].strip()
    else:
        ip = request.client.host
    return ip
