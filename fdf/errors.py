"""Исключения приложения."""


class FdfError(Exception):
    """Базовый класс ошибок приложения FdF."""


class MapFormatError(FdfError):
    """Ошибка в файле карты с позицией, отсчитываемой от единицы."""

    def __init__(self, line: int, column: int, message: str) -> None:
        self.line = line
        self.column = column
        super().__init__(f"строка {line}, колонка {column}: {message}")
