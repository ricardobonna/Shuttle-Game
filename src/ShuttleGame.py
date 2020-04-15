import sys, pygame, math
from typing import Tuple
import random

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1000
THRUST = 10
GRAVITY = 30.0


class GameObject(object):
    """
    All physical objects represented in the game belongs to this class os game objects
    """

    def __init__(self, image, position: Tuple[float, float], speed: Tuple[float, float] = (0.0, 0.0),
                 angle: float = 0.0, angle_speed: float = 0.0):
        self.image = image
        if isinstance(self.image, str):
            self.image = pygame.image.load(self.image)   # Keep original image as surface
        self.rect = self.image.get_rect()
        self.area = pygame.display.get_surface().get_rect()
        self.surf = self.image
        self.surf_size = self.surf.get_size()

        self.pos = position
        self.speed = speed
        self.speed_prev = speed
        self.angle = angle  # angle in rads
        self.angle_speed = angle_speed
        self.angle_speed_prev = angle_speed

    def update_pos(self, dt: float):
        new_pos = ((self.speed[0] + self.speed_prev[0]) * dt / 2 + self.pos[0],
                   (self.speed[1] + self.speed_prev[1]) * dt / 2 + self.pos[1])
        self.set_pos(new_pos)
        self.speed_prev = self.speed

        new_angle = ((self.angle_speed + self.angle_speed_prev) * dt/2 + self.angle) % (2 * math.pi)
        self.set_angle(new_angle)
        self.angle_speed_prev = self.angle_speed

    def update(self, dt: float):
        self.update_pos(dt)

    def get_speed(self):
        return self.speed

    def set_speed(self, speed: Tuple[float, float]):
        self.speed = speed

    def get_pos(self) -> Tuple[float, float]:
        return self.pos

    def set_pos(self, pos: Tuple[float, float]):
        self.pos = pos
        self.rect.center = (int(self.pos[0]), int(self.pos[1]))

    def set_angle(self, angle: float):  # angle must be in radians
        self.angle = angle
        self.rot_image(self.angle)

    def set_angle_speed(self, angle_speed: float):
        self.angle_speed = angle_speed

    def get_angle_speed(self) -> float:
        return self.angle_speed

    def get_size(self):
        return self.image.get_size()

    def rot_image(self, angle: float):
        """rotate an image while keeping its center"""
        self.surf = pygame.transform.rotate(self.image, (angle * 180 / math.pi) % 360)
        self.rect = self.surf.get_rect(center=self.get_pos())
        self.surf_size = self.surf.get_size()

    def draw(self, window):
        window.blit(self.surf, self.rect)


class Ship(GameObject):
    def __init__(self, image, position, mass: float = 1.0, inertia: float = 1.0, arm_length: float = 1.0,
                 gravity: float = 9.81):
        GameObject.__init__(self, image, position)
        self.mass = mass
        self.inertia = inertia
        self.length = arm_length
        self.gravity = gravity
        self.reloaded = True
        self.k = 0
        self.shot_speed = 1000.0

    def fire(self):
        if self.reloaded:
            self.reloaded = False
            projectile_speed = (-self.speed[0] - self.shot_speed * math.sin(self.angle),
                                -self.speed[1] - self.shot_speed * math.cos(self.angle))
            bullet_surface = pygame.Surface((5, 5))
            bullet_surface.fill((255, 255, 255))
            return GameObject(bullet_surface, position=self.pos, speed=projectile_speed)
        return None

    def reload(self):
        if not self.reloaded:
            self.k += 1
            if self.k > 10:
                self.k = 0
                self.reloaded = True

    def update(self, dt: float, fd=0, fe=0):
        self.update_pos(dt)

        new_speed = ((-math.sin(self.angle) / self.mass) * (fd + fe) * dt + self.speed[0],
                     (-(math.cos(self.angle) / self.mass) * (fd + fe) + self.gravity) * dt + self.speed[1])
        self.set_speed(new_speed)
        new_angle_speed = (self.length / self.inertia * (fd - fe)) * dt + self.angle_speed
        self.set_angle_speed(new_angle_speed)

        self.reload()


