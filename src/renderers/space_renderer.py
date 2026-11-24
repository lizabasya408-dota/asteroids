"""Отрисовка космоса, корабля, астероидов и надписей."""

from __future__ import annotations

import random
import time
import tkinter as tk

from src import config
from src.models.game import OVER, PAUSED, START, AsteroidsGame
from src.models.ship import Ship

LEVEL_BANNER_TIME = 1.6


def hex_to_rgb(color: str) -> tuple[int, int, int]:
    """Перевести цвет ``#rrggbb`` в три числа от 0 до 255."""
    return tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))


def blend(color: str, background: str, alpha: float) -> str:
    """Смешать цвет с фоном: alpha = 1 — цвет, alpha = 0 — только фон.

    Так рисуются гаснущие обломки: холст tkinter не умеет
    полупрозрачность, поэтому цвет постепенно сдвигается к цвету космоса.
    """
    mixed = (round(b + (c - b) * alpha)
             for c, b in zip(hex_to_rgb(color), hex_to_rgb(background)))
    return "#{:02x}{:02x}{:02x}".format(*mixed)


class SpaceRenderer:
    """Рисует один кадр игры на холсте.

    Звёзды рисуются один раз. Всё остальное помечено тегом
    ``"dynamic"`` и на каждом кадре стирается и рисуется заново:
    объектов на экране немного, поэтому это быстро и просто.
    """

    def __init__(self, canvas: tk.Canvas) -> None:
        """Нарисовать звёздное небо."""
        self.canvas = canvas
        self._level = 0
        self._level_shown = 0.0
        rng = random.Random(5)
        for _ in range(120):
            x = rng.uniform(0, config.WIDTH)
            y = rng.uniform(0, config.HEIGHT)
            size = rng.choice((1, 1, 1, 2))
            shine = rng.uniform(0.3, 1.0)
            canvas.create_oval(x, y, x + size, y + size, width=0,
                               fill=blend(config.STAR_COLOR,
                                          config.SPACE_COLOR, shine))

    def draw(self, game: AsteroidsGame) -> None:
        """Нарисовать текущее состояние игры ``game``."""
        self.canvas.delete("dynamic")
        for rock in game.asteroids:
            self.canvas.create_polygon(
                rock.outline(), outline=config.ASTEROID_COLOR,
                fill="", width=2, tags="dynamic")
        for bullet in game.bullets:
            self._dot(bullet.x, bullet.y, 2.5, config.BULLET_COLOR)
        for piece in game.debris:
            self._dot(piece.x, piece.y, 1.6,
                      blend(config.DEBRIS_COLOR, config.SPACE_COLOR,
                            piece.fade))
        if game.ship:
            self._draw_ship(game.ship)
        self._draw_messages(game)

    def _dot(self, x: float, y: float, r: float, color: str) -> None:
        """Нарисовать маленький кружок радиуса ``r``."""
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=color,
                                width=0, tags="dynamic")

    def _draw_ship(self, ship: Ship) -> None:
        """Нарисовать корабль и пламя двигателя.

        Пока корабль защищён после появления, он мигает: виден
        в чётные восьмые доли секунды и не виден в нечётные.
        """
        if ship.invulnerable > 0 and int(ship.invulnerable * 8) % 2:
            return
        if ship.thrusting:
            # Пламя — треугольник за кормой, длина которого случайно
            # «дрожит», как у настоящего огня.
            dx, dy = ship.direction()
            length = ship.radius * random.uniform(1.0, 1.7)
            back_x = ship.x - dx * ship.radius * 0.45
            back_y = ship.y - dy * ship.radius * 0.45
            side_x, side_y = -dy * ship.radius * 0.35, dx * ship.radius * 0.35
            self.canvas.create_polygon(
                back_x + side_x, back_y + side_y,
                back_x - dx * length, back_y - dy * length,
                back_x - side_x, back_y - side_y,
                fill=config.FLAME_COLOR, outline="", tags="dynamic")
        self.canvas.create_polygon(
            ship.outline(), outline=config.SHIP_COLOR,
            fill=config.SPACE_COLOR, width=2, tags="dynamic")

    def _draw_messages(self, game: AsteroidsGame) -> None:
        """Надписи поверх игры: заставка, пауза, конец игры, уровень."""
        cx, cy = config.WIDTH / 2, config.HEIGHT / 2
        if game.state == START:
            self._text(cx, cy - 60, "АСТЕРОИДЫ", 46)
            self._text(cx, cy + 10, "Enter - начать игру", 20)
            self._text(cx, cy + 60,
                       "Стрелки - полёт,  Пробел - огонь,  Esc - пауза",
                       14, config.MUTED_TEXT_COLOR)
        elif game.state == PAUSED:
            self._text(cx, cy - 20, "ПАУЗА", 40)
            self._text(cx, cy + 30, "Esc - продолжить", 18)
        elif game.state == OVER:
            self._text(cx, cy - 50, "ИГРА ОКОНЧЕНА", 40)
            self._text(cx, cy + 5, f"Счёт: {game.score}", 22)
            self._text(cx, cy + 50, "Enter - сыграть ещё раз", 18,
                       config.MUTED_TEXT_COLOR)
        else:
            self._level_banner(game)

    def _level_banner(self, game: AsteroidsGame) -> None:
        """Показать «Уровень N» в начале уровня, плавно гася надпись."""
        now = time.perf_counter()
        if game.level != self._level:
            self._level = game.level
            self._level_shown = now
        left = 1 - (now - self._level_shown) / LEVEL_BANNER_TIME
        if left > 0:
            self._text(config.WIDTH / 2, config.HEIGHT / 3,
                       f"Уровень {game.level}", 30,
                       blend(config.TEXT_COLOR, config.SPACE_COLOR, left))

    def _text(self, x: float, y: float, text: str, size: int,
              color: str = config.TEXT_COLOR) -> None:
        """Написать текст по центру точки ``(x, y)``."""
        self.canvas.create_text(x, y, text=text, fill=color,
                                font=("Helvetica", size, "bold"),
                                tags="dynamic")
