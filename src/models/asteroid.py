"""Астероид: неровный камень, который раскалывается от попадания."""

from __future__ import annotations

import math
import random

from src.models.space_object import SpaceObject


class Asteroid(SpaceObject):
    """Астероид размера 3 (большой), 2 (средний) или 1 (маленький).

    Форма — неровный многоугольник: вершины стоят по кругу, но каждая
    на своём случайном расстоянии от центра. Астероид летит по прямой
    и медленно вращается.
    """

    def __init__(self, x: float, y: float, vx: float, vy: float,
                 size: int, radius: float, rng: random.Random) -> None:
        """Создать астероид размера ``size`` со случайной формой."""
        super().__init__(x, y, vx, vy, radius)
        self.size = size
        self.angle = rng.uniform(0, 360)
        self.spin = rng.uniform(-60, 60)
        count = rng.randint(9, 12)
        # Для каждой вершины — её угол и доля радиуса от 0.7 до 1.15.
        self.shape = [(360 * i / count, rng.uniform(0.7, 1.15))
                      for i in range(count)]

    def move(self, dt: float, width: float, height: float) -> None:
        """Сдвинуть астероид и немного повернуть его."""
        super().move(dt, width, height)
        self.angle = (self.angle + self.spin * dt) % 360

    def outline(self) -> list[tuple[float, float]]:
        """Точки контура на экране с учётом поворота."""
        points = []
        for offset, part in self.shape:
            rad = math.radians(self.angle + offset)
            points.append((self.x + self.radius * part * math.cos(rad),
                           self.y + self.radius * part * math.sin(rad)))
        return points


def random_velocity(speed_range: tuple[float, float],
                    rng: random.Random) -> tuple[float, float]:
    """Случайная скорость: случайное направление и модуль из диапазона."""
    angle = rng.uniform(0, 2 * math.pi)
    speed = rng.uniform(*speed_range)
    return speed * math.cos(angle), speed * math.sin(angle)


def split(asteroid: Asteroid, radii: dict[int, float],
          speeds: dict[int, tuple[float, float]],
          rng: random.Random) -> list[Asteroid]:
    """Расколоть астероид на два поменьше.

    Большой даёт два средних, средний — два маленьких, а маленький
    просто рассыпается (пустой список). Осколки получают случайную
    скорость своего размера плюс половину скорости родителя, поэтому
    разлетаются в разные стороны, но продолжают его движение.
    """
    size = asteroid.size - 1
    if size == 0:
        return []
    pieces = []
    for _ in range(2):
        vx, vy = random_velocity(speeds[size], rng)
        pieces.append(Asteroid(asteroid.x, asteroid.y,
                               vx + asteroid.vx * 0.5,
                               vy + asteroid.vy * 0.5,
                               size, radii[size], rng))
    return pieces
