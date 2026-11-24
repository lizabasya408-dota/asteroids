"""Главное окно игры: клавиатура и игровой цикл."""

from __future__ import annotations

import time
import tkinter as tk

from src import config
from src.models.game import OVER, START, AsteroidsGame, Controls
from src.renderers.space_renderer import SpaceRenderer
from src.widgets.status_bar import StatusBar

# Какая клавиша за какое действие отвечает. Используются названия
# клавиш (keysym), а не буквы, поэтому раскладка не важна.
KEYS = {"Left": "left", "Right": "right", "Up": "thrust", "space": "fire"}


class AsteroidsApp:
    """Приложение «Астероиды».

    Хранит игру ``AsteroidsGame``, рисует её через ``SpaceRenderer``,
    показывает счёт в ``StatusBar`` и следит за клавиатурой.
    """

    def __init__(self) -> None:
        """Создать окно, строку состояния, холст и игру."""
        self.root = tk.Tk()
        self.root.title("Астероиды")
        self.root.resizable(False, False)
        self.root.configure(bg=config.BAR_COLOR)

        self.bar = StatusBar(self.root)
        self.bar.pack(fill="x")
        self.canvas = tk.Canvas(self.root, width=config.WIDTH,
                                height=config.HEIGHT,
                                bg=config.SPACE_COLOR, highlightthickness=0)
        self.canvas.pack()

        self.game = AsteroidsGame()
        self.renderer = SpaceRenderer(self.canvas)
        self.controls = Controls()
        self._last = time.perf_counter()

        self.root.bind("<KeyPress>", self._on_press)
        self.root.bind("<KeyRelease>", self._on_release)
        # Если окно потеряло фокус, отпускания клавиш мы не узнаем,
        # поэтому на всякий случай «отпускаем» их все.
        self.root.bind("<FocusOut>", lambda _e: self._release_all())

    def _on_press(self, event: tk.Event) -> None:
        """Нажатие клавиши: управление, новая игра или пауза."""
        if event.keysym in KEYS:
            setattr(self.controls, KEYS[event.keysym], True)
        elif event.keysym == "Return" and self.game.state in (START, OVER):
            self.game.new_game()
        elif event.keysym == "Escape":
            self.game.toggle_pause()

    def _on_release(self, event: tk.Event) -> None:
        """Отпускание клавиши управления."""
        if event.keysym in KEYS:
            setattr(self.controls, KEYS[event.keysym], False)

    def _release_all(self) -> None:
        """Считать все клавиши управления отпущенными."""
        self.controls = Controls()

    def tick(self) -> None:
        """Один кадр: шаг игры, перерисовка, планирование следующего."""
        now = time.perf_counter()
        # Шаг времени — сколько реально прошло с прошлого кадра,
        # но не больше MAX_STEP, если программа подвисла.
        dt = min(now - self._last, config.MAX_STEP)
        self._last = now
        self.game.update(dt, self.controls)
        self.renderer.draw(self.game)
        self.bar.show(self.game.score, self.game.best, self.game.level,
                      self.game.lives)
        self.root.after(config.FRAME_DELAY_MS, self.tick)

    def run(self) -> None:
        """Запустить первый кадр и главный цикл tkinter."""
        self.tick()
        self.root.mainloop()
