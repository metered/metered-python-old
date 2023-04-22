# Copyright Tesserai, Inc.
# SPDX-License-Identifier: MIT

import http.client
import json
import partial
from typing import Any

def __call__(host: str):
    return partial(request, host=host)

def request(host: str, query: str, variables: Dict[Any]={}, path: str = "/"):
    payload = {
      "query": query,
      "variables": variables,
    }

    conn = http.client.HTTPSConnection(host)
    conn.request("POST", path, json.dumps(payload), {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + os.environ['METERED_API_KEY']
    })
    res = conn.getresponse()
    data = res.read()
    json_data = json.loads(data.decode("utf-8"))

    if "errors" in json_data and json_data["errors"]:
      raise Exception(json.dumps(json_data["errors"]))
    
    return json_data
