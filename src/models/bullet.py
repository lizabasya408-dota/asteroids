"""Пули корабля и обломки взрывов."""

from __future__ import annotations

from src.models.space_object import SpaceObject


class Bullet(SpaceObject):
    """Пуля: летит по прямой и исчезает через ``life`` секунд."""

    def __init__(self, x: float, y: float, vx: float, vy: float,
                 life: float) -> None:
        """Создать пулю с ограниченным временем жизни."""
        super().__init__(x, y, vx, vy, radius=2)
        self.life = life

    @property
    def alive(self) -> bool:
        """Не закончилось ли время жизни."""
        return self.life > 0

    def move(self, dt: float, width: float, height: float) -> None:
        """Сдвинуть пулю и уменьшить оставшееся время жизни."""
        super().move(dt, width, height)
        self.life -= dt


class Debris(Bullet):
    """Обломок взрыва: как пуля, но постепенно гаснет.

    ``fade`` — доля оставшейся жизни от 1 до 0, по ней рисуется
    всё более тёмная точка.
    """

    def __init__(self, x: float, y: float, vx: float, vy: float,
                 life: float) -> None:
        """Создать обломок."""
        super().__init__(x, y, vx, vy, life)
        self.max_life = life

    @property
    def fade(self) -> float:
        """Яркость обломка: 1 — только что появился, 0 — погас."""
        return max(0.0, self.life / self.max_life)
