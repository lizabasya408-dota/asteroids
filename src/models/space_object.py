"""Базовый класс для всего, что летает в космосе."""

from __future__ import annotations

import math


class SpaceObject:
    """Летающий объект: положение, скорость и радиус.

    Поле «склеено» по краям, как в оригинальной игре: объект, улетевший
    за правый край, появляется слева, за нижний — сверху. От этого
    класса наследуются корабль, астероиды, пули и обломки.
    """

    def __init__(self, x: float, y: float, vx: float = 0.0,
                 vy: float = 0.0, radius: float = 1.0) -> None:
        """Создать объект в точке ``(x, y)`` со скоростью ``(vx, vy)``."""
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius

    def move(self, dt: float, width: float, height: float) -> None:
        """Сдвинуть объект на скорость × время и «склеить» края поля.

        Остаток от деления (%) возвращает координату в пределы поля:
        например, x = -5 при ширине 900 превращается в 895.
        """
        self.x = (self.x + self.vx * dt) % width
        self.y = (self.y + self.vy * dt) % height

    def distance_to(self, other: SpaceObject) -> float:
        """Расстояние между центрами двух объектов."""
        return math.hypot(self.x - other.x, self.y - other.y)

    def collides(self, other: SpaceObject) -> bool:
        """Столкнулись ли объекты.

        Каждый объект считается кругом. Круги пересекаются, если
        расстояние между центрами меньше суммы радиусов.
        """
        return self.distance_to(other) < self.radius + other.radius
