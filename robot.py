from hashlib import new
from re import U
import pygame
import numpy as np
from pygame.locals import *
pygame.init()

display_width = 1800
display_height = 1600

gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('A bit Racey')

black = (0,0,0)
white = (255,255,255)

clock = pygame.time.Clock()
crashed = False
carImg = pygame.image.load('car_128.png')




position=np.array([[0],[0]])
position_measure=position
p_0=np.array([[0,0],[0,0]])
def car(x,y):
    gameDisplay.blit(carImg, (x,y))

def estimate_pose(position):
    F=np.array([[1,0],[0,1]])
    # u_r=np.random.normal(0,0.1)
    # u_l=np.random.normal(0,0.15)
    r=0.1
    delta_t=1/8
    G=np.array([[r/2*delta_t,r/2*delta_t],[r/2*delta_t,r/2*delta_t]])
    u=np.array([[1],[1]])
    
    position_new=np.matmul(F,position)+np.array([[np.random.normal(0,0.1)],[np.random.normal(0,0.15)]])
    return position_new
# x =  (0)
# y = (0)
x_change = 0
# car_speed = 0


def update():
    global p_0 
    delta_t=1/8
    F=np.array([[1,0],[0,1]])
    temp=np.matmul(F,p_0)
    Q=np.array([[0.1*0.1,0],[0,0.15*0.15]])*1/8
    # print(Q)
    p_new=temp*F.transpose()+Q
    
    p_0=p_new

def measurement():
    global position_measure
    H=np.array([[1,0],[0,2]])
    R=np.array([[0.05,0],[0,0.075]])
    ########???????????
    Z=np.matmul(H,position_measure)
    position_measure=Z
def correction():
    H=np.array([[1,0],[0,2]])
    R=np.array([[0.05,0],[0,0.075]])
    temp1=np.matmul(p_0,H.transpose())
    temp2=np.matmul(np.matmul(H,p_0),H.transpose())+R
    k=temp1/temp2
    return H,k
def update_final(H,K):
    global p_0
    global position
    p_0=np.matmul((np.identity(2)-np.matmul(K,H)),p_0)

    # a = array([[1, 2, 3], [0, 3, NaN]])
    K[np.isnan(K)] = 0

    position=position+np.matmul(K,(position_measure-np.matmul(H,position)))
    print(position)
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
    # print(estimate_pose(position))

    position=estimate_pose(position)
    update()
    # print(position)
    if(t%8==0):

        measurement()
        H_new,K_new=correction()
        update_final(H_new,K_new)
# #    ##         
    f=open("position.txt","a")
    gameDisplay.fill(white)
    WHITE=(255,255,255)
    BLUE=(0,0,255)

    # gameDisplay.fill(WHITE)

    pygame.draw.rect(gameDisplay,BLUE,(position[0,0],position[1,0],20,20))
    car(position_measure[0,0],position_measure[1,0])
    print(position_measure)

    # pygame.draw.rect(gameDisplay, (255,0,0),  (position[0,0],position[1,0], 0.0001, 0.0001))
    pygame.display.update()
    clock.tick(60/8)
    t+=1
pygame.quit()
quit()