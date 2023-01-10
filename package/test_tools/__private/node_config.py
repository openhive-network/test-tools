import re

from test_tools.__private.node_config_attributes import NodeConfigAttributes


class NodeConfig(NodeConfigAttributes):
    # pylint: disable=too-many-instance-attributes
    # Config contains so many entries and all of them must be defined here

    def __is_initialization_stage(self):
        return "_initialization_stage" in self.__dict__

    def __setattr__(self, key, value):
        if self.__is_initialization_stage():
            self.__entries[key] = value
        else:
            try:
                self.__entries[key].set_value(value)
            except KeyError as error:
                raise KeyError(f'There is no such entry like "{key}"') from error

    def __getattr__(self, key):
        try:
            return self.__entries[key].get_value()
        except KeyError as error:
            raise KeyError(f'There is no such entry like "{key}"') from error

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise Exception("Comparison with unsupported type")
        return not self.get_differences_between(other, stop_at_first_difference=True)

    def __ne__(self, other):
        return not self == other

    def get_differences_between(self, other, stop_at_first_difference=False):
        differences = {}
        for name_of_entry in self.__entries:
            mine = getattr(self, name_of_entry)
            his = getattr(other, name_of_entry)

            if mine != his:
                differences[name_of_entry] = (mine, his)
                if stop_at_first_difference:
                    break

        return differences

    def write_to_lines(self):
        def should_skip_entry(entry):
            value = entry.get_value()
            if value is None:
                return True

            if isinstance(value, list) and not value:
                return True

            return False

        file_entries = []
        for key, entry in self.__entries.items():
            if should_skip_entry(entry):
                continue

            values = entry.serialize_to_text()
            values = values if isinstance(values, list) else [values]
            for value in values:
                file_entries.append(f"{key.replace('_', '-')} = {value}")

        return file_entries

    def write_to_file(self, file_path):
        self.validate()

        with open(file_path, "w", encoding="utf-8") as file:
            file.write("\n".join(self.write_to_lines()))

    def validate(self):
        self.__assert_no_plugins_duplicates()

    def __assert_no_plugins_duplicates(self):
        plugin_occurences = {plugin: 0 for plugin in self.plugin}
        for plugin in self.plugin:
            plugin_occurences[plugin] += 1

        duplicated_plugins = [plugin for plugin, occurences in plugin_occurences.items() if occurences > 1]
        if duplicated_plugins:
            raise RuntimeError(
                f"Following plugins are included more than once:\n"
                f"{duplicated_plugins}\n"
                f"\n"
                f"Remove places from code where you added them manually."
            )

    def load_from_lines(self, lines):
        assert isinstance(lines, list)

        def parse_entry_line(line):
            result = re.match(r"^\s*([\w\-]+)\s*=\s*(.*?)\s*$", line)
            return (result[1], result[2]) if result is not None else None

        def is_entry_line(line):
            return parse_entry_line(line) is not None

        self.__clear_values()
        for line in lines:
            if is_entry_line(line):
                key, value = parse_entry_line(line)

                self.__check_if_key_from_file_is_valid(key)

                if value != "":
                    self.__entries[key.replace("-", "_")].parse_from_text(value)

    def __check_if_key_from_file_is_valid(self, key_to_check):
        """Keys from file have hyphens instead of underscores"""
        valid_keys = [key.replace("_", "-") for key in self.__entries]

        if key_to_check not in valid_keys:
            raise KeyError(f'Unknown config entry name: "{key_to_check}".')

    def __clear_values(self):
        for entry in self.__entries.values():
            entry.clear()

    def load_from_file(self, file_path):
        with open(file_path, encoding="utf-8") as file:
            self.load_from_lines(file.readlines())
