# -*- coding: utf-8 -*-
"""
Created on Sat May 28 20:07:32 2022

@author: ibro
"""
import random
import pygame
import time
import math
from math import exp, sqrt
import numpy as np
import matplotlib.pyplot as plt
################################################



#################################################
"""  General fucntion """
def distance(x1, y1, x2, y2):
    return sqrt( (x2-x1)**2 + (y2-y1)**2)

def get_obj_size(world, obj_class):
    return len([obj for obj in world if isinstance(obj, obj_class)])

def get_population_sizes(world, obj_types):
    populations = dict()
    for obj in obj_types.keys():
        populations[obj] = get_obj_size(world, obj)        
    return populations

def is_close(x1, y1, x2, y2, Vision_range):
    Distance = distance(x1, y1, x2, y2)
    if Distance <= Vision_range:
        return True
    return False
def energy_reDistibution(percentage):
    # 0.2 0.5
    portion1 = random.uniform(0,1)
    portion2 = random.uniform(portion1, 1)
    
    portion3 = 1 - portion2   
    portion2 -= portion1
    print(portion1+portion2 + portion3)
    return percentage * np.array([portion1, portion2, portion3])
#################################################
class Objects(pygame.sprite.Sprite):
    def __init__(self, world, coord):
        super(Objects, self).__init__()
        pygame.sprite.Sprite.__init__(self)
        self.world = world
        self.birth_place = coord
        
    def generate_object(self, object_type, size):
        #self.Typo = object_type
        self.x = self.birth_place[0]
        self.y = self.birth_place[1]
        self.size = size
        self.width = int(self.size[0] * self.world.proportion )
        self.height = int(self.size[1] * self.world.proportion )
        
        image = f"images/{object_type}.png"
        self.Image0 = pygame.image.load(image)
        self.Image = pygame.transform.scale(self.Image0, (self.width, self.height))
        self.rect = pygame.rect.Rect((self.x, self.y, self.width, self.height))
        self.rect.center = (self.x, self.y)
    """
    def grow(self):
        self.width += self.increment
        self.height += self.increment
        if self.speed >0.3:
            self.speed -=self.increment*0.2
       # print(self.width)
        
        self.Image = pygame.transform.scale(self.Image0, (self.width, self.height))
        self.rect = pygame.rect.Rect((self.x, self.y, self.width, self.height))
    """  
        
    def is_eaten_from(self, obj):
        obj.survive = True
        obj.score +=1
       
        self.alive = False
        
    def check_energy(self):
        if self.energy <= 0:
            self.alive = False
            
    def get_position(self):
        return self.x, self.y

