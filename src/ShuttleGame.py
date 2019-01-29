import sys, pygame, math, time, threading

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

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
            thrustLock.acquire()
            fd = lib.Fd
            fe = lib.Fe
            thrustLock.release()

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

            resultLock.acquire()
            lib.x = int(self.z1[0])
            lib.y = int(self.z3[0])
            lib.theta = (self.z5[0]*180/math.pi)
            resultLock.release()
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
        thrustLock.acquire()
        if (keys[pygame.K_RIGHT]):
            lib.Fd = lib.thrust
        else:
            lib.Fd = 0
        if (keys[pygame.K_LEFT]):
            lib.Fe = lib.thrust
        else:
            lib.Fe = 0
        thrustLock.release()
        pygame.event.clear()

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
