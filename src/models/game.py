"""Правила игры: уровни, стрельба, столкновения, очки и жизни."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from src import config
from src.models.asteroid import Asteroid, random_velocity, split
from src.models.bullet import Bullet, Debris
from src.models.ship import Ship

START = "start"
PLAYING = "playing"
PAUSED = "paused"
OVER = "over"


@dataclass
class Controls:
    """Какие клавиши управления сейчас нажаты."""

    left: bool = False
    right: bool = False
    thrust: bool = False
    fire: bool = False


class AsteroidsGame:
    """Вся игра: корабль, астероиды, пули, обломки, счёт и жизни.

    Состояния игры: ``START`` — заставка, ``PLAYING`` — идёт игра,
    ``PAUSED`` — пауза, ``OVER`` — игра окончена. На заставке
    и после конца игры астероиды продолжают летать для красоты.
    """

    def __init__(self, rng: random.Random | None = None) -> None:
        """Создать игру на заставке с несколькими астероидами."""
        self.rng = rng or random.Random()
        self.width = config.WIDTH
        self.height = config.HEIGHT
        self.state = START
        self.ship: Ship | None = None
        self.asteroids: list[Asteroid] = []
        self.bullets: list[Bullet] = []
        self.debris: list[Debris] = []
        self.score = 0
        self.best = 0
        self.lives = 0
        self.level = 0
        self.respawn = 0.0
        for _ in range(config.START_ASTEROIDS + 2):
            self._spawn_asteroid()

    # ------------------------------------------------------------------
    # Начало игры и уровни
    # ------------------------------------------------------------------
    def new_game(self) -> None:
        """Начать игру с нуля: 3 жизни, первый уровень."""
        self.score = 0
        self.lives = config.LIVES
        self.level = 0
        self.asteroids.clear()
        self.bullets.clear()
        self.debris.clear()
        self._new_ship()
        self.state = PLAYING
        self.next_level()

    def next_level(self) -> None:
        """Перейти на следующий уровень: больших астероидов больше."""
        self.level += 1
        count = min(config.START_ASTEROIDS + self.level,
                    config.MAX_ASTEROIDS)
        for _ in range(count):
            self._spawn_asteroid()

    def _new_ship(self) -> None:
        """Поставить корабль в центр с временной защитой."""
        self.ship = Ship(self.width / 2, self.height / 2,
                         config.SHIP_RADIUS)
        self.ship.invulnerable = config.INVULNERABLE_TIME

    def _spawn_asteroid(self) -> None:
        """Добавить большой астероид подальше от корабля.

        Случайная точка выбирается заново, пока она слишком близко
        к кораблю (или к центру, где он появится).
        """
        cx, cy = self.width / 2, self.height / 2
        if self.ship:
            cx, cy = self.ship.x, self.ship.y
        while True:
            x = self.rng.uniform(0, self.width)
            y = self.rng.uniform(0, self.height)
            if math.hypot(x - cx, y - cy) > config.SAFE_DISTANCE:
                break
        vx, vy = random_velocity(config.ASTEROID_SPEED[3], self.rng)
        self.asteroids.append(Asteroid(x, y, vx, vy, 3,
                                       config.ASTEROID_RADIUS[3],
                                       self.rng))

    def toggle_pause(self) -> None:
        """Поставить игру на паузу или продолжить."""
        if self.state == PLAYING:
            self.state = PAUSED
        elif self.state == PAUSED:
            self.state = PLAYING

    # ------------------------------------------------------------------
    # Один шаг игры
    # ------------------------------------------------------------------
    def update(self, dt: float, controls: Controls) -> None:
        """Сделать шаг времени ``dt`` секунд с нажатыми ``controls``."""
        if self.state == PAUSED:
            return
        for rock in self.asteroids:
            rock.move(dt, self.width, self.height)
        for piece in self.debris:
            piece.move(dt, self.width, self.height)
        self.debris = [d for d in self.debris if d.alive]
        if self.state != PLAYING:
            return

        if self.ship:
            self._control_ship(dt, controls)
        for bullet in self.bullets:
            bullet.move(dt, self.width, self.height)
        self.bullets = [b for b in self.bullets if b.alive]

        self._bullet_hits()
        self._ship_hit()
        self._respawn(dt)
        if not self.asteroids:
            self.next_level()

    def _control_ship(self, dt: float, controls: Controls) -> None:
        """Повернуть, разогнать, сдвинуть корабль и выстрелить."""
        ship = self.ship
        if controls.left:
            ship.turn(-1, config.SHIP_TURN_SPEED, dt)
        if controls.right:
            ship.turn(1, config.SHIP_TURN_SPEED, dt)
        ship.thrusting = controls.thrust
        if controls.thrust:
            ship.thrust(config.SHIP_THRUST, config.SHIP_MAX_SPEED, dt)
        else:
            ship.drift(config.SHIP_DRAG, dt)
        ship.move(dt, self.width, self.height)
        ship.tick(dt)
        if controls.fire and ship.can_shoot():
            self.shoot()

    def shoot(self) -> None:
        """Выпустить пулю из носа корабля.

        Скорость пули — её собственная скорость в сторону носа плюс
        скорость корабля: пуля, выпущенная на ходу, летит быстрее.
        """
        ship = self.ship
        dx, dy = ship.direction()
        nose = ship.radius * 1.25
        self.bullets.append(Bullet(
            ship.x + dx * nose, ship.y + dy * nose,
            dx * config.BULLET_SPEED + ship.vx,
            dy * config.BULLET_SPEED + ship.vy, config.BULLET_LIFE))
        ship.cooldown = config.SHOT_COOLDOWN

    def _bullet_hits(self) -> None:
        """Проверить попадания пуль: астероид раскалывается, пуля пропадает.

        Каждую пулю сравниваем с каждым астероидом. Попавшая пуля
        и сбитый астероид убираются, вместо астероида появляются
        осколки, игроку начисляются очки.
        """
        for bullet in list(self.bullets):
            for rock in self.asteroids:
                if bullet.collides(rock):
                    self.bullets.remove(bullet)
                    self.asteroids.remove(rock)
                    self.asteroids.extend(split(
                        rock, config.ASTEROID_RADIUS,
                        config.ASTEROID_SPEED, self.rng))
                    self.add_points(config.ASTEROID_POINTS[rock.size])
                    self._explode(rock.x, rock.y)
                    break

    def add_points(self, points: int) -> None:
        """Прибавить очки и обновить рекорд."""
        self.score += points
        self.best = max(self.best, self.score)

    def _ship_hit(self) -> None:
        """Проверить, не врезался ли корабль в астероид."""
        ship = self.ship
        if ship is None or ship.invulnerable > 0:
            return
        if any(ship.collides(rock) for rock in self.asteroids):
            self._explode(ship.x, ship.y, count=config.DEBRIS_COUNT * 2)
            self.ship = None
            self.lives -= 1
            self.respawn = config.RESPAWN_DELAY

    def _respawn(self, dt: float) -> None:
        """После гибели подождать и дать новый корабль или закончить игру."""
        if self.ship is not None:
            return
        self.respawn -= dt
        if self.respawn <= 0:
            if self.lives > 0:
                self._new_ship()
            else:
                self.state = OVER

    def _explode(self, x: float, y: float,
                 count: int = config.DEBRIS_COUNT) -> None:
        """Разбросать обломки из точки ``(x, y)`` во все стороны."""
        for _ in range(count):
            vx, vy = random_velocity((40, 160), self.rng)
            life = self.rng.uniform(0.5, 1.0) * config.DEBRIS_LIFE
            self.debris.append(Debris(x, y, vx, vy, life))
