"""Панель над игровым полем: счёт, рекорд, уровень и жизни."""

from __future__ import annotations

import tkinter as tk

from src import config


class StatusBar(tk.Frame):
    """Строка состояния игры.

    Состоит из нескольких надписей ``tk.Label``. Метод ``show``
    меняет текст только когда значение действительно изменилось,
    чтобы не перерисовывать надписи 60 раз в секунду.
    """

    FIELDS = (("score", "Счёт"), ("best", "Рекорд"),
              ("level", "Уровень"), ("lives", "Жизни"))

    def __init__(self, master: tk.Misc) -> None:
        """Создать надписи для каждого показателя."""
        super().__init__(master, bg=config.BAR_COLOR, padx=14, pady=8)
        self._labels: dict[str, tk.Label] = {}
        self._values: dict[str, int] = {}
        for key, title in self.FIELDS:
            tk.Label(self, text=title, bg=config.BAR_COLOR,
                     fg=config.MUTED_TEXT_COLOR,
                     font=("Helvetica", 12)).pack(side="left",
                                                  padx=(0, 6))
            label = tk.Label(self, text="0", width=6, anchor="w",
                             bg=config.BAR_COLOR, fg=config.TEXT_COLOR,
                             font=("Helvetica", 16, "bold"))
            label.pack(side="left", padx=(0, 18))
            self._labels[key] = label
        tk.Label(self, text="Esc - пауза",
                 bg=config.BAR_COLOR, fg=config.MUTED_TEXT_COLOR,
                 font=("Helvetica", 11)).pack(side="right")

    def show(self, score: int, best: int, level: int, lives: int) -> None:
        """Показать текущие значения."""
        values = {"score": score, "best": best, "level": level,
                  "lives": lives}
        for key, value in values.items():
            if self._values.get(key) != value:
                self._labels[key].config(text=str(value))
                self._values[key] = value
