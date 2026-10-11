#!/usr/bin/env python
# coding: utf-8

import dashscope
import json
from http import HTTPStatus

text = "我叫陈永达"

resp = dashscope.TextEmbedding.call(
    model="text-embedding-v4",
    input=text,
)

if resp.status_code == HTTPStatus.OK:
    result = {
        "status_code": resp.status_code,
        "request_id": getattr(resp, "request_id", ""),
        "code": getattr(resp, "code", ""),
        "message": getattr(resp, "message", ""),
        "output": resp.output,
        "usage": resp.usage,
    }
    print(json.dumps(result, ensure_ascii=False, indent=4))
else:
    print(resp)
