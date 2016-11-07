# -*- coding: utf-8 -*-
"""
Created on Mon Oct 10 16:46:58 2016

@author: Pedro
"""
import math 
import numpy as np
# from scipy.optimize import differential_evolution

# def hausdorff_distance_2D(a, b, rotation = False, rotation_pivot = False,
                           # rotation_limits = [-math.pi/4., math.pi/4.]):
    # """Comparing a vector data 'a' to a vector data 'b'."""

    # def find_d_rotated(beta):
        # """Find Hausdorff distance considering a rigid body rotation."""
        # for i in range(len(data['x'])):
            # x = b['x'][i] - x_pivot
            # y = b['y'][i] - y_pivot
            # c_beta = math.cos(beta)
            # s_beta = math.sin(beta)
            # x_rotated = c_beta*x - s_beta*y + x_pivot
            # y_rotated = s_beta*x + c_beta*y + y_pivot
        # b_rotated = {'x': x_rotated, 'y': y_rotated}
        # return find_d(a, b_rotated)
    
    # if rotation == False and rotation_pivot == False:
        # return find_d(a,b)
    # else:
        # # determine what is the leading edge and the rotation angle beta
        # x_pivot = rotation_pivot[0]
        # y_pivot = rotation_pivot[1]
        
        # beta_bounds = [0,-math.pi/4]
        
        # result = differential_evolution(find_d_rotated, beta_bounds)
        # return result.fun
        
def find_d(a, b): 
    # It is assumed that a and b have the same keys with the same lengths
    keys = a.keys()
    n_a = len(a[keys[0]])
    n_b = len(b[keys[0]])
    min_values = 1e10 * np.ones(n_a) 
    for i in range(n_a):
        a_x = a['x'][i]
        a_y = a['y'][i]
        for j in range(n_b):
            v = [a_x - b['x'][j], a_y - b['y'][j]]
            norm = euclidian_norm(v)
            if norm < min_values[i]:
                min_values[i] = norm
    d = max(min_values)
    return d

def euclidian_norm(v):
    """Calculate the Euclidina norm of avector with size n"""
    squared_sum = 0
    for i in range(len(v)):
        squared_sum += v[i]**2
    return math.sqrt(squared_sum)

if __name__ == '__main__':
    from xfoil_module import output_reader
    
    filename = 'sampled_airfoil_data.csv'

    data = output_reader(filename, separator = ', ', header = ['x', 'y'])
    
    print hausdorff_distance_2D(data, data)