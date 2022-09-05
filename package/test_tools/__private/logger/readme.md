# Class hierarchy

Classes are organized in following hierarchy:
```plantuml
@startuml
    class "LoggerWrapper" as wrapper
    class "LoggerInterfaceBase" as base {
        + debug(message: str): None
        + info(message: str): None
        + warning(message: str): None
        + error(message: str): None
        + critical(message: str): None
    }
    class "LoggerInternalInterface" as internal_handle
    class "LoggerUserInterface" as user_handle

    internal_handle --|> base
    user_handle --|> base
    base *-- "1" wrapper
@enduml
```

# Sequence diagram of logging a message

```python
import test_tools as tt


def test_something():
    tt.logger.info("Example")
```

Above log registration is handled by following sequence of actions:
```plantuml
@startuml
    participant test_something as test
    participant "tt.logger\n<i>LoggerUserInterface</i>" as handler
    participant "tt.logger.__instance\n<i>LoggerWrapper</i>" as wrapper
    participant "tt.logger.__instance.internal_logger\n<i>logging.Logger</i>" as logging

    test --> handler: info("Example")
    activate handler
        handler --> wrapper: info("Example", stacklevel=1)
        activate wrapper
            wrapper --> logging: info("Example", stacklevel=3)
            activate logging
                wrapper <-- logging
            deactivate logging
            handler <-- wrapper
        deactivate wrapper
    test <-- handler
    deactivate handler
@enduml
```