class Blob(Objects):# has World class as an input and the coordinate of the object in that world
    def __init__(self, world, coord ):
        super(Blob,self).__init__(world, coord)
        self.type = "Blob"
        self.initial_energy = 2000#10000->2000
        self.energy = self.initial_energy
        #self.energy_lose = 10
        
        #self.size_scaling = self.energy_lose# max 10
        #self.speed_scaling = 0.2*self.energy_lose# max 2
        #self.vision_scaling = 10*self.energy_lose# max 100
    
        
        self.Size = 1#0.1 * self.size_scaling# the first part is portion of energy and the second part is scaling
        self.speed = 1#0.7 * self.speed_scaling# the first part is portion of energy and the second part is scaling
        self.vision = 20#0.2 * self.vision_scaling# the first part is portion of energy and the second part is scaling
        self.energy_lose = self.Size**3 * self.speed**2 + self.vision/20# = 2
       # self.increment = 0.1
        self.size_blob = ( 160, 240) # this for window size
        self.world = world
        
        
        self.alive = True
        self.survive = False
        self.attention = False
        
       # self.mutation = 0.2
       # self.mutation_probability = 0.1
        self.attention_spot = random_attention()
        #print(world.world_height*random.uniform(0,1))
        self.attention_spot.x = self.world.world_width*random.uniform(0,1)
        self.attention_spot.y = self.world.world_height*random.uniform(0,1)
        self.obj_attention = {"food":None, "enemy":None}
        self.generate_object(self.type, self.size_blob)
        
        self.score = 0
        
   # def activate(self):
        
    def update(self, world, objs):
        neighbors = self.neighbors(objs)
        self.update_blob()
        if self.score < 2:
            self.act(neighbors)
            self.check_encounter(world, objs)
        else:
            self.go_home()
        
        self.check_energy()
       
        
    def neighbors(self, objs):
        return [obj for obj in objs if distance(self.x, self.y, obj.x, obj.y) <=self.vision and id(self)!=id(obj)]
    
    def update_blob(self):
        self.attention = False
        self.update_sight()
        self.explore() if random.random() <= 0.0001 else None
        if self.score == 0:
            self.energy -= self.energy_lose
        
    def explore(self):
        self.attention_spot.x = self.world.world_width *random.uniform(0,1)
        self.attention_spot.y = self.world.world_height *random.uniform(0,1)
        
    def act(self, objs):
        obj_distance = {"enemy": math.inf, "food": math.inf}
        flag = 0
        
        for obj in objs:
            dist = distance(self.x, self.y, obj.x, obj.y)
            in_sight = dist <= self.vision
            
            if in_sight:
                if isinstance(obj, Blob):
                 
                    obj_is_enemy = obj.Size/self.Size >=2
                    obj_is_food = self.Size/obj.Size >= 2
                    if obj_is_enemy and dist<=obj_distance["enemy"] and id(self)!=id(obj):
                    
                        obj_distance["enemy"] = dist
                        self.attention_on(obj, "enemy")
                        flag += 1
                        
                    
                    elif obj_is_food and dist <= obj_distance["food"] and id(self)!=id(obj):
                      
                        obj_distance["food"] = dist
                        self.attention_on(obj, "food")
                        flag += 1
                
                elif isinstance(obj, Apple) and dist <= obj_distance["food"] and id(self)!=id(obj):
                  
                    obj_distance["food"] = dist
                    self.attention_on(obj, "food")
                    flag += 1
                    
        
        if flag:
            if obj_distance["enemy"] <= obj_distance["food"]:
                location = self.obj_attention["enemy"]
                if location is not None:
                    self.attention_spot.x = location[0]
                    self.attention_spot.y = location[1]
                    self.reverse_direction()
                    
            elif obj_distance["food"] < obj_distance["enemy"]:
                location = self.obj_attention["food"]
                if location is not None:
                    self.attention_spot.x = location[0]
                    self.attention_spot.y = location[1]
        else:
            if np.sqrt((self.attention_spot.x-self.x)**2 + (self.attention_spot.y - self.y)**2) < 10:
                self.explore()
            
        
        self.move()
        
                    
    def attention_on(self, obj, Type):
        self.obj_attention[Type] = (obj.x, obj.y)
        self.attention = True
        
    def reverse_direction(self):
        self.attention_spot.x = self.x + (self.x - self.attention_spot.x)
        self.attention_spot.y = self.y + (self.y - self.attention_spot.y)
        
    def attention_direction(self):
        d = np.subtract((self.attention_spot.x, self.attention_spot.y),(self.x, self.y))
        d = d/np.linalg.norm(d)
        return d*self.speed
    
    def go_home(self):
        self.attention_spot.x = self.birth_place[0]
        self.attention_spot.y = self.birth_place[1]
        self.move()
        
    def move(self):
        dx = self.attention_direction()[0]
        dy = self.attention_direction()[1]
        
        self.x = (dx + self.x)#%self.world.world_width
        self.y = (dy + self.y)#%self.world.world_height
        if self.x >= self.world.world_width:
            self.x -= 2*dx
            self.reverse_direction()
        if self.y >= self.world.world_height:
            self.y -= 2*dy
            self.reverse_direction()
        
        self.rect.center = (self.x, self.y)
        
    def update_sight(self):
        for obj_name in self.obj_attention.keys():
            location = self.obj_attention[obj_name]
            if location is not None and distance(self.x, self.y, location[0], location[1]) <= self.vision:
                self.obj_attention[obj_name] = None
                
    def check_encounter(self, world, objs):
        for obj in objs:
            if self.rect.colliderect(obj):
                if type(obj) is Apple:
                    obj.is_eaten_from(self)
                    
                elif type(obj) is Blob and self.Size/obj.Size >=2:
                    obj.is_eaten_from(self)
                    
    def reproduce(self, birth_coord):
        #example of energy redistribution
        # 0.2 0.5 -> 0.3 0.4
        # 0.2 0.3 0.5->  0.3 0.1 0.6
        #-0.1 0.2 -0.1
        #replica = Blob(self.world, (self.x, self.y - (self.width + 5)))
        #energy_percentage = 0.1
        replica = Blob(self.world, birth_coord)
        #increment = energy_reDistibution(energy_percentage) - energy_reDistibution(energy_percentage)
        replica.speed = self.speed   + random.uniform(-0.5,0.5)
        replica.vision = self.vision + random.uniform(-0.5,0.5)
        replica.Size  = self.Size    + random.uniform(-0.5,0.5)
        replica.width = self.width   #+ increment[2] *self.size_scaling
        replica.height = self.height #+ increment[2] *self.size_scaling
        
        replica.energy_lose = replica.Size**3 * replica.speed**2 + replica.vision/20

        replica.Image = pygame.transform.scale(replica.Image0, (replica.width, replica.height))
        replica.rect = pygame.rect.Rect((replica.x, replica.y, replica.width, replica.height))
        
        return replica
    
