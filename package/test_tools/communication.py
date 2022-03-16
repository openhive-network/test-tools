import json
import time

import requests

from test_tools.exceptions import CommunicationError
from test_tools.private.asset import AssetBase
from test_tools.private.logger.logger_internal_interface import logger


class CustomJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, AssetBase):
            return str(o)

        return super().default(o)


def request(url: str, message: dict, max_attempts=3, seconds_between_attempts=0.2):
    assert max_attempts > 0

    message = bytes(json.dumps(message, cls=CustomJsonEncoder), "utf-8") + b"\r\n"

    attempts_left = max_attempts
    while attempts_left > 0:
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
        attempts_left -= 1

    raise CommunicationError(
        f'Problem occurred during communication with {url}',
        message,
        response
    )
