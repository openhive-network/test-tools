from typing import AnyStr, Optional
from urllib.parse import urlparse


class Url:
    def __init__(self, url: str, *, protocol=""):
        parsed_url = urlparse(url, scheme=protocol)

        if not parsed_url.netloc:
            parsed_url = urlparse(f"//{url}", scheme=protocol)

        self.__protocol: str = parsed_url.scheme

        self.__address: Optional[AnyStr] = parsed_url.hostname
        if not self.__address:
            raise ValueError("Address was not specified.")

        self.__port: Optional[int] = parsed_url.port

    @property
    def protocol(self) -> str:
        return self.__protocol

    @property
    def address(self) -> str:
        return self.__address

    @property
    def port(self) -> Optional[int]:
        return self.__port

    def as_string(self, *, with_protocol=True) -> str:
        protocol_prefix = f"{self.protocol}://" if with_protocol else ""
        port_suffix = f":{self.port}" if self.port else ""

        return f"{protocol_prefix}{self.address}{port_suffix}"
