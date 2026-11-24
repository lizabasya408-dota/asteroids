"""Настройки игры: размеры, физика, очки, цвета."""

# Размер игрового поля в пикселях.
WIDTH = 900
HEIGHT = 640

# Частота кадров. Если кадр задержался, шаг по времени всё равно не
# больше MAX_STEP секунд, чтобы объекты не «перепрыгивали» друг друга.
FPS = 60
FRAME_DELAY_MS = 1000 // FPS
MAX_STEP = 0.05

# Корабль: скорость поворота (градусов в секунду), ускорение двигателя
# (пикселей в секунду за секунду), торможение в космосе и предел скорости.
SHIP_RADIUS = 15
SHIP_TURN_SPEED = 220
SHIP_THRUST = 330
SHIP_DRAG = 0.5
SHIP_MAX_SPEED = 400

# Пули: скорость, время жизни и пауза между выстрелами (в секундах).
BULLET_SPEED = 560
BULLET_LIFE = 0.9
SHOT_COOLDOWN = 0.18

# Жизни и защита после появления нового корабля.
LIVES = 3
RESPAWN_DELAY = 1.5
INVULNERABLE_TIME = 2.5

# Астероиды трёх размеров: 3 — большой, 2 — средний, 1 — маленький.
# Для каждого размера: радиус, диапазон скорости и очки за попадание.
ASTEROID_RADIUS = {3: 46, 2: 26, 1: 14}
ASTEROID_SPEED = {3: (30, 70), 2: (60, 110), 1: (90, 150)}
ASTEROID_POINTS = {3: 20, 2: 50, 1: 100}

# Сколько больших астероидов на уровне: START_ASTEROIDS + номер уровня,
# но не больше MAX_ASTEROIDS. Новые астероиды появляются не ближе
# SAFE_DISTANCE пикселей от корабля.
START_ASTEROIDS = 3
MAX_ASTEROIDS = 10
SAFE_DISTANCE = 170

# Обломки при взрыве: сколько их и сколько секунд они живут.
DEBRIS_COUNT = 14
DEBRIS_LIFE = 0.8

# Цвета.
SPACE_COLOR = "#05070f"
STAR_COLOR = "#8790b8"
SHIP_COLOR = "#e8f1ff"
FLAME_COLOR = "#ffb347"
BULLET_COLOR = "#ffe27a"
ASTEROID_COLOR = "#b9c2d8"
DEBRIS_COLOR = "#ffcf8a"
TEXT_COLOR = "#e8f1ff"
MUTED_TEXT_COLOR = "#8790b8"
BAR_COLOR = "#0c1020"
