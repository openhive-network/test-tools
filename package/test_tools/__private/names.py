from __future__ import annotations

from test_tools.__private.exceptions import NameAlreadyInUseError


class Names:
    def __init__(self, parent: Names | None = None) -> None:
        self.__unique_names: set[str] = set()
        self.__next_name_numbers: dict[str, int] = {}

        self.__parent = parent

    def get_names_in_use(self) -> set[str]:
        numbered_names = set()
        for name, number_limit in self.__next_name_numbers.items():
            numbered_names.update([f"{name}{i}" for i in range(number_limit)])

        return self.__unique_names | numbered_names

    def __get_numbered_name_next_free_number(self, name: str) -> int:
        # Accessing another instance private member of the same class is not a privacy violation.
        parent_next_free_number = self.__parent.__get_numbered_name_next_free_number(name) if self.__parent else 0
        my_next_free_number = self.__next_name_numbers.get(name, 0)

        return max(parent_next_free_number, my_next_free_number)

    def register_numbered_name(self, name: str) -> str:
        self.__next_name_numbers[name] = self.__get_numbered_name_next_free_number(name)

        name_with_number = f"{name}{self.__next_name_numbers[name]}"
        self.__next_name_numbers[name] += 1

        return name_with_number

    def register_unique_name(self, name: str) -> None:
        if name in self.__unique_names:
            raise NameAlreadyInUseError(f'Name "{name}" is already in use')

        self.__unique_names.add(name)
