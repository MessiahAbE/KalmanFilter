from cProfile import label
from cmath import atan
from hashlib import new
from re import U
import pygame
import numpy as np
from pygame.locals import *
import matplotlib.pyplot as plt 
pygame.init()

display_width = 1800
display_height = 1600

gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('A bit Racey')

black = (0,0,0)
white = (255,255,255)

clock = pygame.time.Clock()
crashed = False
points=[]
points.append([0,0])
points_measure=[]
points_gt=[]
points_gt.append([0,0])
points_measure.append([0,0])
measured_positions_x=[]
measured_positions_y=[]
predicted_positions_x=[]
predicted_positions_y=[]
cov_width=[]
cov_hight=[]
position=np.array([[0],[0]])
position_measure=position
p_0=np.array([[0,0],[0,0]])
teta=-1
point_prev=[[0],[0]]
def car(x,y):
    gameDisplay.blit(carImg, (x,y))


#In this function the position estimation is being conducted 
def estimate_pose(position):
    global position_new_true
    global position_new_true
    
    F=np.array([[1,0],[0,1]])
    r=0.1
    delta_t=1/8
    G=np.array([[r/2*delta_t,r/2*delta_t],[r/2*delta_t,r/2*delta_t]])
    u=np.array([[1],[1]])
    
    position_new = np.matmul(F,position) + np.matmul(G,u) + np.array([[np.random.normal(0,0.1)],[np.random.normal(0,0.15)]])*delta_t
    position_new_true = np.matmul(F,position)+np.matmul(G,u)
    
    return position_new

x_change = 0


#The state covariance Matrix is being updated in this function 
def update():
    global p_0 
    delta_t=1/8
    F=np.array([[1,0],[0,1]])
    temp=np.matmul(F,p_0)
    Q=np.array([[0.1,0],[0,0.15]])*1/8
    p_new=np.matmul(temp,F.transpose())+Q
    p_0=p_new
    
#The measurement data is being computed 
def measurement():
    global position_measure
    global position
    H=np.array([[1,0],[0,2]])
    R=np.array([[0.05],[0.075]])
    
    Z=np.matmul(H,position_new_true) + np.asarray([[np.random.normal(0,0.05)],[np.random.normal(0,0.075)]])
    
    position_measure=Z

#Computing Kalman gain    
def correction():
    global p_0

    H=np.array([[1,0],[0,2]])
    R=np.array([[0.05,0],[0,0.075]])
    temp1=np.matmul(p_0,H.transpose())
    temp2=np.matmul(np.matmul(H,p_0),H.transpose()) + R

    k=temp1/temp2
    k[np.isnan(k)] = 0

    return H,k
#final update 
def update_final(H,K):
    global p_0
    global position    
    p_0=np.matmul((np.identity(2)-np.matmul(K,H)),p_0)
    H = np.array([[1,0],[0,2]])
    position = position + np.matmul( K , (position_measure - np.matmul(H,position)) )
    print("pos!", position)

t=1   
while not crashed:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            crashed = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                x_change = -5
            elif event.key == pygame.K_RIGHT:
                x_change = 5
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                x_change = 0


    position=estimate_pose(position)
    update()

    if(t%8==0):
        measurement()
        H_new,K_new=correction()
        update_final(H_new,K_new)


    
    
    
    gameDisplay.fill(white)
    WHITE=(255,255,255)
    BLUE=(0,0,255)
    RED=(255,0,0)
    GREEN=(0,255,0)

    red = (180, 50, 50)
    size = (position[0,0]*1000+50-(p_0[0,0]*2000)/2, position[1,0]*1000+50-(2000*p_0[1,1])/2, p_0[0,0]*2000, 2000*p_0[1,1])
    pygame.draw.ellipse(gameDisplay, red, size,1)  
    # pygame.draw.rect(gameDisplay,BLUE,(position[0,0]*1000+50,position[1,0]*1000+50,10,10))
    # points1=[(position[0,0]*1000+50,position[1,0]*1000+50), (position[0,0]*1000+50,position[1,0]*1000+500), (position[0,0]*1000+250,position[1,0]*1000+500)]
    # pygame.draw.polygone(gameDisplay, color=(255,0,0),points=points1)
    # teta=atan((point_prev[1,0]-(position[1,0]*1000+50))/(point_prev[0,0]-(position[1,0]*1000+50)))
    pygame.draw.polygon(gameDisplay, BLUE,
                        [[position[0,0]*1000+50,position[1,0]*1000+50],[position[0,0]*1000+40,position[1,0]*1000+35] ,
                        [position[0,0]*1000+40,position[1,0]*1000+65]])
  
    points.append([position[0,0]*1000+50,position[1,0]*1000+50])
    points_gt.append([position_new_true[0,0]*1000+50,position_new_true[1,0]*1000+50])
    points_measure.append([position_measure[0,0]*1000+50,(position_measure[1,0]/2)*1000+50])
    pygame.draw.lines(gameDisplay,BLUE,False,points,5)
    pygame.draw.lines(gameDisplay,GREEN,False,points_gt,5)
    pygame.draw.lines(gameDisplay,RED,False,points_measure,5)

# pygame.display.update()
    # pygame.draw.polygon(surface=gameDisplay, color=(255, 0, 0),points=[(position[0,0]*1000+50,position[1,0]*1000+50), (position[0,0]*1000+40,position[1,0]*1000+40), (position[0,0]*1000+30,position[1,0]*1000+30)])

    if(t%8==0):
        pygame.draw.rect(gameDisplay,RED,(position_measure[0,0]*1000+50,(position_measure[1,0]/2)*1000+50,10,10))
        pygame.draw.rect(gameDisplay,GREEN,(position_new_true[0,0]*1000+50,(position_new_true[1,0]/2)*1000+50,10,10))

    pygame.draw.rect(gameDisplay,RED,(position_measure[0,0]*1000+50,(position_measure[1,0]/2)*1000+50,10,10))
    pygame.draw.rect(gameDisplay,GREEN,(position_new_true[0,0]*1000+50,(position_new_true[1,0])*1000+50,10,10))   
    measured_positions_x.append(position_measure[0,0])
    measured_positions_y.append(position_measure[1,0])
    predicted_positions_x.append(position[0,0])
    predicted_positions_y.append(position[1,0])
    cov_hight.append(p_0[0,0])
    cov_width.append(p_0[1,1])
    # plt.plot(measured_positions_x)
    # plt.show()
    pygame.display.update()
    clock.tick(8) 
        
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

