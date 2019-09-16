#!/usr/bin/python3
import pygame
import math

pygame.init()
infos = pygame.display.Info()

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
GREEN = (  0, 255,   0)
RED   = (255,   0,   0)
GRAY  = (168, 168, 168)

#WIDTH = 900
#HEIGHT = 900
WIDTH  = int( 0.5 * infos.current_w ) # get screen width
HEIGHT = int( 0.5 * infos.current_h )
size = (WIDTH,HEIGHT)

CX = int(WIDTH/2)  # center's X coordinate
CY = int(HEIGHT/2)

gFactor  = 5
friction = 0.05
deltaT   = 0.1  #time increment per frame
theta0   = math.pi/2  #initial gravity angle
step     = 0.12  #gravity angle per frame
done     = False  #boolean for main loop

#Keyboard boolean
leftDown  = False
upDown    = False
rightDown = False
downDown  = False
spaceDown = False

pygame.display.set_caption("Gravity")

#Font initilization
fontpath = pygame.font.match_font('Monospace')
font = pygame.font.Font(fontpath, 36)

screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

#Sound and pictures
sound = pygame.mixer.Sound("ping.ogg")
arrowPic = pygame.image.load("arrow2.png")

class Gravity:
    def __init__(self,a):
        self._r0 = 9.81
        self._r = 9.81
        self._theta = theta0
        self._set_x()
        self._set_y()
        self._w = 5
        self.arrows = a
    def _set_theta(self,t):
        self._theta = t
        self._set_x()
        self._set_y()
    def _set_r(self,r):
        self._r = r
        self._set_x()
        self._set_y()
    def _set_x(self):
        self._x = int(self._r*math.cos(self._theta))
    def _set_y(self):
        self._y = int(self._r*math.sin(self._theta))
    def _get_g(self):
        return (self._r/self._r0,self._theta,self._x,self._y)
    def dtheta(self,e):
        self._set_theta(self._theta + e)
        return self._get_g()
    def dr(self,f):
        self._set_r(self._r*f)
        return self._get_g()
#    def update(self):
        #ax = int(0.4*self._r*math.cos(self._theta+0.2))
        #ay = int(0.4*self._r*math.sin(self._theta+0.2))
        #bx = int(0.4*self._r*math.cos(self._theta-0.2))
        #by = int(0.4*self._r*math.sin(self._theta-0.2))
#        self._set_x()
#        self._set_y()
    def draw(self,screen):
        ax = int(0.4*self._r*math.cos(self._theta+0.2))
        ay = int(0.4*self._r*math.sin(self._theta+0.2))
        bx = int(0.4*self._r*math.cos(self._theta-0.2))
        by = int(0.4*self._r*math.sin(self._theta-0.2))
        self._set_x()
        self._set_y()
        pygame.draw.line(screen, WHITE, [CX-self._x/2,CY-self._y/2], [CX+self._x/2, CY+self._y/2], self._w)
        pygame.draw.line(screen, WHITE, [CX+ax,CY+ay], [CX+self._x/2, CY+self._y/2], self._w)
        pygame.draw.line(screen, WHITE, [CX+bx,CY+by], [CX+self._x/2, CY+self._y/2], self._w)
    def display(self):
        textG = font.render("g="+str(math.floor(100*self._r)/100)+" m.s-2",False,(255,255,255))
        #textG = font.render(str(self._r),False,(255,255,255))
        screen.blit(textG,[50,40])
        
