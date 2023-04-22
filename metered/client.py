# Copyright Tesserai, Inc.
# SPDX-License-Identifier: MIT

import http.client
import json
from functools import partial as _partial
from typing import Any

def partial(**kw):
    return _partial(request, **kw)

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
