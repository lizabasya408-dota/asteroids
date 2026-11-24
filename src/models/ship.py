"""Корабль игрока."""

from __future__ import annotations

import math

from src.models.space_object import SpaceObject


class Ship(SpaceObject):
    """Корабль: поворачивается, разгоняется по инерции и стреляет.

    ``angle`` — куда смотрит нос корабля, в градусах: 0 — вверх,
    90 — вправо. В космосе нет трения, поэтому корабль летит, даже
    когда двигатель выключен, и лишь понемногу тормозит.
    """

    def __init__(self, x: float, y: float, radius: float = 15) -> None:
        """Поставить неподвижный корабль носом вверх в точку ``(x, y)``."""
        super().__init__(x, y, radius=radius)
        self.angle = 0.0
        self.thrusting = False
        self.invulnerable = 0.0
        self.cooldown = 0.0

    def direction(self) -> tuple[float, float]:
        """Единичный вектор, куда смотрит нос.

        Угол отсчитывается от направления «вверх» по часовой стрелке.
        Ось Y экрана смотрит вниз, поэтому вверх — это (0, -1),
        а в общем случае (sin угла, -cos угла).
        """
        rad = math.radians(self.angle)
        return math.sin(rad), -math.cos(rad)

    def turn(self, direction: int, speed: float, dt: float) -> None:
        """Повернуть корабль: ``direction`` = -1 влево, +1 вправо."""
        self.angle = (self.angle + direction * speed * dt) % 360

    def thrust(self, power: float, max_speed: float, dt: float) -> None:
        """Включить двигатель: прибавить скорость в сторону носа.

        Скорость меняется на ускорение × время. Если она стала больше
        ``max_speed``, вектор скорости укорачивается до этой длины,
        а направление полёта сохраняется.
        """
        dx, dy = self.direction()
        self.vx += dx * power * dt
        self.vy += dy * power * dt
        speed = math.hypot(self.vx, self.vy)
        if speed > max_speed:
            self.vx *= max_speed / speed
            self.vy *= max_speed / speed

    def drift(self, drag: float, dt: float) -> None:
        """Плавно погасить скорость: умножить её на e^(-drag * dt)."""
        slow = math.exp(-drag * dt)
        self.vx *= slow
        self.vy *= slow

    def tick(self, dt: float) -> None:
        """Отсчитать время защиты и перезарядки."""
        self.invulnerable = max(0.0, self.invulnerable - dt)
        self.cooldown = max(0.0, self.cooldown - dt)

    def can_shoot(self) -> bool:
        """Перезарядилась ли пушка."""
        return self.cooldown == 0

    def outline(self) -> list[tuple[float, float]]:
        """Точки контура корабля на экране.

        Контур — нос, правое крыло, вырез сзади и левое крыло.
        Каждая точка задана углом относительно носа и расстоянием
        от центра. Чтобы повернуть её вместе с кораблём, к углу
        прибавляется угол корабля, и по синусу и косинусу находятся
        координаты (как при переходе из полярных координат).
        """
        r = self.radius
        shape = ((0, r * 1.25), (140, r), (180, r * 0.45), (220, r))
        points = []
        for offset, dist in shape:
            rad = math.radians(self.angle + offset)
            points.append((self.x + dist * math.sin(rad),
                           self.y - dist * math.cos(rad)))
        return points
