# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 18:36:06 2015

Contains:
 - DOE class: does everything you will ever need including factor effect plots
 - pareto_frontier function: calculates for you the Pareto Front
@author: Pedro Leal
"""
import pickle
import time
import random
import math

from pyDOE import lhs
from optimization_tools.filehandling import output_reader

try:
    from abaqus import *
    in_Abaqus = True
except:
    in_Abaqus = False

if not in_Abaqus:
    import matplotlib.pyplot as plt


class DOE:
    """Create a Design of Experiences Environment."""

    def __init__(self, levels=2, driver='Taguchi', store=False):
        self.levels = levels
        self.driver = driver
        # All variable will be defined through the add_variable method
        self.variables = []
        # For the influence method, we need a list of names of all variables
        self.variables_names = []
        # Variable to know if store  values in a txt
        self.store = store

    def add_variable(self, name, lower, upper, levels=None, type=float):
        """Add variables to the DOE problem. """
        if levels is None:
            levels = self.levels

        try:
            self.variables.append({'upper': upper, 'lower': lower,
                                   'name': name, 'levels': levels,
                                   'type': type})
            self.variables_names.append(name)
        except:
            print('Forgot to define upper, lower or name')

    def define_points(self, runs=None):
        """
        Method to define the points to be evaluated based on the results from
        distribution given by the array method and the bound defined by the
        add_variable method.

        For dummy, levels means nothing"""
        self.n_var = 0
        self.n_var_2 = 0

        for variable in self.variables:
            if variable['levels'] == self.levels:
                self.n_var += 1
            elif variable['levels'] == 2:
                self.n_var_2 += 1
            else:
                raise Exception('A variable has a number of levels that is ' +
                                'not the default or 2')
        if self.driver == 'Taguchi':
            self.Taguchi()
        elif self.driver == 'Full Factorial':
            self.FullFactorial()
        elif self.driver == 'Random':
            self.runs = runs
            self.Random(runs)
        elif self.driver == 'Latin Hypercube':
            self.runs = runs
            self.array = lhs(len(self.variables), samples=runs,
                             criterion='center')

        self.domain = {}

        for j in range(self.n_var+self.n_var_2):
            upper = self.variables[j]['upper']
            lower = self.variables[j]['lower']
            levels = self.variables[j]['levels']
            type = self.variables[j]['type']

            dummy = []
            for i in range(self.runs):
                scale = self.array[i][j]
                if type == int and (scale*(upper-lower) % (levels-1.) != 0):
                    raise Exception('The bounds of the defined integer are ' +
                                    'not compatible with number of levels.')
                else:
                    dummy.append(lower + scale*(upper-lower) / (levels-1.))
            self.domain[self.variables[j]['name']] = dummy

    def run(self, function, cte_input=None, dependent_variables=None):
        """Runs and saves the results for the configurations obtained in
        define_points method.

        - cte_input : if defined, is a dictionary containing the constant
          inputs.
        - dependent_variables: if defined, it creates a relationship between
          different variables such as {'t_spar':'t_rib'}
        """

        def set_input(self, run):
            output = {}
            for key in self.domain:
                output[key] = self.domain[key][run]
            return output

        if self.store is not False:
            # timestr = time.strftime('%Y%m%d')
            file_txt = open('DOE_data.txt', 'w')

        header_ready = False

        for i in range(self.runs):
            input = set_input(self, i)
            # If there is a constant input, add it to input dictionary
            if cte_input is not None:
                input.update(cte_input)
            if dependent_variables is not None:
                for key_dependent in dependent_variables:
                    key_independent = dependent_variables[key_dependent]
                    input.update({key_dependent: input[key_independent]})

            # Store values before (if first time create header
            if self.store is not False:
                if header_ready is False:
                    for key in input:
                        file_txt.write(key + '\t')
                else:
                    file_txt = open('DOE_data.txt', 'a')
                    for key in input:
                        file_txt.write('%10f \t ' % (input[key]))
                file_txt.close()
            # Run script
            result = function(input)

            # Store output values (if first time, will finish header
            # with output keys and then write all the input and outputs
            if self.store is not False:
                file_txt = open('DOE_data.txt', 'a')
                if header_ready is False:
                    for key in self.store:
                        file_txt.write(key + '\t')
                    file_txt.write('\n')
                    for key in input:
                        file_txt.write('%10f \t ' % (input[key]))
                    for key in self.store:
                        file_txt.write('%10f \t ' % (result[key]))
                    header_ready = True
                else:
                    for key in result:
                        file_txt.write('%10f \t ' % (result[key]))
                file_txt.write('\n')
                file_txt.close()
            # Store output values
            if i == 0:
                # We will save the name of the putputs for plotting and etc
                self.output_names = [key for key in result]
                self.output = {}
                for key in self.output_names:
                    self.output[key] = []
            for key in self.output_names:
                self.output[key].append(result[key])

    def find_influences(self, not_zero=False):
        """ Calculate average influence of each variable over the
        objective functions. If refinement_criteria is defined, certain points
        will be eliminated. Works for Taguchi, Full Factorial and probably
        anything else.
        """
        self.influences = {}

        # For refinement reasons during plotting, it is relevant to
        # know which ones have zeros
        self.equal_to_zero = {key: [False]*(self.n_var +
                                            self.n_var_2)*self.levels for
                              key in self.output_names}
        for output_name in self.output_names:
            Y = self.output[output_name]
            # List of outputs
            self.influences[output_name] = []

            for var in self.variables_names:
                X = self.domain[var]
                # Eliminate repetitions by transforming the list in to a set
                # and sort them. X_set will be used for counting
                unique_X = sorted(set(X))
                # For each unique X, the value average will be calculated

                for j in range(len(unique_X)):
                    indices = [i for i, x in enumerate(X) if x == unique_X[j]]
                    # Filter option
                    if not_zero:
                        # Evaluate if any of the values of output is
                        # zero
                        for key, item in self.output.items():
                            if 0 in item:
                                # Eliminate it from the list of indices
                                for i in indices:
                                    if self.output[key][i] == 0:
                                        indices.remove(i)
                                        self.equal_to_zero[key][j] = True
                    # Count number of times the variable repeats itself
                    count = len(indices)
                    # Create an empyt slot in Y_DOE list to add all Ys
                    self.influences[output_name].append(0)
                    # Average of all points with same X value
                    dummy = 0
                    for index in indices:
                        dummy += Y[index]/count
                        # Add to the last term of Y_DOE (sum of all)
                        self.influences[output_name][-1] += Y[index]/count
    if not in_Abaqus:
        def plot(self, shadow=[], xlabel=None, ylabel=None,
                 number_y=5, process=None, ylimits=None):
            """plots DOE just like in excel.

            :param process: dictionary with output_name of outputs to be
            processed as keys and functions as the value of each key.
            :param number_y: number of values on the y-axis for each
            output."""
            import matplotlib.pyplot as plt

            def list_to_string(self, separator=', '):
                """Summ all the elements of a list of strings in to a string"""
                resultant_string = ''
                for component in self.variables_names:
                    resultant_string += component + separator
                # Remove the last separator.
                resultant_string = resultant_string[:-len(separator)]
                return resultant_string

            def create_ticks(self):
                # In japanese mora is the length of each sylab
                #  here it is the length of e
                if self.levels == 2:
                    mora = ['-', '+']
                elif self.levels == 3:
                    mora = ['-', 'o', '+']
                elif self.levels == 4:
                    mora = ['-', '-o', 'o+', '+']
                elif self.levels == 5:
                    mora = ['-', '-o', 'o', 'o+', '+']
                else:
                    raise Exception('n_range to high, max is 5!')

                # Replicate standard for all variables
                return (self.n_var_2)*['-', '+'] + (self.n_var)*mora

            def subtick_distance(self, border_spacing):
                """Function to generate the distances of the second x axis
                using figtext"""

                # normalizing values forimage to be >0 and <1
                norm = (2*border_spacing + self.levels*self.n_var - 1)

                # Initial proportional distance
                x0 = border_spacing/norm
                distances = []
                for i in range(len(self.variables_names)):
                    current = x0 + i*(self.levels - 1)/norm
                    if self.levels % 2 == 0:  # if even
                        if i == 0:
                            current += (self.levels - 2)/2./norm
                        elif i == 1:
                            current += (self.levels + 1)/2./norm
                        else:
                            current += (self.levels + 3)/2./norm
                    else:  # if odd
                        if i == 0:
                            current += (self.levels/2-.5)/norm
                        elif i == 1:
                            current += (self.levels/2 + .5)/norm
                        else:
                            current += (self.levels/2 + 1.5)/norm
                    distances.append(current)
                return distances

            # IF the user wants to add pretty names, if not just do with the
            # variable names
            if xlabel is None:
                xlabel = self.variables_names
            if ylabel is None:
                ylabel = self.output_names
            ticks = create_ticks(self)
            border_spacing = 0.2
            for output in self.output_names:
                Y = self.influences[output]
                if process is not None:
                    if output in process:
                        for i in range(len(Y)):
                            Y[i] = process[output](Y[i])
                plt.subplot(100*len(self.output_names) + 11 +
                            self.output_names.index(output))

                # Creating dummy values for horizontal axis
                xi = range((self.n_var+self.n_var_2) * self.levels)
                # Define ticks for only last
                if self.output_names[-1] == output:
                    plt.xticks(xi, ticks)
                else:
                    frame = plt.gca()
                    frame.axes.get_xaxis().set_visible(False)
#                plt.fill_between(xi, min(Y) - 0.05*(max(Y)-min(Y)),
#                                 max(Y) + 0.05*(max(Y)-min(Y)),
#                                 where = self.equal_to_zero[output],
#                                 color = '0.75')
                for i in range(self.n_var+self.n_var_2):
                    plt.plot(xi[i*self.levels: (i+1) * self.levels],
                             Y[i*self.levels: (i+1) * self.levels],
                             '-o')
    #                if output in shadow:
    #                    plt.plot(xi[i*self.levels : (i+1) * self.levels],
    #                             Y[i*self.levels : (i+1) * self.levels],
    #                             '--',color=plt.getp(line, 'linewidth'))

                plt.ylabel(ylabel[self.output_names.index(output)])
#                plt.xlabel("Design Variables ("+list_to_string(self)+")")

#                if self.output_names.index(output) == 0:
#                    plt.title("Design of Experiment: %i level %s" %
#                              (self.levels, self.driver))

                plt.xlim([-border_spacing, max(xi) + border_spacing])
                if ylimits is None:
                    plt.ylim(min(Y) - 0.05*(max(Y)-min(Y)),
                             max(Y) + 0.05*(max(Y)-min(Y)))
                else:
                    plt.ylim(ylimits[output][0], ylimits[output][1])
                plt.locator_params(axis='y', nbins=number_y)
                # plt.grid()

            # Create the second x axis
            distances = subtick_distance(self, border_spacing)
            print(xlabel, distances)
            for i in range(len(distances)):
                plt.annotate(xlabel[i], xy=(distances[i], 0),
                             xytext=(0, -25), xycoords='axes fraction',
                             textcoords='offset points',
                             horizontalalignment='center',
                             verticalalignment='center')
            for i in range(len(distances)-1):
                for j in range(10):
                    y = -2.5*(j+2)
                    plt.annotate('|', xy=((distances[i] +
                                           distances[i+1])/2., 0),
                                 xytext=(0, y), xycoords='axes fraction',
                                 textcoords='offset points',
                                 horizontalalignment='center',
                                 verticalalignment='center')
            plt.show()

        def plot_domain(self, Xaxis, Yaxis, not_equal=None, pareto=False,
                        labels=False):
            """Plots all the points in a 2D plot for the definided Xaxis and
            Yaxis

            param: Xaxis: string containing key for x axis
            param: Yaxis: string containing key for y axis
            param: pareto if != False print PAreto frontier. It is a list of
                   True/False related to max/min value
            param: not_equal is list of values that if equal, data is removed
                     from sample.
            It is of length 2"""
            if Xaxis not in self.output:
                X = self.domain[Xaxis]
            else:
                X = self.output[Xaxis]
            if Yaxis not in self.output:
                Y = self.domain[Yaxis]
            else:
                Y = self.output[Yaxis]
            if not_equal is None:
                plt.scatter(X, Y)
                if pareto is not False:
                    pareto_X, pareto_Y = pareto_frontier(X, Y,
                                                         maxX=pareto[0],
                                                         maxY=pareto[1])
                    plt.plot(pareto_X, pareto_Y)
            else:
                data = zip(X, Y)
                data = list(filter(lambda xy: xy[0] != not_equal[0], data))
                data = list(filter(lambda xy: xy[1] != not_equal[1], data))
                # Check for Not a number
                data = list(filter(lambda xy: math.isnan(xy[0]), data))
                data = list(filter(lambda xy: math.isnan(xy[1]), data))
                X, Y = zip(*data)

                plt.scatter(X, Y)

                if pareto is not False:
                    pareto_X, pareto_Y = pareto_frontier(X, Y,
                                                         maxX=pareto[0],
                                                         maxY=pareto[1])
                    plt.plot(pareto_X, pareto_Y)
            if labels is False:
                plt.xlabel(Xaxis)
                plt.ylabel(Yaxis)
            else:
                plt.xlabel(labels[0])
                plt.ylabel(labels[1])
            plt.show()

        def load(self, data_object, variables_names=None,
                 outputs_names=None, header=None, filetype='file'):
            """ Load data from text file with results of DOE.
                TODO: NEED TO INCLUDE POSSIBILITY FOR TWO LEVEL VARIABLE
                - input:
                    - data_object: string for text file or name of previous
                                    DOE object
                    - header: If not specified, the first line in the file
                      will be considered to be the header.
                    - filetype:
                        - if 'file': will use output_reader and read data from
                            file
                        - if 'object': will load a DOE object and copy all of
                         its attributes. Allows to have the same object
                         inside and outside Abaqus, but with optional
                         plotting results.

            """
            if filetype == 'file':
                if self.variables_names == []:
                    if header is None:
                        Data = output_reader(filename=data_object)
                    else:
                        Data = output_reader(filename=data_object,
                                             header=header)
                    if True is True:
                        self.output_names = outputs_names
                        self.variables_names = variables_names
                        self.n_var = len(variables_names)
                        self.n_var_2 = 0
                        self.output = {key: Data[key] for key in
                                       self.output_names}
                        self.domain = {key: Data[key] for key in
                                       self.variables_names}
        #            except:
        #                raise Exception('Something wrong with  '+
        #                                'variables_names and outputs_names.')
                else:
                    raise Exception('Cannot atribute variables and load ' +
                                    'data at the same object.')
            # If an object just copy all attributes to the new DOE object
            elif filetype == 'object':
                for attribute in dir(data_object):
                    var = getattr(data_object, attribute)
                    setattr(self, attribute, var)

    def Taguchi(self):
        """ Find the necessary Taguchi array."""
        self.runs = 50
        Taguchi_L50 = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                       [0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
                       [0, 0, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
                       [0, 0, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
                       [0, 1, 0, 1, 2, 3, 4, 0, 1, 2, 3, 4],
                       [0, 1, 1, 2, 3, 4, 0, 1, 2, 3, 4, 0],
                       [0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 0, 1],
                       [0, 1, 3, 4, 0, 1, 2, 3, 4, 0, 1, 2],
                       [0, 1, 4, 0, 1, 2, 3, 4, 0, 1, 2, 3],
                       [0, 2, 0, 2, 4, 1, 3, 3, 0, 2, 4, 1],
                       [0, 2, 1, 3, 0, 2, 4, 4, 1, 3, 0, 2],
                       [0, 2, 2, 4, 1, 3, 0, 0, 2, 4, 1, 3],
                       [0, 2, 3, 0, 2, 4, 1, 1, 3, 0, 2, 4],
                       [0, 2, 4, 1, 3, 0, 2, 2, 4, 1, 3, 0],
                       [0, 3, 0, 3, 1, 4, 2, 4, 2, 0, 3, 1],
                       [0, 3, 1, 4, 2, 0, 3, 0, 3, 1, 4, 2],
                       [0, 3, 2, 0, 3, 1, 4, 1, 4, 2, 0, 3],
                       [0, 3, 3, 1, 4, 2, 0, 2, 0, 3, 1, 4],
                       [0, 3, 4, 2, 0, 3, 1, 3, 1, 4, 2, 0],
                       [0, 4, 0, 4, 3, 2, 1, 3, 2, 1, 0, 4],
                       [0, 4, 1, 0, 4, 3, 2, 4, 3, 2, 1, 0],
                       [0, 4, 2, 1, 0, 4, 3, 0, 4, 3, 2, 1],
                       [0, 4, 3, 2, 1, 0, 4, 1, 0, 4, 3, 2],
                       [0, 4, 4, 3, 2, 1, 0, 2, 1, 0, 4, 3],
                       [1, 0, 0, 0, 3, 4, 3, 2, 1, 4, 1, 2],
                       [1, 0, 1, 1, 4, 0, 4, 3, 2, 0, 2, 3],
                       [1, 0, 2, 2, 0, 1, 0, 4, 3, 1, 3, 4],
                       [1, 0, 3, 3, 1, 2, 1, 0, 4, 2, 4, 0],
                       [1, 0, 4, 4, 2, 3, 2, 1, 0, 3, 0, 1],
                       [1, 1, 0, 1, 0, 2, 2, 1, 3, 4, 4, 3],
                       [1, 1, 1, 2, 1, 3, 3, 2, 4, 0, 0, 4],
                       [1, 1, 2, 3, 2, 4, 4, 3, 0, 1, 1, 0],
                       [1, 1, 3, 4, 3, 0, 0, 4, 1, 2, 2, 1],
                       [1, 1, 4, 0, 4, 1, 1, 0, 2, 3, 3, 2],
                       [1, 2, 0, 2, 2, 0, 1, 4, 4, 3, 1, 3],
                       [1, 2, 1, 3, 3, 1, 2, 0, 0, 4, 2, 4],
                       [1, 2, 2, 4, 4, 2, 3, 1, 1, 0, 3, 0],
                       [1, 2, 3, 0, 0, 3, 4, 2, 2, 1, 4, 1],
                       [1, 2, 4, 1, 1, 4, 0, 3, 3, 2, 0, 2],
                       [1, 3, 0, 3, 4, 3, 0, 1, 4, 1, 2, 2],
                       [1, 3, 1, 4, 0, 4, 1, 2, 0, 2, 3, 3],
                       [1, 3, 2, 0, 1, 0, 2, 3, 1, 3, 4, 4],
                       [1, 3, 3, 1, 2, 1, 3, 4, 2, 4, 0, 0],
                       [1, 3, 4, 2, 3, 2, 4, 0, 3, 0, 1, 1],
                       [1, 4, 0, 4, 1, 1, 4, 2, 3, 3, 2, 0],
                       [1, 4, 1, 0, 2, 2, 0, 3, 4, 4, 3, 1],
                       [1, 4, 2, 1, 3, 3, 1, 4, 0, 0, 4, 2],
                       [1, 4, 3, 2, 4, 4, 2, 0, 1, 1, 0, 3],
                       [1, 4, 4, 3, 0, 0, 3, 1, 2, 2, 1, 4]
                       ]
        # Initialize the Taguchi array.
        self.array = self.runs*[[]]
        # The reange of easch array was defined in:
        # https://controls.engin.umich.edu/wiki/index.php/
        # Design_of_experiments_via_taguchi_methods:_orthogonal_arrays
        if (self.n_var >= 7 and self.n_var <= 12) and self.n_var_2 <= 1:
            # Since the first column is for two level variables, we ignore it.
            for i in range(self.runs):
                self.array[i] = Taguchi_L50[i][1-self.n_var_2: self.n_var+1]

    def FullFactorial(self):
        """Define array for Full Factorial for a given number of
        levels.
        """
        def product(*args, **kwds):
            """ Returns all the possible combinations beween two lists
            or between itself.

            >>> print product('ABCD', 'xy')
            >>> Ax Ay Bx By Cx Cy Dx Dy

            >>> print product(range(2), repeat=3)
            >>>000 001 010 011 100 101 110 111

            Source: itertools
            """
            pools = list(map(tuple, args)) * kwds.get('repeat', 1)
            result = [[]]
            for pool in pools:
                result = [x+[y] for x in result for y in pool]
            for prod in result:
                yield tuple(prod)

        self.array = []

        possibilities = [i for i in range(self.levels)]

        for subset in product(possibilities, repeat=self.n_var):
            self.array.append(subset)

        self.runs = len(self.array)

    def Random(self, runs):
        random.seed()
        self.array = []
        for i in range(self.runs):
            design_i = []
            for j in range(self.n_var):
                design_i.append(random.random())
            self.array.append(design_i)

    def find_nadir_utopic(self, not_zero=True):
        """Find the minimum and maximum, nadir and utopic, for each
        output variable.

        This function is quite relevant for normalizing the objective
        function for the optimization.

        param: not_zero: filters the zero values out.

        returns: attributes utopic and nadir dictionaries for the output
                 variables, each containing a float value

        sources: http://stackoverflow.com/questions/16122362/python-matplotlib-how-to-put-text-in-the-corner-of-equal-aspect-figure
        """
        # First verify if there are any zeros, if true, get them out
        equal_to_zero = {}
        for key in self.output_names:
            equal_to_zero[key] = [False]*len(self.output[key])

            if not_zero:
                for i in range(len(self.output[key])):
                    for key2 in self.output_names:
                        if self.output[key2][i] == 0:
                            equal_to_zero[key][i] = True
                        elif equal_to_zero[key][i] is not True:
                            equal_to_zero[key][i] = False

        # Now we can find the nadir and the utopic points
        self.nadir = {}
        self.utopic = {}
        for key in self.output_names:
            self.nadir[key] = 0
            self.utopic[key] = 99999999999999999.

            for i in range(len(self.output[key])):
                if (equal_to_zero[key][i] is not True and
                        self.output[key][i] < self.utopic[key]):
                    self.utopic[key] = self.output[key][i]

                if (equal_to_zero[key][i] is not True and
                        self.output[key][i] > self.nadir[key]):
                    self.nadir[key] = self.output[key][i]


def pareto_frontier(Xs, Ys, maxX=True, maxY=True):
    # Sort the list in either ascending or descending order of X
    XY = [[float(Xs[i]), float(Ys[i])] for i in range(len(Xs))]
    myList = sorted(XY, reverse=maxX)
# Start the Pareto frontier with the first value in the sorted list
    p_front = [myList[0]]
# Loop through the sorted list
    for pair in myList[1:]:
        if maxY:
            if pair[1] >= p_front[-1][1]:  # Look for higher values of Y…
                p_front.append(pair)  # … and add them to the Pareto frontier
        else:
            if pair[1] <= p_front[-1][1]:  # Look for lower values of Y…
                p_front.append(pair)  # … and add them to the Pareto frontier
# Turn resulting pairs back into a list of Xs and Ys
    p_frontX = [pair[0] for pair in p_front]
    p_frontY = [pair[1] for pair in p_front]
    return p_frontX, p_frontY
