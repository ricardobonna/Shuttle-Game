import os, sys, pygame, math, time, threading

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
THRUST = 10
GRAVITY = 25


class GameObject( pygame.sprite.Sprite ):
    """
    Esta é a classe básica de todos os objetos do jogo.
    """
    def __init__(self, image, position, speed = (0,0), angle = 0, angle_speed = 0):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        if isinstance(self.image, str):
            self.image = pygame.image.load(self.image)

        self.rect = self.image.get_rect()
        screen    = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.surf = self.image

        self.set_pos(position)
        self.set_speed(speed)
        self.set_angle(angle)       # angle in rads
        self.set_angle_speed(angle_speed)

    def update(self, dt):
        new_pos = (self.speed[0] * dt + self.pos[0], self.speed[1] * dt + self.pos[1])
        self.set_pos(new_pos)
        self.set_angle((self.angle_speed * dt + self.angle) % (2*math.pi))

        if ( self.rect.left > self.area.right ) or \
               ( self.rect.top > self.area.bottom ) or \
               ( self.rect.bottom > self.area.top ) or \
               ( self.rect.right < 0 ):
            self.kill()
        if ( self.rect.bottom < - 40 ):
            self.kill()

    def get_speed(self):
        return self.speed

    def set_speed(self, speed):
        self.speed = speed

    def get_pos(self):
        return self.pos

    def set_pos(self, pos):
        self.pos = pos
        self.rect.center = self.pos

    def set_angle(self, angle):     # angle must be in radians
        self.angle = angle
        self.rot_image(self.angle)

    def set_angle_speed(self, angle_speed):
        self.angle_speed = angle_speed

    def get_angle_speed(self):
        return self.angle_speed

    def get_size(self):
        return self.image.get_size()

    def rot_image(self, angle):
        """rotate an image while keeping its center"""
        rotated_image = pygame.transform.rotate(self.image, angle * 180/math.pi)
        rot_rect = rotated_image.get_rect(center = self.get_pos())
        self.rect = rot_rect
        self.surf = rotated_image


class Ship(GameObject):
    def __init__(self, image, position, m = 1, I = 1, l = 1, g = 9.81):
        GameObject.__init__(self, image, position)
        self.m = m
        self.I = I
        self.l = l
        self.g = g

    def update(self, dt, fd = 0, fe = 0):
        new_pos = (self.speed[0] * dt + self.pos[0], self.speed[1] * dt + self.pos[1])
        self.set_pos(new_pos)
        self.set_angle((self.angle_speed * dt + self.angle) % (2*math.pi))

        new_speed = ((-math.sin(self.angle)/self.m) * (fd+fe) * dt + self.speed[0],
                      (-(math.cos(self.angle)/self.m) * (fd+fe) + self.g) * dt + self.speed[1])
        self.set_speed(new_speed)
        new_angle_speed = (self.l/self.I * (fd-fe)) * dt + self.angle_speed
        self.set_angle_speed(new_angle_speed)

        if ( self.rect.left > self.area.right ) or \
               ( self.rect.top > self.area.bottom ) or \
               ( self.rect.bottom > self.area.top ) or \
               ( self.rect.right < 0 ):
            self.kill()
        if ( self.rect.bottom < - 40 ):
            self.kill()


if __name__ == '__main__':
    pygame.init()
    clock   = pygame.time.Clock()
    freq    = 30

    size = SCREEN_WIDTH, SCREEN_HEIGHT
    black = 0, 0, 0
    screen = pygame.display.set_mode(size)
    background = pygame.image.load("./figs/earth.png")

    shuttle = Ship("./figs/shuttle.png", (SCREEN_WIDTH/2,SCREEN_HEIGHT/2),
                   0.2, 10, 0.5, GRAVITY)

    while 1:
        clock.tick(freq)
        for event in pygame.event.get([pygame.QUIT,pygame.MOUSEBUTTONUP,pygame.MOUSEBUTTONDOWN]):
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_RIGHT]):
            Fd = THRUST
        else:
            Fd = 0
        if (keys[pygame.K_LEFT]):
            Fe = THRUST
        else:
            Fe = 0
        pygame.event.clear()

        # Update actors
        shuttle.update(1/freq, Fd, Fe)

        # Update screen
        screen.fill(black)
        screen.blit(background,(SCREEN_WIDTH/3,SCREEN_HEIGHT/3))
        screen.blit(shuttle.surf, shuttle.rect)
        pygame.display.flip()
        print("FPS: %0.2f" % clock.get_fps())