"""
energy 10

"""    

class random_attention:
    x = -1
    y = -1
    
class Apple(Objects):
    def __init__(self, world, coord):
        super(Apple, self).__init__(world, coord)
        self.type = "Apple"
        self.size_apple = (64,80)
        self.Size = 1
        self.generate_object(self.type, self.size_apple)
        self.alive = True
    def update(self):
        pass
        

class World:
    def __init__(self, world):
        self.world_width = world[0]
        self.world_height = world[1]
        self.proportion = 0.1
        self.width_num = 50
        self.height_num = 50
        self.width_PortionSize = math.ceil(self.world_width/self.width_num) # s0 500/50 is equivalent to 500/55
        self.height_PortionSize = math.ceil(self.world_height/self.height_num)
        self.blobs = Blob.__subclasses__()
        self.replicas = []
        self.birth = "boundary" # "random"
        
        self.color = []
        self.coord = 0
        self.x = 0
        self.y = 0
        
    def generate_objects(self, object_types=None):
        self.fill_landscape()
        objects=[]
        for obj in object_types.keys():
            if obj == Apple:
                for apple in range(object_types[obj]):
                    objects.append(self.generate_apple())
            else: # if the obj == Blob
                if self.birth == "random":
                    X = self.world_width*random.random()
                    Y = self.world_height *random.random()          
                    objects += [obj(self, (X,Y) ) for i in range(object_types[obj])]
                
                elif self.birth == "boundary":
                    for i in range(object_types[obj]):
                        left_bound   = (1                                      ,       self.world_height *random.random())
                        right_bound  = (self.world_width-self.width_PortionSize,       self.world_height *random.random())
                        upper_bound  = (self.world_width *random.random()      ,                                        1)
                        lower_bound  = (self.world_width *random.random()      ,self.world_height-self.height_PortionSize)
                        boundary = [ upper_bound, lower_bound, left_bound, right_bound]
                        X_Y = random.choice(boundary)            
                        objects += [ obj(self, X_Y ) ]
            
        return objects
    
    def fill_landscape(self):
        for row in range(self.width_num):
            for col in range(self.height_num):
                self.color.append( (random.randint(75, 90), random.randint(110, 120), random.randint(40, 50)) )
                
        
    def generate_apple(self):
        return Apple(self, (self.world_width*random.random(),
                            self.world_height * random.random()))
    
    def update(self, world_objects):
        for obj in world_objects:
            if isinstance(obj, Blob):
                obj.update(self, world_objects)
            elif isinstance(obj, Apple):
                obj.update()
          
        
        world_objects = [obj for obj in world_objects if obj.alive]  
        
        """ This for to add apples with time"""
       # if random.random() <= 0.1:
         #   world_objects.append(self.generate_apple())
        
        world_objects += self.replicas
        #for i in range(5):
        self.replicas = []          
        return world_objects
    
    def new_day(self, world_objects, object_types ):
        world_objects = [obj for obj in world_objects if (isinstance(obj, Blob) and obj.alive and obj.survive )]
        replicas = []
        for obj in world_objects:
                
            left_bound   = (1                                      ,       self.world_height *random.random())
            right_bound  = (self.world_width-self.width_PortionSize,       self.world_height *random.random())
            upper_bound  = (self.world_width *random.random()      ,                                        1)
            lower_bound  = (self.world_width *random.random()      ,self.world_height-self.height_PortionSize)
            boundary = [ upper_bound, lower_bound, left_bound, right_bound]
            X_Y = random.choice(boundary)
            if obj.score == 2:
                replica = obj.reproduce(random.choice(boundary))
                replicas.append(replica)
            obj.x = X_Y[0]
            obj.y = X_Y[1]
            obj.energy = obj.initial_energy
            obj.score = 0
            obj.attention = False
            obj.survive = False
            
            
        for apple in range(object_types[Apple]):
            world_objects.append(self.generate_apple())
                
                                   
        
        return world_objects + replicas
            
    
            
        
                    