class Body(pygame.sprite.Sprite):
    def __init__(self,w,h):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([w,h])
        self.image.fill(WHITE)
        self.image.set_colorkey(WHITE)
        self.preImage = self.image
        #self.preImage.fill(WHITE)
        #self.preImage.set_colorkey(WHITE)
        self.rect = self.image.get_rect()

        self._mass = 1
        self._ax = 0
        self._ay = 0
        self._vx = 0
        self._vy = 0
        self._px = CX
        self._py = CY

    def update(self,a,dt):
        a1x = gFactor*a[0] - friction * self._vx / self._mass
        a1y = gFactor*a[1] - friction * self._vy / self._mass
        v1x = self._vx + (self._ax+a1x)/2 * dt
        v1y = self._vy + (self._ay+a1y)/2 * dt
        self._px = (self._px + self._vx * dt + (self._ax+a1x)/4 * dt*dt) % WIDTH
        self._py = (self._py + self._vy * dt + (self._ay+a1y)/4 * dt*dt) % HEIGHT
        self._ax = a1x
        self._ay = a1y
        self._vx = v1x
        self._vy = v1y
        self.rect.x = self._px - self.rect.w/2
        self.rect.y = self._py - self.rect.h/2
    def vChoc(self):
        self._vx *= -1
    def hChoc(self):
        self._vy *= -1
    def kineticE(self):
        e = "E="+str(math.floor(100*0.5*self._mass*(self._vx*self._vx+self._vy*self._vy))/100)
        text = font.render(e,False,(255,255,255))
        screen.blit(text,[WIDTH-250,40])
    def grow(self, factor):
        self.image = pygame.Surface([self.rect.w * factor, self.rect.h * factor])
        self.image.fill(WHITE)
        self.image.set_colorkey(WHITE)
        self.preImage = self.image
        self.rect = self.image.get_rect()
        self._mass = self._mass * factor * factor;

class Marble(Body):
    def __init__(self,r, color):
        Body.__init__(self,2*r,2*r)
        #pygame.draw.ellipse(self.image, color, [0, 0, 2*r, 2*r])
        self._color = color
        self.make()
    def make(self):
        pygame.draw.ellipse(self.image, self._color, self.rect)
    def grow(self,factor):
        Body.grow(self,factor)
        self.make()
        
class Wall(pygame.sprite.Sprite):
    def __init__(self,w,h,x,y,color,vert):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([w,h])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vert = vert
        
class Arrow(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.preImage = arrowPic.convert()
    def update(self,r,theta):
        self.image = pygame.transform.rotozoom(self.preImage, -theta*180/math.pi,r)
        #self.image = self.preImage
        #self.image.fill(GREEN)
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = CX - self.rect.w/2
        self.rect.y = CY - self.rect.h/2

arrow = Arrow()
wallTop    = Wall(WIDTH-40,5,20,20,RED,False)
wallBottom = Wall(WIDTH-40,5,20,HEIGHT-25,RED,False)
wallLeft   = Wall(5,HEIGHT-50,20,25,RED,True)
wallRight  = Wall(5,HEIGHT-50,WIDTH-25,25,RED,True)
marble = Marble(20,GREEN)

world   = pygame.sprite.Group()
marbles = pygame.sprite.Group()
arrows  = pygame.sprite.Group()

gravity = Gravity(arrows)

g = gravity.dtheta(theta0);

world.add(wallTop)
world.add(wallBottom)
world.add(wallLeft)
world.add(wallRight)
arrows.add(arrow)
marbles.add(marble)

while not done:
    #pixar = pygame.PixelArray(screen)    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                leftDown = True
            if event.key == pygame.K_RIGHT:
                rightDown = True
            if event.key == pygame.K_UP:
                upDown = True
            if event.key == pygame.K_DOWN:
                downDown = True
            if event.key == pygame.K_SPACE:
                spaceDown = not spaceDown
                if(spaceDown):
                    gravity._set_r(0)
                else:
                    gravity._set_r(gravity._r0)
                g = gravity._get_g()
            if event.key == pygame.K_i:
                marble.grow(1.5)
            if event.key == pygame.K_j:
                marble.grow(0.67)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                leftDown = False
            if event.key == pygame.K_RIGHT:
                rightDown = False
            if event.key == pygame.K_UP:
                upDown = False
            if event.key == pygame.K_DOWN:
                downDown = False

    if(leftDown):
        g = gravity.dtheta(-step)
    if(rightDown):
        g = gravity.dtheta(step)
    if(upDown):
        g = gravity.dr(1.01)
    if(downDown):
        g = gravity.dr(0.99)

    marble.update((g[2],g[3]),deltaT)
    arrow.update(g[0],g[1])
    
    walls_hit = pygame.sprite.spritecollide(marble,world,False)

    for wall in walls_hit:
        if wall.vert:
            marble.vChoc();
        else:
            marble.hChoc();
        #sound.play()

    screen.fill(BLACK)
    #pygame.draw.rect(screen, GREEN, [100,100,200,200], 0)
    #arrows.draw(screen)
    gravity.draw(screen)
    marbles.draw(screen)
    world.draw(screen)
    gravity.display()
    marble.kineticE()
    pygame.display.flip()
    clock.tick(60)
