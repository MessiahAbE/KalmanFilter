from cmath import sin
from hashlib import new
from math import cos
from re import U
import pygame
import numpy as np
from pygame.locals import *
import math
pygame.init()

display_width = 1000
display_height = 2000

gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('A bit Racey')

black = (0,0,0)
white = (255,255,255)

clock = pygame.time.Clock()
crashed = False
carImg = pygame.image.load('car_128.png')
angle1 = math.radians(90)
center=np.array([[10],[10]])

position=np.array([[100],[400],[0]])
# position_measure=np.array([[-1],[-1]])
# ppp
polar_pose=np.array([[-1],[-1]])
position_measure=position
position_measure_polar=np.array([[-1],[-1]])
t=0
p_0=np.array([[0.1,0],[0,0.1]])
def car(x,y):
    gameDisplay.blit(carImg, (x,y))

def estimate_pose(position):
    F=np.array([[1,0,0],[0,1,0],[0,0,1]])
    # u_r=np.random.normal(0,0.1)
    # u_l=np.random.normal(0,0.15)
    global position_cart
    r=0.1
    l=0.3
    delta_t=1/8
    G=np.array([[r*cos(30)*delta_t,0],[r*sin(30)*delta_t,0],[0,delta_t]])

    u=np.array([[1],[0]])
    G1=np.matmul(np.abs(G),u)


    position_new=np.matmul(F,position)+G1+np.array([[np.random.normal(0,0.1)],[np.random.normal(0,0.1)],[np.random.normal(0,0.01)]])
    # position_cart=np.matmul(G,u)
    position=position_new
    x=position_new[0,0]*position_new[2,0]
    y=position_new[1,0]*position_new[2,0]
    temp=np.array([[x],[y]])
    print(math.dist(temp,center))
    
    polar_pose=np.array([[math.dist(temp,center)],[position_new[2,0]]])
    
    
    return polar_pose
# x =  (0)
# y = (0)
x_change = 0
# car_speed = 0


def update():
    global p_0 
    delta_t=1/8
    F=np.array([[1,0],[0,1]])
    temp=np.matmul(F,p_0)
    Q=np.array([[0.1*0.1,0],[0,0.1*0.1]])*1/8
    p_new=temp*F.transpose()+Q
    
    p_0=p_new

def measurement():
    global position_measure
    H=np.array([[1,0,0],[0,2,0],[0,0,0]])
    
    ########???????????
    Z=np.matmul(H,position_measure)
    # ppppp
    
    position_measure=Z

    
    x=position_measure[0,0]*position_measure[2,0]
    y=position_measure[1,0]*position_measure[2,0]
    temp=np.array([[x],[y]])    
    position_measure_polar=np.array([[math.dist(temp,center)],[Z[2,0]]])

def correction():
    
    x=position_measure[0,0]*position_measure[2,0]
    y=position_measure[1,0]*position_measure[2,0]
    temp=np.array([[x],[y]])
    
    H=np.array([[temp[0,0]/math.dist(temp,center),temp[1,0]/math.dist(temp,center)],[temp[0,0]/(math.dist(temp,center)*math.dist(temp,center)),temp[1,0]/(math.dist(temp,center)*math.dist(temp,center))]])

    R=np.array([[0.1,0],[0,0.01]])
    temp1=np.matmul(p_0,H.transpose())
    temp2=np.matmul(np.matmul(H,p_0),H.transpose())+R

    temp1[np.isnan(temp1)] = 0
    temp2[np.isnan(temp2)]=0
    k=temp1/temp2
    return H,k
def update_final(H,K):
    global p_0
    global position
    global polar_pose
    p_0=np.matmul((np.identity(2)-np.matmul(K,H)),p_0)

    # a = array([[1, 2, 3], [0, 3, NaN]])

    K[np.isnan(K)] = 0

    
    # H[np.isnan[H]]=0

    polar_pose=polar_pose+np.matmul(K,(position_measure_polar-np.matmul(H,polar_pose)))
    print(polar_pose)
    # ppppp
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
    ##
    # position[0,0] += x_change

    polar_pose=estimate_pose(position)
    # position=estimate_pose(position)
    update()
    
    # print(position)
    if(t%8==0):

        measurement()
        H_new,K_new=correction()
        update_final(H_new,K_new)
# #    ##         
    f=open("position.txt","a")
    gameDisplay.fill(white)
    # WHITE=(255,255,255)
    # BLUE=(0,0,255)

    # # gameDisplay.fill(WHITE)

    # pygame.draw.rect(gameDisplay,BLUE,(position[0,0],position[1,0],20,20))
    # car(position_measure[0,0],position_measure[1,0])
    # print(position_measure)

    # # pygame.draw.rect(gameDisplay, (255,0,0),  (position[0,0],position[1,0], 0.0001, 0.0001))
    pygame.display.update()
    # clock.tick(60/8)
    t+=1
pygame.quit()
quit()