# mypy: ignore-errors
# ruff: noqa
# file for deletion after cli_wallet deprecation
from collections.abc import Callable
from datetime import datetime
import json
import time
from typing import Any, Callable

import requests

from schemas.fields.assets import AssetBase
from schemas.fields.json_string import JsonString
from schemas._preconfigured_base_model import PreconfiguredBaseModel
from schemas.operations.representations import LegacyRepresentation
from beekeepy.exceptions import CommunicationError
from loguru import logger
from beekeepy.interfaces import HttpUrl
from wax.helpy import Time


class CommonJsonEncoder(json.JSONEncoder):
    def default(self, o: Any):
        if isinstance(o, datetime):
            return Time.serialize(o)
        if isinstance(o, JsonString):
            return o.serialize()
        if isinstance(o, PreconfiguredBaseModel):
            return o.shallow_dict()

        return super().default(o)


class LegacyJsonEncoder(CommonJsonEncoder):
    def default(self, o: Any):
        if isinstance(o, AssetBase):
            return o.as_legacy()
        if isinstance(o, LegacyRepresentation):
            return (o[0], o[1].dict(by_alias=True, exclude_none=True))
        return super().default(o)


class Hf26JsonEncoder(CommonJsonEncoder):
    def default(self, o: Any):
        if isinstance(o, AssetBase):
            return o.as_nai()
        return super().default(o)


def __workaround_communication_problem_with_node(send_request: Callable) -> Callable:
    """Workaround for "Unable to acquire database/forkdb lock" problem in node"""

    def __implementation(*args, **kwargs):
        while True:
            try:
                return send_request(*args, **kwargs)
            except CommunicationError as exception:
                if "Unable to acquire database lock" in str(exception) or "Unable to acquire forkdb lock" in str(
                    exception
                ):
                    message = str(args[1])
                    logger.debug(
                        f'Ignored "Unable to acquire {"database" if "database" in str(exception) else "forkdb"} lock" error during sending request: {message}'
                    )
                    continue

                raise

    return __implementation


@__workaround_communication_problem_with_node
def request(url: str, message: dict, use_nai_assets: bool = False, max_attempts=3, seconds_between_attempts=0.2):
    assert max_attempts > 0

    json_encoder = LegacyJsonEncoder if not use_nai_assets else Hf26JsonEncoder
    body = json.dumps(message, cls=json_encoder)
    headers = {"Content-Type": "application/json"}
    decoded_content = "<NO RESPONSE>"

    for attempts_left in reversed(range(max_attempts)):
        response = requests.post(url, data=body, headers=headers)
        status_code = response.status_code
        try:
            decoded_content = response.content.decode("utf-8")
        except UnicodeDecodeError as exception:
            logger.error(
                "An error occurred while decoding the response content.\n\n"
                "Response content:\n"
                f"{response.content}"
            )  # fmt: skip
            raise exception

        response = json.loads(decoded_content)

        if status_code == 200:
            if "result" in response:
                return response

            if "error" in response:
                logger.debug(f"Error in response from {url}: message={body}, response={response}")
            else:
                raise CommunicationError(
                    url=HttpUrl(url), request=body, response=f"Unknown response format from {url}: "
                )
        else:
            logger.debug(
                f"Received bad status code {status_code} != 200 from {url}, message={body}, response={response}"
            )

        if attempts_left > 0:
            time.sleep(seconds_between_attempts)

    raise CommunicationError(url=HttpUrl(url), request=body, response=decoded_content)