class GameWindow(object):
    def __init__(self, width, height, background):
        self.size = width, height
        self.window = pygame.display.set_mode(self.size)
        self.background = pygame.image.load(background)
        self.back_size = self.background.get_size()
        self.shuttle = Ship("./figs/shuttle.png", position=(self.size[0] / 2, self.size[1] / 2),
                            mass=0.2, inertia=10.0, arm_length=1.0, gravity=GRAVITY)
        self.asteroid_list = []
        self.bullet_list = []

    def generate_asteroid(self):
        """
        Randomly generates an asteroid in one of the corners of the window
        """
        screen_side = random.randint(1, 4)
        if screen_side == 1:
            asteroid_pos = (0.0, random.random() * self.size[1])
            asteroid_speed = (random.uniform(1, 2) * 30.0, random.uniform(-2, 2) * 20.0)
        elif screen_side == 2:
            asteroid_pos = (self.size[0], random.random() * self.size[1])
            asteroid_speed = (random.uniform(-2, -1) * 30.0, random.uniform(-2, 2) * 20.0)
        elif screen_side == 3:
            asteroid_pos = (random.random() * self.size[0], 0.0)
            asteroid_speed = (random.uniform(-2, 2) * 30.0, random.uniform(1, 2) * 20.0)
        else:
            asteroid_pos = (random.random() * self.size[0], self.size[1])
            asteroid_speed = (random.uniform(-2, 2) * 30.0, random.uniform(-2, -1) * 20.0)
        asteroid_rot = random.random() * 2
        asteroid_scale = random.random() * 0.7 + 0.3
        asteroid_angle = random.random() * 360
        asteroid_fig = pygame.image.load("./figs/asteroid.png")
        asteroid_fig = pygame.transform.rotozoom(asteroid_fig, asteroid_angle, asteroid_scale)
        new_asteroid = GameObject(asteroid_fig, asteroid_pos, asteroid_speed, angle_speed=asteroid_rot)
        self.asteroid_list.append(new_asteroid)

    def on_screen(self, position: Tuple[float, float]):
        return -20 <= position[0] <= self.size[0] + 20 and -20 <= position[1] <= self.size[1] + 20

    def update(self, dt: float, fd=0, fe=0, fire: bool = False):
        if fire:
            projectile = self.shuttle.fire()
            if projectile is not None:
                self.bullet_list.append(projectile)
        self.shuttle.update(dt, fd, fe)
        for asteroid in self.asteroid_list:
            asteroid.update(dt)
        for bullet in self.bullet_list:
            bullet.update(dt)

    def draw(self):
        self.window.fill((0, 0, 0))
        self.window.blit(self.background, (self.size[0] / 2 - self.back_size[0] / 2,
                         self.size[1] / 2 - self.back_size[1] / 2))
        if not self.on_screen(self.shuttle.pos):
            print("Game over")
        self.shuttle.draw(self.window)

        for asteroid in self.asteroid_list:
            if not self.on_screen(asteroid.pos):
                self.asteroid_list.remove(asteroid)
                continue
            asteroid.draw(self.window)

        for bullet in self.bullet_list:
            if not self.on_screen(bullet.pos):
                self.bullet_list.remove(bullet)
                continue
            bullet.draw(self.window)


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption("Shuttle game")
    clock = pygame.time.Clock()
    freq = 30

    screen = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, "./figs/earth.png")

    run = True
    while run:
        clock.tick(freq)
        for event in pygame.event.get([pygame.QUIT, pygame.K_SPACE]):
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        Fd = THRUST if keys[pygame.K_RIGHT] else 0
        Fe = THRUST if keys[pygame.K_LEFT] else 0
        fire = True if keys[pygame.K_SPACE] else False
        if keys[pygame.K_BACKSPACE]:
            screen.generate_asteroid()
        pygame.event.clear()

        # Update actors
        screen.update(1 / freq, Fd, Fe, fire)

        # Update screen
        screen.draw()
        pygame.display.update()
        # print("FPS: %0.2f" % clock.get_fps())

