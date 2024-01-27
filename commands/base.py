# https://www.kapresoft.com/java/2023/12/03/java-command-pattern.html

from abc import ABC, abstractmethod


class ICommand(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass
    
    @abstractmethod
    def undo(self) -> None:
        pass


class CommandHistory:
    def __init__(self) -> None:
        self._commands = []
    
    def add(self, command: ICommand) -> None:
        self._commands.append(command)
    
    def pop(self) -> ICommand:
        return self._commands.pop()
    
    def __len__(self) -> int:
        return len(self._commands)
    

class Invoker:
    def __init__(self) -> None:
        self._history = CommandHistory()
    
    def execute(self, command: ICommand) -> None:
        command.execute()
        self._history.add(command)
    
    def undo(self) -> None:
        command = self._history.pop()
        command.undo()

    def undo_all(self) -> None:
        try:
            while len(self._history) > 0:
                self.undo()
        except Exception as e:
            print("Error al deshacer el proceso:", e)


class CompositeCommand(ICommand):
    def __init__(self) -> None:
        self._commands = []
        self._history = CommandHistory()
    
    def add(self, command: ICommand) -> None:
        self._commands.append(command)
    
    def execute(self) -> None:
        for command in self._commands:
            command.execute()
            self._history.add(command)

    def undo(self) -> None:
        while len(self._history) > 0:
            command = self._history.pop()
            command.undo()
