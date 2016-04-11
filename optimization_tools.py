# -*- coding: utf-8 -*-
"""
Created on Sun Jul 20 21:43:27 2014

@author: pbc1877
"""
import matplotlib.pyplot as plt

from xfoil_module import output_reader

def plot_generations(filename, cost = None, g = None, p = None,
                     output_constrained = ['EigenValue', ['Weight','Lift']],
                     outputs_plotted = ['Weight', 'Velocity'], source = 'raw',
                     units = ['N','m/s'], n_generation = 20,
                     last_best = True, color_scheme = 'individual', 
                     optimizers = ['NSGA2','SNOPT'], plot_type = 'all',
                     output_labels = None):
    """
    
    :param filename: name of file to read
    :param cost: function that calculates the cost, if not defined and
           'best' used, it is the minimum value in outputs_plotted
    :param g: constraint function
    :param p: processing function(eg. convert units after constraints)
    :param output_constrained: Outputs that will be constrained by g
    :param outputs_plotted: The two outputs in the axis of the scatter 
            plot. If only one is defined, the x axis is considered the
            generation
    :param source: 'raw' or 'processed'
    :param units: units to be on the scatter plots
    :param n_generation: number of generations
    :param last_best: if Trye, the last individual is the best and plot it.
    :param color_scheme: if 'individual', each point in the scatter plot
        has a unique color. If 'generation', each individual in the
        same generation have the same color.
    :optimizers: list of optimizers (works for plot_type = 'best')
    :param plot_type: 'all' plots all individuals and 'best' plots only the
        best individuals (still does not work for multiobjective). 'all and best'
        plots both together.
    :param output_labels: if defined, defines the labels on the plot.
        Otherwise the outputs_plotted are used
    """
    #h = # Equality Constraint
    if g==None or output_constrained == None:
        process = False
    else:
        process = True
    if source == 'processed':
        pullData = open(filename).read()
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
        pullData = output_reader(filename)
        
        # Creating Generation counter
        pullData['Generation'] = []
        
        RandomKey = pullData.keys()[0] # Assumes all keys have item of same len
        
        population_size = len(pullData[RandomKey]) / n_generation
        for i in range(population_size, len(pullData[RandomKey])+population_size):
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
        
    # Processing
    if p != None:
        for k in range(len(outputs_plotted)):
            for i in range(len(pullData[outputs_plotted[k]])):
                pullData[outputs_plotted[k]][i] = p[k](pullData[outputs_plotted[k]][i])
                
    plt.colors()
    
    generation = pullData['Generation']
    x = pullData[outputs_plotted[0]]
    if len(outputs_plotted) == 2:
        x = pullData[outputs_plotted[0]]
        y = pullData[outputs_plotted[1]]
        space = 0.02*(max(x) - min(x))
        plt.xlim(min(x) - space ,max(x) + space)
    else:
        x = pullData['Generation']
        y = pullData[outputs_plotted[0]]
        plt.xlim(0.5, n_generation + 0.5)

    if plot_type == 'best' or plot_type == 'all and best':
        global_min = 9999.
        cost_list = []
        generation_list = []
        if cost == None:
            for j in range(1,n_generation+1):
                current_min = 9999.
                for i in range(len(generation)):
                    if generation[i] == j and y[i] < current_min:
                        current_min = y[i]
                if current_min < global_min:
                    global_min = current_min
                cost_list.append(global_min)
                generation_list.append(j)
        plt.plot(generation_list, cost_list, '-o')
        plt.xlim(0.5, n_generation + 0.5)
        
    if plot_type == 'all' or plot_type == 'all and best':
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
        
        if last_best:
            plt.scatter(x[-1], y[-1], marker = 's')
            plt.plot()     

    

    plt.grid()
        
    if len(outputs_plotted) == 2:
        if output_labels == None:
            if units != None:
                plt.xlabel(outputs_plotted[0] + ' (' + units[0] + ')')
                plt.ylabel(outputs_plotted[1] + ' (' + units[1] + ')')
            else:
                plt.xlabel(outputs_plotted[0])
                plt.ylabel(outputs_plotted[1])               
        else:
            if units != None:
                plt.xlabel(output_labels[0] + ' (' + units[0] + ')')
                plt.ylabel(output_labels[1] + ' (' + units[1] + ')')   
            else:
                plt.xlabel(output_labels[0])
                plt.ylabel(output_labels[1])                  
    else:
        plt.xlabel('Iteration number')
        if output_labels == None:
            if units != None:
                plt.ylabel(outputs_plotted[0] + ' (' + units[0] + ')')
            else:
                plt.ylabel(outputs_plotted[0])
        else:
            if units != None:
                plt.ylabel(output_labels[0] + ' (' + units[0] + ')')
            else:
                plt.ylabel(output_labels[0])
if __name__ == "__main__":
    filename = "Results.txt"

    n_generation = 20
    # Eigenvalue constraint
    g1 = lambda x: True if x >= 1. else False # Inequality Constraint
    # Lift higher than weight
    g2 = lambda x, y: True if abs(y - x) <= 500. else False # Inequality Constraint
    g = [g1, g2] #
    outputs_constrained = ['EigenValue', ['Weight','Lift']] #, ['Weight','Lift']
    outputs_plotted = ['Weight', 'Velocity'] 
    units = ['N','m/s']
    plot_generations(filename, g = g, output_constrained = outputs_constrained,
                     outputs_plotted = outputs_plotted, n_generation = n_generation,
                     units = units)