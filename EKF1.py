from hashlib import new
from re import U
import pygame
import numpy as np
from pygame.locals import *
from math import *

###### elipse
from matplotlib.patches import Ellipse
#import matplotlib.pyplot as plt
#import matplotlib
#matplotlib.use('TkAgg')
import multiprocessing
import matplotlib.pyplot as plt
######

pygame.init()

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
center=np.array([[10],[10]])
points=[]
points.append([400,400])
points_measure=[]
points_gt=[]
points_gt.append([400,400])
points_measure.append([400,400])


position=np.array([[0],[0],[0]])
position_measure=position
p_0=np.array([[0,0,0],[0,0,0],[0,0,0]])
position_new_true = np.array([[0,0,0],[0,0,0],[0,0,0]])
def car(x,y):
    gameDisplay.blit(carImg, (x,y))

def estimate_pose(position):
    global position_new_true
    F=np.array([[1,0,0],[0,1,0],[0,0,1]])

    r=0.1
    l=0.3
    delta_t=1/8
    u_r=u_l=1
    print(position)
    print(dist([position[0,0]*10,position[1,0]*10],center))
    if (dist([position[0,0],position[1,0]],center)<10):
        u_r=1
        u_l=0
    if (dist([position[0,0],position[1,0]],center)>11):
        u_r=0
        u_l=1
    G=np.array([[r*delta_t*cos(position[2,0]),0],[r*delta_t*sin(position[2,0]),0],[0,delta_t*r/l]])
    G_true = np.array([[r*delta_t*cos(position_new_true[2,0]),0],[r*delta_t*sin(position_new_true[2,0]),0],[0,delta_t*r/l]])

    u=np.array([[(u_r+u_l)/2],[u_r-u_l]])
    
    position_new=np.matmul(F,position)+np.matmul(G,u) + delta_t*np.array([[np.random.normal(0,0.01)],[np.random.normal(0,0.1)],[0]])
    position_new_true = np.matmul(F,position_new_true) + np.matmul(G_true,u)
     
    return position_new

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
    global position
    H=np.array([[1,0,0],[0,2,0],[0,0,1]])
    R=np.array([[0.05,0,0],[0,0.075,0],[0,0,0]])

    R=np.asarray([[np.random.normal(0,0.05)],[np.random.normal(0,0.075)],[0]])
    Z = np.matmul(H,position_new_true) + R
    position_measure = Z

    
def correction():
    global p_0
    H=np.array([[1,0,0],[0,2,0],[0,0,1]])
    R=np.array([[0.05,0,0],[0,0.075,0],[0,0,0]])

    temp1=np.matmul(p_0,H.transpose())
    temp2=np.matmul(np.matmul(H,p_0),H.transpose())+R

    k=temp1/temp2
    k[np.isnan(k)] = 0
  
    return H,k
def update_final(H,K):
    global p_0
    global position
    p_0=np.matmul((np.identity(3)-np.matmul(K,H)),p_0)
    H = np.array([[1,0,0],[0,2,0],[0,0,1]])
    position = position + np.matmul( K , (position_measure - np.matmul(H,position)) )


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

    position=estimate_pose(position)

    update()

    if(t%8==0):
        measurement()
        H_new,K_new=correction()
        update_final(H_new,K_new)
        

# # #    ##         
#     f=open("position.txt","a")
#     gameDisplay.fill(white)

    WHITE=(255,255,255)
    BLUE=(0,0,255)
    RED=(255,0,0)
    GREEN=(0,255,0)
    
    gameDisplay.fill(WHITE)
    
    surface = pygame.Surface((320, 240))
    red = (180, 50, 50)
    # size = (0, 0, p_0[0,0]*2000, 2000*p_0[1,1])
    pygame.draw.polygon(gameDisplay, BLUE,
                        [[position[0,0]*1000+400,position[1,0]*1000+400],[position[0,0]*1000+390,position[1,0]*1000+390] ,
                        [position[0,0]*1000+400,position[1,0]*1000+410]])

    size = (position[0,0]*1000+400-(p_0[0,0]*2000)/2, position[1,0]*1000+400-(2000*p_0[1,1])/2, p_0[0,0]*2000, 2000*p_0[1,1])
    pygame.draw.ellipse(gameDisplay, red, size,1)
    points.append([position[0,0]*1000+400,position[1,0]*1000+400])
    points_gt.append([position_new_true[0,0]*1000+400,position_new_true[1,0]*1000+400])
    points_measure.append([position_measure[0,0]*1000+400,(position_measure[1,0]/2)*1000+400])
    pygame.draw.lines(gameDisplay,BLUE,False,points,5)
    pygame.draw.lines(gameDisplay,GREEN,False,points_gt,5)
    pygame.draw.lines(gameDisplay,RED,False,points_measure,5)
    # pygame.draw.rect(gameDisplay,BLUE,(position[0,0]*1000+400,position[1,0]*1000+400,10,10))
    
    if(t%8==0):
        pygame.draw.rect(gameDisplay,RED,(position_measure[0,0]*1000+400,(position_measure[1,0]/2)*1000+400,10,10))
        pygame.draw.rect(gameDisplay,GREEN,(position_new_true[0,0]*1000+400,(position_new_true[1,0]/2)*1000+400,10,10))

    pygame.draw.rect(gameDisplay,RED,(position_measure[0,0]*1000+400,(position_measure[1,0]/2)*1000+400,10,10))
    pygame.draw.rect(gameDisplay,GREEN,(position_new_true[0,0]*1000+400,(position_new_true[1,0])*1000+400,10,10))
    measured_positions_x.append(position_measure[0,0])
    measured_positions_y.append(position_measure[1,0])
    predicted_positions_x.append(position[0,0])
    predicted_positions_y.append(position[1,0])
    cov_hight.append(p_0[0,0])
    cov_width.append(p_0[1,1])
    pygame.display.update()
    clock.tick(8)
    t+=1
plt.plot(predicted_positions_x,label='x values')
plt.plot(predicted_positions_y,label='y values')
plt.xlabel("iteation")
plt.ylabel("value")
plt.legend()
plt.show()
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
