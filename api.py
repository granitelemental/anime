import os
import requests
from time import sleep

from flask import Flask, request

from db import upsert, Title



app = Flask("api")

api_path = "https://kitsu.io/api/edge"


@app.route("/ping")
def ping():
    return {"ok": True}

@app.route("/get_titles", methods=["GET"])
def get_titles():
    attribute = request.args.get("attribute", "categories")
    value = request.args.get("value", "adventure")
    url = api_path + f"/anime?filter[{attribute}]={value}"
    resp = requests.get(url=url).json()
    return resp


@app.route("/add_titles", methods=["POST"])
def add_titles():
    try:
        assert request.data, "there is no data"
        json = request.get_json()
        upsert(json, Title, ["id"])
    except Exception as e:
        return {"status": str(e)}
    return {"status": "ok"}


def start_app():
    app.run(host="0.0.0.0", port="8080", debug=True)

if __name__ == '__main__':
    start_app()