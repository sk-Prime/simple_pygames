#pylint:disable=W0621
from geomdl import BSpline
from geomdl import utilities
from random import randint

import pymunk
import pymunk.pygame_util
import pygame,sys


pygame.init()
class Config():
    def __init__(self):
        self.fill = (20,20,30)
        self.width=2
        self.color = (255,180,0)
        self.dark=(50,50,60)
        self.bright = (70,90,80)
        self.brightdanger=(80,70,70)
        self.restrict=False
        self.restrict_zone=(160,200,560,600)
        self.show_points=True
        self.edit_mode = True
cfg=Config()

class Physics():
    def __init__(self,screen):
        self.draw_option = pymunk.pygame_util.DrawOptions(screen)
        self.space = None
        self.new()
        
    def new(self):
        self.space = pymunk.Space()
        self.space.gravity = 0, 200
    def add_seg(self,bspline):
        for i,p in enumerate(bspline[:-1]):
            segment = pymunk.Segment(self.space.static_body,p, bspline[i+1], 1)
            segment.elasticity = 1
            self.space.add(segment)
    
    def add_circle(self,x,y):
        body = pymunk.Body(mass=randint(1,10), moment=10)
        body.position = x,y
        circle = pymunk.Circle(body, radius=randint(10,50))
        circle.elasticity = randint(1,9)/10
        circle.color = (randint(0,255),randint(0,255),randint(0,255),255)
        self.space.add(body,circle)
        
    def run(self):
        self.space.debug_draw(self.draw_option)
        self.space.step(0.01)
        
class Spline():
    def __init__(self,degree=2):
        self.degree=degree
        self.curve = BSpline.Curve()
        self.curve.degree = degree
        
        self.points = []

    def draw(self,points):
        self.curve.ctrlpts = points
        self.curve.knotvector = utilities.generate_knot_vector(self.curve.degree, len(self.curve.ctrlpts))
        #self.curve.vis = VisMPL.VisCurve3D()
        self.points=self.curve.evalpts
        
    def set_degree(self,d):
        self.curve.degree = d
        self.degree=d
        
class Canvas():
    def __init__(self,screen):
        self.screen = screen
        self.curve = Spline()
        self.physics = Physics(self.screen)
        #self.physics.add_circle(400,700)
        self.ctrl_points=[]
        self.count=0
        self.selected=None
        self.move_point=False
        self.add_mode=0
        
        self.add_button = (20,460,50,20)
        self.del_button = (90,460,50,20)
        self.sel_button = (160,460,50,20)
        self.hide_button = (230,460,50,20)
        self.play_button = (300,460,50,20)
        
        self.edit_button = (20,460,50,20)
        
    def add_points(self,xy):
        self.ctrl_points.append(xy)
        
    def button_render(self):
        if cfg.edit_mode:
            if self.add_mode:
                pygame.draw.rect(self.screen,cfg.bright,self.add_button)
            else:
                pygame.draw.rect(self.screen,cfg.dark,self.add_button)
            if self.selected!=None:
                pygame.draw.rect(self.screen,cfg.bright,self.sel_button)
                pygame.draw.rect(self.screen,cfg.brightdanger,self.del_button)
            pygame.draw.rect(self.screen,cfg.dark,self.hide_button)
            pygame.draw.rect(self.screen,cfg.dark,self.play_button)
        else:
            pygame.draw.rect(self.screen,cfg.dark,self.edit_button)
            
            
    def render(self):
        if cfg.edit_mode:
            if cfg.show_points:
                if self.count>=2:
                    pygame.draw.lines(self.screen,(100,100,100),0,self.ctrl_points)
                for i,point in enumerate(self.ctrl_points):
                    if i==0:
                        pygame.draw.circle(self.screen,(0,140,200),point,5)
                    elif i==self.selected:
                        pygame.draw.circle(self.screen,(20,200,80),point,5)
                    else:
                        pygame.draw.circle(self.screen,(140,140,140),point,5)
            if self.count>=self.curve.degree+1:
                pygame.draw.lines(self.screen,cfg.color,0,self.curve.points,width=cfg.width)
        self.button_render()
        
    def region(self,button,x,y):
        bx,by,brx,bry=button
        if bx<x<bx+brx and by<y<by+bry:
            return True
        return False
        
    def select(self,x,y,r=10):
        if cfg.edit_mode:
            can_add=True
            if self.region(self.add_button,x,y):
                self.add_mode=not self.add_mode
                can_add=False
            elif self.region(self.sel_button,x,y):
                self.selected=None
                can_add=False
                
            elif self.region(self.hide_button,x,y):
                cfg.show_points= not cfg.show_points
                self.selected=None
                can_add=False
                
            elif self.region(self.play_button,x,y):
                cfg.show_points= False
                self.selected=None
                self.add_mode=False
                can_add=False
                cfg.edit_mode = False
                self.physics.add_seg(self.curve.points)
                
            elif self.region(self.del_button,x,y):
                if self.selected:
                    self.ctrl_points.pop(self.selected)
                    self.count-=1
                    self.selected=None
                    can_add=False
                    if self.count>=self.curve.degree+1:
                        self.curve.draw(self.ctrl_points)
            elif self.count:
                for i,points in enumerate(self.ctrl_points):
                    px,py = points
                    if px-r<x<px+r and py-r<y<py+r:
                        self.selected=i
                        self.move_point=True
                        can_add=False
                        break
            if self.add_mode and can_add:
                self.count+=1
                if self.selected!=None:
                    xpoint,_=self.ctrl_points[self.selected]
                    if xpoint>x:
                        self.ctrl_points.insert(self.selected,(x,y))
                    else:
                        self.ctrl_points.insert(self.selected+1,(x,y))
           
                else:
                    self.ctrl_points.append((x,y))
                if self.count>=self.curve.degree+1:
                    self.curve.draw(self.ctrl_points)
                
        else:
            if self.region(self.edit_button,x,y):
                self.physics.new()
                cfg.edit_mode = True
            else:
                self.physics.add_circle(x,y)
        
                    
    def move(self,xy):
        if self.move_point:
            self.ctrl_points.pop(self.selected)
            self.ctrl_points.insert(self.selected,xy)
            if self.count>=self.curve.degree+1:
                self.curve.draw(self.ctrl_points)
                
            return True
    def simulate(self):
        self.physics.run()

if __name__=="__main__":
    screen = pygame.display.set_mode((500,500))
    canvas = Canvas(screen)
    def update():
        screen.fill(cfg.fill)
        canvas.simulate()
        canvas.render()
        pygame.display.update()
                    
    update()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                canvas.select(*event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                canvas.move_point=False
            elif event.type == pygame.MOUSEMOTION:
                canvas.move(event.pos)
        update()
    
