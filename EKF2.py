from array import array
from cmath import polar
from dis import dis
from hashlib import new
from re import U
import pygame
import numpy as np
from pygame.locals import *
from math import *
pygame.init()

###### elipse
from matplotlib.patches import Ellipse
import matplotlib.pyplot as plt
# import matplotlib
# matplotlib.use('TkAgg')
import multiprocessing
######

display_width = 1800
display_height = 1600

gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('A bit Racey')

black = (0,0,0)
white = (255,255,255)

clock = pygame.time.Clock()
crashed = False
measured_positions_x=[]
measured_positions_y=[]
predicted_positions_x=[]
predicted_positions_y=[]
cov_width=[]
cov_hight=[]
points=[]
points.append([400,400])
#carImg = pygame.image.load('car_128.png')
points=[]
points.append([400,400])
center=np.array([[10],[10]])



position=np.array([[0],[0],[0]])
position_new_true = np.array([[0],[0],[0]])
position_polar=np.array([[0],[0]])
polar_measure=position_polar
position_measure=position
p_0=np.array([[0,0,0],[0,0,0],[0,0,0]])

def car(x,y):
    gameDisplay.blit(carImg, (x,y))

def convert_polar(p):

    rho = np.sqrt((p[0,0] - center[0,0])**2 + (p[1,0] - center[1,0])**2)
    phi = np.arctan2(p[1,0] - center[1,0], p[0,0] - center[0,0])# - p[2,0]
    new_pose=np.array([[rho],[phi]])

    return new_pose

def estimate_pose(position):
    global position_new_true 
    F=np.array([[1,0,0],[0,1,0],[0,0,1]])

    r=0.1
    l=0.3

    delta_t=1/8
    u_r=u_l=1

    if (dist([position[0,0],position[1,0]],center)<10):
        
        u_r=1
        u_l=0

    if (dist([position[0,0],position[1,0]],center)>11):
        
        u_r=0
        u_l=1

    G=np.array([[r*delta_t*cos(position[2,0]),0],[r*delta_t*sin(position[2,0]),0],[0,delta_t*r/l]])

    u=np.array([[(u_r+u_l)/2],[u_r-u_l]])
    
    position_new = np.matmul(F,position)+np.matmul(G,u) + np.array([[np.random.normal(0,0.001)],[np.random.normal(0,0.001)],[0]])*1/8
    position_new_true = np.matmul(F,position_new_true) + np.matmul(G,u)
    
    polar_pose = convert_polar(position_new)
    
    
    return position_new,polar_pose
    
x_change = 0


def update():
    global p_0 
    delta_t=1/8
    F=np.array([[1,0,0],[0,1,0],[0,0,1]])
    temp=np.matmul(F,p_0)
    Q=np.array([[0.01,0,0],[0,0.1,0],[0,0,0]])*1/8

    p_new=np.matmul(temp,F.transpose())+Q

    p_0=p_new
    

def measurement():
    global position_measure
    global position_new_true
    global position
    global polar_measure
        
    R = np.asarray([[np.random.normal(0,0.001)],[np.random.normal(0,0.001)]])
    
    Z = convert_polar(position_new_true) + R

    polar_measure = Z
    
    
def correction():
    global p_0
    global position_new
    
    rho = np.sqrt((position[0,0] - center[0,0])**2 + (position[1,0] - center[1,0])**2)
    phi = np.arctan2(position[1,0] - center[1,0], position[0,0] - center[0,0])

    x1 = (position[0,0] - center[0,0])/rho
    y1 = (position[1,0] - center[1,0])/rho
    
    x2 = -1*(position[1,0] - center[1,0])/(rho**2)
    y2 = 1*(position[0,0] - center[0,0])/(rho**2)
    
    #H=np.array([[1,0],[0,1]])
    H=np.array([[x1,y1,0],[x2,y2,-1]])

    R=np.array([[0.1,0],[0,0.01]])

    temp1=np.matmul(p_0,H.transpose())
    temp2=np.matmul(np.matmul(H,p_0),H.transpose()) + R
    
    k = np.matmul(temp1,np.linalg.inv(temp2)) 
    print(temp1)
    print(temp2)
    print(k)
