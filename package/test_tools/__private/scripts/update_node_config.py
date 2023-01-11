from pathlib import Path
import subprocess

import test_tools as tt
from test_tools.__private import node_config_attributes
from test_tools.__private.node_option import NodeOption


class NodeConfigGenerator:
    @staticmethod
    def convert_type(name: str, type: str, multitoken: bool):
        if type == "string" or type == "ubyte" or type == "ushort" or type == "uint" or type == "ulong":
            return "=String()"
        elif type == "byte" or type == "short" or type == "int" or type == "long":
            return "=Integer()"
        elif type == "path":
            return "=StringQuoted()"
        elif type == "string_array":
            if multitoken:
                if name == "witness":  # This is an exception: witnesses are given with quotes
                    return "=List(StringQuoted, single_line=False)"
                else:
                    return "=List(String, single_line=False)"
            else:
                return "=List(String)"
        elif type == "bool":
            return "=Boolean()"
        else:
            assert False

    @staticmethod
    def generate(node: NodeOption):
        assert node.value is not None

        _result = "        "
        _result += "self."

        _result += node.name.replace("-", "_")
        _result += NodeConfigGenerator.convert_type(node.name, node.value.value_type, node.value.multitoken)
        if len(node.description) > 0:
            _result += "#"
            _result += node.description

        _result += "\n"
        return _result

    @staticmethod
    def extend_source_code(code_with_set_of_attributes: str):
        _extended_code_with_set_of_attributes = '"""Begin of machine generated code"""\n'

        _extended_code_with_set_of_attributes += """
# pylint: disable=line-too-long too-many-instance-attributes too-many-statements too-few-public-methods

from test_tools.__private.node_config_entry_types import (
    Boolean, Integer, List, String, StringQuoted
)

class NodeConfigAttributes:
    \"\"\"Stores all attributes.\"\"\"

    def __init__(self):
        self.__enter_initialization_stage()
        self.__initialize()
        self.__exit_initialization_stage()

    def __enter_initialization_stage(self):
        super().__setattr__("_initialization_stage", None)

    def __exit_initialization_stage(self):
        super().__delattr__("_initialization_stage")

    def __initialize(self):

        super().__setattr__(f"_{self.__class__.__name__}__entries", {})

"""
        _extended_code_with_set_of_attributes += code_with_set_of_attributes
        _extended_code_with_set_of_attributes += "\n# End of machine generated code"

        return _extended_code_with_set_of_attributes

    @staticmethod
    def run(node_options):
        _code_with_set_of_attributes = ""

        for node_option in node_options:
            _code_with_set_of_attributes += NodeConfigGenerator.generate(node_option)

        return NodeConfigGenerator.extend_source_code(_code_with_set_of_attributes)

    @staticmethod
    def write(code_with_set_of_attributes: str, dest_file_name: str):
        f = Path(dest_file_name)
        f.write_text(code_with_set_of_attributes)


if __name__ == "__main__":
    node = tt.RawNode()
    cfg_options = node.config_options()

    _code = NodeConfigGenerator.run(cfg_options)
    NodeConfigGenerator.write(_code, node_config_attributes.__file__)

    # Format generated code, (because code generated by above script do not follow our formatter code style).
    subprocess.run(["black", node_config_attributes.__file__], check=False)