class EcoSystem:
    def __init__(self, world_width, world_height):
        self.w = world_width
        self.h = world_height
        super(EcoSystem,self).__init__()
        num_apples = 20
        num_blobs = 10
        self.object_types = {Apple: num_apples, Blob: num_blobs}
        
        self.eco_system = None
       # self.popSize_time = dict()
        self.iteration = 0
        self.past_size = 0
        self.system_objects = None
        
        self.stop = time.time()
        self.last_time = time.time()
        
        self.activate()
        
    def activate(self):
        self.eco_system = World((self.w, self.h))
        self.system_objects = self.eco_system.generate_objects(object_types=self.object_types)
        self.past_size = len(self.system_objects)
        
    def update(self,iterations):
        one_day_passed = ((iterations+1) %1000 == 0)
        #eco_system is a world with object and updating the system implies updating the objects of its world
        if one_day_passed:
            #print(self.object_types)
            #print(self.system_objects)
            for obj in self.system_objects:
                if isinstance(obj, Blob):
                    print(obj)
                    print(obj.Size)
                    print(obj.speed)
                    print(obj.vision)
            self.system_objects = self.eco_system.new_day(self.system_objects,object_types=self.object_types)
            
            #self.system_objects = self.eco_system.update(self.system_objects)
        else:
            self.system_objects = self.eco_system.update(self.system_objects)
            
    
  
    
"""
Parameter Review:
    -Day: is 1000 iteration
    -start population: blubs: 10, apples 20
    -initial energy is 800
    -energy lose = 1 => every blob can spend 80% of the day way scorching for food before it is home gain otherwise it dies
    -each blob can eat blobs that half the size and avoid the blobs that double the size
    -the size increase only with mutation however it can be made as a function of food intake
    -vision range in 10 and it changes only with mutation
    -mutation is invitabley every generation, however it can be given a probability
    -initial configuration 10 blobs and 20 apples. Apples are constant and renewed every day
    - size is inversely proportionate to speed
    summary:
        each blob start from the boundary scorching for food and losses energy every time step
        if the blob get to eat one food item, then it ensures survival to the next day
        if the blob runs out of energy before getting food, it dies
        and it stop losing energy in this particular day. Thus, after eating one food item
        the blob continue walking freely for the second food item that ensures reproduction
        if the blob gets the second item, it goes home 
        in the next day, only blobs that got two items get replicated
        in the replication, the mutation occurs
"""
       
window = pygame.display.set_mode((500, 500))
world_width, world_height = window.get_size()
#pygame.display.set_caption("EcoSystem")
Time = pygame.time.Clock()

runTime_speed = 60
display_world = True


blob_world = EcoSystem(world_width, world_height)
iteration = 0
while True:
    #print(iteration)
    if display_world:
        i = 0
        
        for row in range(blob_world.eco_system.width_num):
            for col in range(blob_world.eco_system.height_num):
                pygame.draw.rect(window,blob_world.eco_system.color[i],
                                 (blob_world.eco_system.width_PortionSize * row,
                                 blob_world.eco_system.height_PortionSize * col,
                                 blob_world.eco_system.width_PortionSize,
                                 blob_world.eco_system.height_PortionSize))
                i += 1
                
        [ window.blit(obj.Image, (obj.x, obj.y)) for obj in blob_world.system_objects ]
        
       
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                pygame.quit()
    
                
                
    blob_world.update(iteration)
    Day = "Day: "+ f"{int(iteration/1000 + 1)}"
    pygame.display.set_caption(Day)
    pygame.display.update()
    Time.tick(runTime_speed)
    iteration += 1