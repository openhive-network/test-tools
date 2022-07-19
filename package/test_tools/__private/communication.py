import json
import time
from typing import Callable

import requests
from test_tools.__private.asset import AssetBase
from test_tools.__private.exceptions import CommunicationError
from test_tools.__private.logger.logger_internal_interface import logger


class JsonEncoderWithLegacyAssets(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, AssetBase):
            return str(o)

        return super().default(o)


class JsonEncoderWithNaiAssets(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, AssetBase):
            return o.as_nai()

        return super().default(o)


def __workaround_communication_problem_with_node(send_request: Callable) -> Callable:
    """Workaround for "Unable to acquire database lock" problem in node"""
    def __implementation(*args, **kwargs):
        while True:
            try:
                return send_request(*args, **kwargs)
            except CommunicationError as exception:
                if all([
                    'error' in exception.response,
                    'message' in exception.response['error'],
                    'Unable to acquire database lock' in exception.response['error']['message']
                ]):
                    message = str(args[1])
                    logger.debug(f'Ignored "Unable to acquire database lock" error during sending request: {message}')
                    continue

                raise

    return __implementation


@__workaround_communication_problem_with_node
def request(url: str, message: dict, use_nai_assets: bool = False, max_attempts=3,
            seconds_between_attempts=0.2):
    assert max_attempts > 0

    json_encoder = JsonEncoderWithNaiAssets if use_nai_assets else JsonEncoderWithLegacyAssets
    message = bytes(json.dumps(message, cls=json_encoder), "utf-8") + b"\r\n"

    for attempts_left in reversed(range(max_attempts)):
        response = requests.post(url, data=message)
        status_code = response.status_code
        response = json.loads(response.content.decode('utf-8'))
        if status_code == 200:
            if 'result' in response:
                return response

            if 'error' in response:
                logger.debug(f'Error in response from {url}: message={message}, response={response}')
            else:
                raise CommunicationError(f'Unknown response format from {url}: ', message, response)
        else:
            logger.debug(f'Received bad status code {status_code} != 200 from {url}, '
                         f'message={message}, response={response}')

        if attempts_left > 0:
            time.sleep(seconds_between_attempts)

    raise CommunicationError(
        f'Problem occurred during communication with {url}',
        message,
        response
    )