#    k = temp1/temp2
    k[np.isnan(k)] = 0

    return H,k
    
def update_final(H,K):
    global p_0
    global position
    global position_polar


    p_0=np.matmul((np.identity(3)-np.matmul(K,H)),p_0)
    K = [[K[0,0],K[0,1]],[K[1,0],K[1,1]]]
    
    position_polar = position_polar + np.matmul( K , (polar_measure - position_polar) )
    #position_polar = position_polar

    
    Pose = np.array([center[0,0] + [position_polar[0,0]*cos(position_polar[1,0])], center[1,0] + [position_polar[0,0]*sin(position_polar[1,0])]])

    position[0,0] = Pose[0,0]
    position[1,0] = Pose[1,0]
#    position[0,0] = (position_polar[0,0]*cos(position_polar[1,0]))
    #position[1,0] = (position_polar[0,0]*sin(position_polar[1,0]))
    #position[2,0] = position_polar[1,0]
 #   print("PPPP: ", position)

t=1   
while not crashed:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            crashed = True

        ############################
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                x_change = -5
            elif event.key == pygame.K_RIGHT:
                x_change = 5
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                x_change = 0
        ######################

    position,position_polar=estimate_pose(position)
    
    update()
    
    if(t%8==0):
         measurement()
         H_new,K_new=correction()
         update_final(H_new,K_new)

    WHITE=(255,255,255)
    BLUE=(0,0,255)
    RED=(255,0,0)
    GREEN=(0,255,0)
    
    gameDisplay.fill(WHITE)

    surface = pygame.Surface((320, 240))
    red = (180, 50, 50)
    size = (0, 0, p_0[0,0]*2000, 2000*p_0[1,1])
    # pygame.draw.ellipse(gameDisplay, red, size)
    size = (position[0,0]*1000+400-(p_0[0,0]*2000)/2, position[1,0]*1000+400-(2000*p_0[1,1])/2, p_0[0,0]*2000, 2000*p_0[1,1])
    pygame.draw.ellipse(gameDisplay, red, size,1)    
    
    Pose = np.array([center[0,0] + [position_polar[0,0]*cos(position_polar[1,0])], center[1,0] + [position_polar[0,0]*sin(position_polar[1,0])]])
    Pose_measure = np.array([center[0,0] + [polar_measure[0,0]*cos(polar_measure[1,0])], center[1,0] + [polar_measure[0,0]*sin(polar_measure[1,0])]])

    pygame.draw.polygon(gameDisplay, BLUE,
                        [[position[0,0]*1000+400,position[1,0]*1000+400],[position[0,0]*1000+390,position[1,0]*1000+390] ,
                        [position[0,0]*1000+400,position[1,0]*1000+410]])
    # pygame.draw.rect(gameDisplay,BLUE,(400+1000*(Pose[0,0]),400+1000*Pose[1,0],10,10))
    pygame.draw.rect(gameDisplay,GREEN,(400+1000*(Pose_measure[0,0]),400+1000*(Pose_measure[1,0]),10,10))
    points.append([position[0,0]*1000+400,position[1,0]*1000+400])
    pygame.draw.lines(gameDisplay,RED,False,points,5) 
    pygame.display.update()
    clock.tick(8)
    measured_positions_x.append(Pose_measure[0,0])
    measured_positions_y.append(Pose_measure[1,0])
    predicted_positions_x.append(Pose[0,0])
    predicted_positions_y.append(Pose[1,0])
    cov_hight.append(p_0[0,0])
    cov_width.append(p_0[1,1])
    t+=1

plt.plot(measured_positions_x,label='x values')
plt.plot(measured_positions_y,label='y values')
plt.xlabel("iteation")
plt.ylabel("value")
plt.legend()
plt.show()
plt.plot(predicted_positions_x,label='x values')
plt.plot(predicted_positions_y,label='y values')
plt.xlabel("iteation")
plt.ylabel("value")
plt.legend()
plt.show()
plt.plot(cov_hight,label='covariance of x values')
plt.plot(cov_width,label='covariance y values')
plt.xlabel("iteation")
plt.ylabel("value")
plt.legend()
plt.show()
pygame.quit()
quit()
