"""Тесты физики и правил игры «Астероиды»."""

import math
import random
import unittest

from src import config
from src.models.asteroid import Asteroid, split
from src.models.bullet import Bullet, Debris
from src.models.game import OVER, PAUSED, PLAYING, AsteroidsGame, Controls
from src.models.ship import Ship
from src.models.space_object import SpaceObject
from src.renderers.space_renderer import blend


def rock(x, y, size=3, vx=0.0, vy=0.0):
    """Неподвижный (по умолчанию) астероид нужного размера."""
    return Asteroid(x, y, vx, vy, size, config.ASTEROID_RADIUS[size],
                    random.Random(1))


class SpaceObjectTest(unittest.TestCase):
    """Движение и столкновения."""

    def test_moves_by_velocity(self):
        """За время dt объект сдвигается на скорость × dt."""
        obj = SpaceObject(100, 100, 50, -20)
        obj.move(2, 900, 640)
        self.assertEqual((obj.x, obj.y), (200, 60))

    def test_wraps_around_edges(self):
        """Улетев за край, объект появляется с другой стороны."""
        obj = SpaceObject(895, 5, 10, -10)
        obj.move(1, 900, 640)
        self.assertAlmostEqual(obj.x, 5)
        self.assertAlmostEqual(obj.y, 635)

    def test_collision_by_radii(self):
        """Круги сталкиваются, если расстояние меньше суммы радиусов."""
        a = SpaceObject(0, 0, radius=10)
        self.assertTrue(a.collides(SpaceObject(15, 0, radius=6)))
        self.assertFalse(a.collides(SpaceObject(17, 0, radius=6)))


class ShipTest(unittest.TestCase):
    """Корабль: поворот, двигатель и торможение."""

    def test_starts_facing_up(self):
        """Нос нового корабля смотрит вверх, то есть в сторону -y."""
        dx, dy = Ship(0, 0).direction()
        self.assertAlmostEqual(dx, 0)
        self.assertAlmostEqual(dy, -1)

    def test_turn(self):
        """Поворот вправо за полсекунды на скорости 180°/с — это 90°."""
        ship = Ship(0, 0)
        ship.turn(1, 180, 0.5)
        self.assertAlmostEqual(ship.angle, 90)
        dx, dy = ship.direction()
        self.assertAlmostEqual(dx, 1)

    def test_thrust_and_speed_limit(self):
        """Двигатель разгоняет корабль, но не быстрее предела."""
        ship = Ship(0, 0)
        ship.thrust(100, 1000, 1)
        self.assertAlmostEqual(ship.vy, -100)
        for _ in range(50):
            ship.thrust(100, 300, 1)
        self.assertAlmostEqual(math.hypot(ship.vx, ship.vy), 300)

    def test_drift_slows_down(self):
        """Без двигателя корабль постепенно тормозит."""
        ship = Ship(0, 0)
        ship.vx = 100
        ship.drift(0.5, 1)
        self.assertAlmostEqual(ship.vx, 100 * math.exp(-0.5))


class AsteroidTest(unittest.TestCase):
    """Раскалывание астероидов."""

    def test_big_splits_into_two_medium(self):
        """Большой астероид раскалывается на два средних."""
        pieces = split(rock(50, 50, 3), config.ASTEROID_RADIUS,
                       config.ASTEROID_SPEED, random.Random(2))
        self.assertEqual([p.size for p in pieces], [2, 2])
        for p in pieces:
            self.assertEqual((p.x, p.y), (50, 50))
            self.assertEqual(p.radius, config.ASTEROID_RADIUS[2])

    def test_small_disappears(self):
        """Маленький астероид просто рассыпается."""
        self.assertEqual(split(rock(0, 0, 1), config.ASTEROID_RADIUS,
                               config.ASTEROID_SPEED, random.Random()), [])

    def test_outline_around_center(self):
        """Все вершины контура лежат недалеко от центра."""
        a = rock(100, 100, 3)
        for x, y in a.outline():
            self.assertLessEqual(math.hypot(x - 100, y - 100),
                                 a.radius * 1.15 + 1e-9)


