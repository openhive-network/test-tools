import pytest

import test_tools as tt
from test_tools.__private.scope import current_scope


# @pytest.fixture(autouse=True, scope="module")
# def set_logger():
#     tt.logger.set_level(0)


def test_bar():
    x = current_scope
    tt.logger.set_level(0)
    tt.logger.debug('debug in test')
    tt.logger.info('info in test')
    tt.logger.warning('warning in test')
    tt.logger.error('error in test')
    tt.logger.critical('critical in test')


def test_zoo():
    x = current_scope
    # tt.logger.set_level(tt.logger.level.CRITICAL)
    tt.logger.debug('debug in test')
    tt.logger.info('info in test')
    tt.logger.warning('warning in test')
    tt.logger.error('error in test')
    tt.logger.critical('critical in test')