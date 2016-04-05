# -*- coding: utf-8 -*-
"""
Created on Sun Jul 20 21:43:27 2014

@author: pbc1877
"""
import matplotlib.pyplot as plt

from xfoil_tools import output_reader
source = 'raw' # 'processed'
process = False

# Eigenvalue constraint
g1 = lambda x: True if x >= 1. else False # Inequality Constraint
# Lift higher than weight
g2 = lambda x, y: True if abs(y - x) <= 500. else False # Inequality Constraint
g = [g1, g2] #
output_constrained = ['EigenValue', ['Weight','Lift']] #, ['Weight','Lift']
outputs_plotted = ['Weight', 'Velocity']
units = ['N','m/s']
n_generation = 20
last_best = True
color_scheme = 'individual'

#h = # Equality Constraint
if source == 'processed':
    pullData = open('Data2.txt').read()
    dataArray = pullData.split('\n')
    Drag=[]
    Weight=[]
    Generation=[]
    n_generation=max(Generation)
    for eachLine in dataArray:
        # Avoids extra lines
        if len(eachLine)>1:
            x,y,z = eachLine.split('\t')
            Generation.append(x)
            Weight.append(y)
            Drag.append(z)

elif source == 'raw':
    pullData = output_reader('Results.txt')
    
    # Creating Generation counter
    pullData['Generation'] = []
    
    RandomKey = pullData.keys()[0] # Assumes all keys have item of same len
    
    population_size = len(pullData[RandomKey]) / n_generation
    for i in range(0, len(pullData[RandomKey])):
        pullData['Generation'].append( i/ population_size )
    
    # If process is True, the values that violate the constrain will be 
    # deleted in all of the dictionaries of pullData
    if process:
        for i in range(len(pullData[RandomKey])):
            for j in range(len(g)):
                if type(output_constrained[j]) != list:
                    if pullData[output_constrained[j]][i] != None:
                        if not g[j](pullData[output_constrained[j]][i]):
                            for key in pullData:
            #                    try:
                                pullData[key][i] = None
            #                    except:
            #                        print key

                elif len(output_constrained[j]) == 2:

                    # Need to verify if values was already annuled
                    if pullData[output_constrained[j][0]][i] !=None and pullData[output_constrained[j][1]][i] !=None:
                        if not g[j](pullData[output_constrained[j][0]][i],
                                    pullData[output_constrained[j][1]][i]):
                            for key in pullData:
            #                    try:
                                pullData[key][i] = None
            #                    except:
            #                        print key
        while None in pullData[RandomKey]:
            for key in pullData:
                    pullData[key].remove(None)
    
                
plt.colors()

x = pullData[outputs_plotted[0]]
y = pullData[outputs_plotted[1]]
generation = pullData['Generation']

for i in range(len(x)):
    if color_scheme == 'generation':
        plt.scatter(x[i], y[i], color=((1.-float(generation[i])/n_generation, 
                                        float(generation[i])/n_generation,
                                        0, 1.)))
    elif color_scheme == 'individual':
        plt.scatter(x[i], y[i], color=((1.-float(i)/len(x), 
                                        float(i)/len(x),
                                        0, 1.)))        
    plt.plot()

#if last_best:
#    plt.scatter(x[-1], y[-1], marker = 's')
#    plt.plot()     
#plt.grid()  
plt.xlabel(outputs_plotted[0] + ' (' + units[0] + ')')
plt.ylabel(outputs_plotted[1] + ' (' + units[1] + ')')