class BulletTest(unittest.TestCase):
    """Пули и обломки живут ограниченное время."""

    def test_bullet_life(self):
        """Пуля исчезает, когда кончается время жизни."""
        bullet = Bullet(0, 0, 100, 0, life=0.5)
        bullet.move(0.3, 900, 640)
        self.assertTrue(bullet.alive)
        bullet.move(0.3, 900, 640)
        self.assertFalse(bullet.alive)

    def test_debris_fades(self):
        """Обломок гаснет от 1 до 0."""
        piece = Debris(0, 0, 0, 0, life=1.0)
        self.assertEqual(piece.fade, 1.0)
        piece.move(0.75, 900, 640)
        self.assertAlmostEqual(piece.fade, 0.25)


class GameTest(unittest.TestCase):
    """Правила игры."""

    def setUp(self):
        """Новая игра с фиксированным зерном случайных чисел."""
        self.game = AsteroidsGame(random.Random(4))
        self.game.new_game()

    def test_new_game(self):
        """Новая игра: 3 жизни, уровень 1, 4 больших астероида."""
        g = self.game
        self.assertEqual((g.state, g.lives, g.level), (PLAYING, 3, 1))
        self.assertEqual(len(g.asteroids), config.START_ASTEROIDS + 1)
        for a in g.asteroids:
            self.assertGreater(a.distance_to(g.ship), config.SAFE_DISTANCE)

    def test_shooting_and_cooldown(self):
        """Выстрел создаёт пулю, следующий — только после перезарядки."""
        g = self.game
        g.update(0.01, Controls(fire=True))
        self.assertEqual(len(g.bullets), 1)
        g.update(0.01, Controls(fire=True))
        self.assertEqual(len(g.bullets), 1)
        g.update(config.SHOT_COOLDOWN, Controls(fire=True))
        self.assertEqual(len(g.bullets), 2)

    def test_hit_splits_and_scores(self):
        """Попадание раскалывает астероид и приносит очки."""
        g = self.game
        g.asteroids = [rock(100, 100, 3)]
        g.bullets = [Bullet(100, 100, 0, 0, life=1)]
        g.update(0.01, Controls())
        self.assertEqual(g.score, config.ASTEROID_POINTS[3])
        self.assertEqual([a.size for a in g.asteroids], [2, 2])
        self.assertEqual(g.bullets, [])

    def test_crash_costs_life(self):
        """Столкновение с астероидом отнимает жизнь."""
        g = self.game
        g.ship.invulnerable = 0
        g.asteroids = [rock(g.ship.x, g.ship.y, 3)]
        g.update(0.01, Controls())
        self.assertIsNone(g.ship)
        self.assertEqual(g.lives, 2)

    def test_invulnerable_after_spawn(self):
        """Сразу после появления корабль не погибает."""
        g = self.game
        g.asteroids = [rock(g.ship.x, g.ship.y, 3)]
        g.update(0.01, Controls())
        self.assertIsNotNone(g.ship)
        self.assertEqual(g.lives, 3)

    def test_game_over(self):
        """Потеряв последнюю жизнь, игрок видит конец игры."""
        g = self.game
        g.lives = 1
        g.ship.invulnerable = 0
        g.asteroids = [rock(g.ship.x, g.ship.y, 3)]
        g.update(0.01, Controls())
        g.update(config.RESPAWN_DELAY, Controls())
        self.assertEqual(g.state, OVER)

    def test_next_level(self):
        """Когда астероиды кончились, начинается следующий уровень."""
        g = self.game
        g.asteroids = []
        g.update(0.01, Controls())
        self.assertEqual(g.level, 2)
        self.assertEqual(len(g.asteroids), config.START_ASTEROIDS + 2)

    def test_pause_freezes(self):
        """На паузе ничего не движется."""
        g = self.game
        g.toggle_pause()
        x = g.asteroids[0].x
        g.update(0.5, Controls(thrust=True))
        self.assertEqual(g.state, PAUSED)
        self.assertEqual(g.asteroids[0].x, x)

    def test_best_score(self):
        """Рекорд не уменьшается после новой игры."""
        g = self.game
        g.add_points(300)
        g.new_game()
        self.assertEqual((g.score, g.best), (0, 300))


class BlendTest(unittest.TestCase):
    """Смешивание цветов для гаснущих обломков."""

    def test_blend(self):
        """alpha = 1 — сам цвет, alpha = 0 — фон."""
        self.assertEqual(blend("#ff0000", "#000000", 1), "#ff0000")
        self.assertEqual(blend("#ff0000", "#000000", 0), "#000000")
        self.assertEqual(blend("#c86400", "#000064", 0.5), "#643232")


if __name__ == "__main__":
    unittest.main()
