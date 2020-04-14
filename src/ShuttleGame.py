import sys, pygame, math
from typing import Tuple

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
THRUST = 10
GRAVITY = 30


class GameObject(pygame.sprite.Sprite):
    """
    All physical objects represented in the game belongs to this class os game objects
    """

    def __init__(self, image, position: Tuple[float, float], speed: Tuple[float, float] = (0.0, 0.0),
                 angle: float = 0.0, angle_speed: float = 0.0):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        if isinstance(self.image, str):
            self.image = pygame.image.load(self.image)

        self.rect = self.image.get_rect()
        self.area = pygame.display.get_surface().get_rect()
        self.surf = self.image

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

        if (self.rect.left > self.area.right) or \
                (self.rect.top > self.area.bottom) or \
                (self.rect.bottom < self.area.top) or \
                (self.rect.right < 0):
            self.kill()

    def get_speed(self):
        return self.speed

    def set_speed(self, speed: Tuple[float, float]):
        self.speed = speed

    def get_pos(self):
        return self.pos

    def set_pos(self, pos: Tuple[float, float]):
        self.pos = pos
        self.rect.center = (int(self.pos[0]), int(self.pos[1]))

    def set_angle(self, angle: float):  # angle must be in radians
        self.angle = angle
        self.rot_image(self.angle)

    def set_angle_speed(self, angle_speed: float):
        self.angle_speed = angle_speed

    def get_angle_speed(self):
        return self.angle_speed

    def get_size(self):
        return self.image.get_size()

    def rot_image(self, angle: float):
        """rotate an image while keeping its center"""
        rotated_image = pygame.transform.rotate(self.image, angle * 180 / math.pi)
        rot_rect = rotated_image.get_rect(center=self.get_pos())
        self.rect = rot_rect
        self.surf = rotated_image


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

    def fire(self):
        if self.reloaded:
            self.reloaded = False
            print('fire')

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

        if (self.rect.left > self.area.right) or \
                (self.rect.top > self.area.bottom) or \
                (self.rect.bottom < self.area.top) or \
                (self.rect.right < 0):
            self.kill()


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption("Shuttle game")
    clock = pygame.time.Clock()
    freq = 30

    size = SCREEN_WIDTH, SCREEN_HEIGHT
    black = 0, 0, 0
    screen = pygame.display.set_mode(size)
    background = pygame.image.load("./figs/earth.png")
    back_size = background.get_size()

    shuttle = Ship("./figs/shuttle.png", position=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2),
                   mass=0.2, inertia=10.0, arm_length=1.0, gravity=GRAVITY)

    asteroid = GameObject("./figs/asteroid.png", position=(0.0, 0.0), speed=(30.0, 20.0), angle_speed=1.0)

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
        if keys[pygame.K_SPACE]:
            shuttle.fire()
        pygame.event.clear()

        # Update actors
        shuttle.update(1 / freq, Fd, Fe)
        asteroid.update(1 / freq)

        # Update screen
        screen.fill(black)
        screen.blit(background, (SCREEN_WIDTH / 2 - back_size[0] / 2,
                                 SCREEN_HEIGHT / 2 - back_size[1] / 2))
        screen.blit(shuttle.surf, shuttle.rect)
        screen.blit(asteroid.surf, asteroid.rect)
        pygame.display.flip()
        # print("FPS: %0.2f" % clock.get_fps())

