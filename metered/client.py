# Copyright Tesserai, Inc.
# SPDX-License-Identifier: MIT

import http.client
import json
from functools import partial as _partial
from typing import Any

class GraphQLClient:
  def __init__(self, host: str, path: str = "/") -> None:
    self._host = host
    self._path = path

  def request(self, query: str, variables: Dict[Any]={}):
    payload = {
      "query": query,
      "variables": variables,
    }

    conn = http.client.HTTPSConnection(self._host)
    conn.request("POST", self._path, json.dumps(payload), {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + os.environ['METERED_API_KEY']
    })
    res = conn.getresponse()
    data = res.read()
    json_data = json.loads(data.decode("utf-8"))

    if "errors" in json_data and json_data["errors"]:
      raise Exception(json.dumps(json_data["errors"]))
    
    return json_data
