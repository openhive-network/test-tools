import os


class NodeApiCallProxy:
    def __init__(self, node, method, params=None, jsonrpc='2.0', id_=1):
        self.__node = node
        self.__message = {
            'method': method,
            'params': params,
            'jsonrpc': jsonrpc,
            'id': id_,
        }

    def __call__(self, *args, only_result: bool = True, **kwargs):
        self.__message['params'] = self._prepare_params(*args, **kwargs)
        response = self.__node.send(
            self.__message['method'],
            self.__message['params'],
            jsonrpc=self.__message['jsonrpc'],
            id_=self.__message['id'],
            only_result=only_result,
        )

        def schemas_should_be_automatically_validated() -> bool:
            should_validate = os.getenv('TEST_TOOLS_VALIDATE_RESPONSE_SCHEMAS', default='FALSE')
            return should_validate.lower() == 'true' or should_validate == '1'

        if schemas_should_be_automatically_validated():
            from schemas.get_schema import get_schema  # pylint: disable=import-outside-toplevel, import-error
            get_schema(self.__message['method']).validate(response)

        return response

    @staticmethod
    def _prepare_params(*args, **kwargs):
        if args:
            raise ValueError(
                f'You tried to send parameters which requires names without names.\n'
                f'\n'
                f'Following arguments requires names, but names were missing:\n'
                f'  {", ".join([str(arg) for arg in args])}\n'
                f'\n'
                f'Use following syntax:\n'
                f'  node.api.database.list_witnesses(start=None, limit=100, order=\'by_name\')\n'
                f'instead of:\n'
                f'  node.api.database.list_witnesses(None, 100, \'by_name\')'
            )

        return kwargs


class ApiBase:
    _NodeApiCallProxyType = NodeApiCallProxy

    def __init__(self, node, name):
        self.__name = name
        self.__node = node

    def __getattr__(self, item):
        return self._NodeApiCallProxyType(self.__node, f'{self.__name}.{item}')

    def _send(self, method, params=None, jsonrpc='2.0', id_=1):
        return self.__node.send(f'{self.__name}.{method}', params, jsonrpc=jsonrpc, id_=id_)
