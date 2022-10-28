#To display a graph of a network solution using the force-directed algorithm for drawing networks (graphs)
#This is the result of a lot of testing, debugging and experimentation, so the code is a bit messy

import pygame
import json
import math
from pygame.locals import *
pygame.init()

    


#INITIALIZATION

#Loading file
file = open("network.json", "r")
networkJSON = json.load(file)

screenSize = 600
margins = 100
size = screenSize-(margins*2)
space = 10
totalCount = networkJSON['InputCount'] + networkJSON['HiddenCount'] + networkJSON['OutputCount']
cellSpace = (size/math.floor(math.sqrt(totalCount)))
cellSize = cellSpace/space

screen = pygame.display.set_mode((screenSize,screenSize))

RED = (255,0,0)
GREEN = (0,255,0)

BLUE = (0,0,255)
GREY = (100,100,100)
ORANGE = (255,127,0)

cellsLeft = totalCount

cells= []

#Initializing cell positions as a grid initially
for y in range(math.ceil(math.sqrt(totalCount))):
  for x in range(math.ceil(math.sqrt(totalCount))):
    cells.append(
      {
        'Pos': [margins+cellSpace*x, margins+cellSpace*y],
        'Vel': [0,0]   
      }
    )
    cellsLeft -= 1
    if cellsLeft==0:
      break
  if cellsLeft==0:
      break



#Doing physics computation to reach mechanical equilibrium


for i in range(50)  :
  # applying spring fo\r ce based on synaptic connections with hooke's law
  for synapse in networkJSON['Synapses']:
    c0 = cells[synapse['presynapticID']]
    c1 = cells[synapse['postsynapticID']]

    
    c0['Vel'][0] +=  ((c1['Pos'][0] -c0['Pos'][0])/50)  *abs(synapse['weight'])
    
    c0['Vel'][1] += ((c1['Pos'][1] -c0['Pos'][1])/50)  *abs(synapse['weight'])
    
    c1['Vel'][0] += ((c0['Pos'][0] -c1['Pos'][0])/50) *abs(synapse['weight'])
    
    c1['Vel'][1] += ((c0['Pos'][1] -c1['Pos'][1])/50) *abs(synapse['weight'])
  
  
  #Applying repelling between cells based on columb's law
  for id in range(len(cells)):
    for id1 in range(len(cells)):
      if id!=id1:
        distX = cells[id]['Pos'][0]-cells[id1]['Pos'][0]
        distY = cells[id]['Pos'][1]-cells[id1]['Pos'][1]
        
        magnitude = math.sqrt(distX**2 + distY**2)/(cellSize/1.5)
        
        
        cells[id]['Pos'][0] += distX/(magnitude**2)
        cells[id]['Pos'][1] += distY/(magnitude**2)
  
  #Applying dampening drag on velocities and updating cellPositions based on velocity
  for id in range(len(cells)):
    
    cells[id]['Vel'][0] /= 2
    cells[id]['Vel'][1] /= 2
    
    
    
    cells[id]['Pos'][0] += cells[id]['Vel'][0]
    cells[id]['Pos'][1] += cells[id]['Vel'][1]
    
      
    

  
  for c in cells:
    pygame.draw.circle(screen,RED,tuple(c['Pos']),cellSize)
  for synapse in networkJSON['Synapses']:
    pygame.draw.line(screen, RED, tuple(cells[synapse['presynapticID']]['Pos']),tuple(cells[synapse['postsynapticID']]['Pos']),5)

  
  pygame.display.flip()
  pygame.time.wait(100)
  screen.fill((0,0,0))
  
    
#Drawing final result

for id in range(len(cells)):
  c = cells[id]
  color = ORANGE
  if id<networkJSON['InputCount']:
    color = BLUE
  elif id<networkJSON['InputCount'] + networkJSON['HiddenCount']:
    color = GREY
  
  pygame.draw.circle(screen,color,tuple(c['Pos']),cellSize)
    
for synapse in networkJSON['Synapses']:
  color = GREEN
  if synapse['weight'] < 0:
    color = RED
  pygame.draw.line(screen,color, tuple(cells[synapse['presynapticID']]['Pos']),tuple(cells[synapse['postsynapticID']]['Pos']),math.ceil(abs(synapse['weight'])*2))
    
    

#Updating display
pygame.display.flip()
pygame.time.wait(1000000)
pygame.quit()
