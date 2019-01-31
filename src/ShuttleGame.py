import os, sys, pygame, math, time, threading

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

thrustLock = threading.Lock()
resultLock = threading.Lock()

class lib(object):
    def __init__(self):
        self.Fd = 0
        self.Fe = 0
        self.x = 0
        self.y = 0
        self.theta = 0
        self.thrust = 30
        self.gravity = 90

lib = lib()


class GameObject( pygame.sprite.Sprite ):
    """
    Esta é a classe básica de todos os objetos do jogo.

    Para não precisar se preocupar com a renderização, vamos fazer a
    classe de forma que ela seja compatível com o RenderPlain, que já possui
    uma função otimizada para renderização direta sobre a tela. Para isso,
    temos que ter três coisas nesta classe:

    1) Ser derivada de Sprite, isto é uma boa coisa, pois a classe Sprite
       cria várias facilidades para o nosso trabalho, como poder ser removida
       dos grupos em que foi colocada, inclusive o de Render, através de
       uma chamada a self.kill()

    2) Ter self.image. Uma vez que precisamos carregar uma imagem, isto só
       nos define o nome que daremos a imagem a ser renderizada.

    3) Ter self.rect. Esse retângulo conterá o tamanho da imagem e sua posição.
       Nas formas:
           rect = ( ( x, y ), ( width, height ) )
       ou
           rect = ( x, y, width, height )
       e ainda nos fornece algumas facilidades em troca, como o rect.move que
       já desloca a imagem a ser renderizada com apenas um comando.
    """
    def __init__(self, image, position, speed = (0,0), angle = 0, angle_speed = 0):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        if isinstance(self.image, str):
            self.image = pygame.image.load(self.image)

        self.rect  = self.image.get_rect()
        screen     = pygame.display.get_surface()
        self.area  = screen.get_rect()

        self.set_pos(position)
        self.set_speed(speed)
        self.set_angle(angle)       # angle in rads
        self.set_angle_speed(angle_speed)

    def update(self, dt):
        move_speed = (self.speed[0] * dt, self.speed[1] * dt)
        self.rect  = self.rect.move( move_speed )
        set_angle((self.angle_speed * dt * 180/math.pi) % 360)

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
        return self.rect.center

    def set_pos(self, pos):
        self.rect.center = pos

    def set_angle(self, angle):     # angle must be in radians
        self.angle = angle
        rot_image(self.angle * 180/math.pi)

    def set_angle_speed(self, angle_speed):
        self.angle_speed = angle_speed

    def get_angle_speed(self):
        return self.angle_speed

    def get_size(self):
        return self.image.get_size()

    def rot_image(self, angle):
        """rotate an image while keeping its center"""
        rotated_image = pygame.transform.rotate(self.image, angle)
        rot_rect = rotated_image.get_rect(center = self.get_pos())
        self.rect = rot_rect


class Ship(GameObject):
    def __init__(self, image, position, m = 1, I = 1, l = 1, g = 9.81):
        GameObject.__init__(self, image, position)
        self.m = m
        self.I = I
        self.l = l
        self.g = g

    def update(self, dt, fd = 0, fe = 0):
        move_speed = (self.speed[0] * dt, self.speed[1] * dt)
        self.rect  = self.rect.move( move_speed )
        set_angle((self.angle_speed * dt) % 2*math.pi)

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


class shuttleDynamics(threading.Thread):
    """ Thread implementing the shuttle dynamics """
    def __init__(self, T=1, m=1, I=1, l=1, g=9.81):
        threading.Thread.__init__(self)
        self.m = m
        self.I = I
        self.l = l
        self.g = g
        self.T = T
        self.z1 = [SCREEN_WIDTH/2, 0]   # x position
        self.z2 = [0,0]                 # x velocity
        self.z3 = [SCREEN_HEIGHT/2, 0]  # y position
        self.z4 = [0,0]                 # y velocity
        self.z5 = [0,0]                 # theta position
        self.z6 = [0,0]                 # theta velocity
        self.isActive = True            # active flag
        self.start()

    def run(self):
        while self.isActive:
            with thrustLock:
                fd = lib.Fd
                fe = lib.Fe

            self.z1[1] = (self.z2[0]*self.T+self.z1[0]) % SCREEN_WIDTH
            self.z2[1] = (-math.sin(self.z5[0])/self.m)*(fd+fe)*self.T+self.z2[0]

            self.z3[1] = (self.z4[0]*self.T+self.z3[0]) % SCREEN_HEIGHT
            self.z4[1] = (-(math.cos(self.z5[0])/self.m)*(fd+fe)+self.g)*self.T + self.z4[0]

            self.z5[1] = (self.z6[0]*self.T+self.z5[0]) % (2*math.pi)
            self.z6[1] = (self.l/self.I*(fd-fe))*self.T+self.z6[0]

            self.z1[0] = self.z1[1]
            self.z2[0] = self.z2[1]
            self.z3[0] = self.z3[1]
            self.z4[0] = self.z4[1]
            self.z5[0] = self.z5[1]
            self.z6[0] = self.z6[1]

            with resultLock:
                lib.x = int(self.z1[0])
                lib.y = int(self.z3[0])
                lib.theta = (self.z5[0]*180/math.pi)
            time.sleep(self.T)


def rot_center(image, centro, angle):
    """rotate an image while keeping its center"""
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = rot_image.get_rect(center = centro)
    return rot_image,rot_rect


if __name__ == '__main__':
    pygame.init()

    size = SCREEN_WIDTH, SCREEN_HEIGHT
    black = 0, 0, 0
    T = 0.01
    screen = pygame.display.set_mode(size)

    background = pygame.image.load("./figs/earth.png")
    nave = pygame.image.load("./figs/shuttle.png")
    naverect = nave.get_rect(center = (SCREEN_WIDTH/2,SCREEN_HEIGHT/2))

    shuttleDynamics = shuttleDynamics(0.02, 0.2, 10, 1, lib.gravity)

    while 1:
        for event in pygame.event.get([pygame.QUIT,pygame.MOUSEBUTTONUP,pygame.MOUSEBUTTONDOWN]):
            if event.type == pygame.QUIT:
                shuttleDynamics.isActive = False
                pygame.quit()
                sys.exit()
        keys = pygame.key.get_pressed()
        with thrustLock:
            if (keys[pygame.K_RIGHT]):
                lib.Fd = lib.thrust
            else:
                lib.Fd = 0
            if (keys[pygame.K_LEFT]):
                lib.Fe = lib.thrust
            else:
                lib.Fe = 0
        pygame.event.clear()

        with resultLock:
            nave_rot,naverect = rot_center(nave,naverect.center,lib.theta)
            naverect.centerx = lib.x
            naverect.centery = lib.y
        if naverect.left < 0 or naverect.right > SCREEN_WIDTH:
            pass
        if naverect.top < 0 or naverect.bottom > SCREEN_HEIGHT:
            pass

        screen.fill(black)
        screen.blit(background,(SCREEN_WIDTH/3,SCREEN_HEIGHT/3))
        screen.blit(nave_rot, naverect)
        pygame.display.flip()
        time.sleep(T)
