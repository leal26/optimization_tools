from optimization_tools.DOE import DOE
import time
import pickle


def dummy_function(inputs):
    a = inputs['a']
    b = inputs['b']
    c = inputs['c']
    x = inputs['x']
    return({'y': a*x**2 + b*x + c,
            'z': (a*b**2)*x**2 + a**2*b*x + c**2})


# Define points
problem = DOE(levels=5, driver='Full Factorial')
problem.add_variable('a', lower=0.04, upper=0.2, type=float)
problem.add_variable('b', lower=-0.4, upper=0.1, type=float)
problem.add_variable('c', lower=-0.4, upper=0.1, type=float)
problem.define_points()

# Run for a function with dictionary as inputs
problem.run(dummy_function, cte_input={'x': -2})

problem.find_influences(not_zero=True)
problem.find_nadir_utopic(not_zero=True)
print('Nadir: ', problem.nadir)
print('Utopic: ', problem.utopic)

# Plot factor effects
problem.plot(xlabel=['a', 'b', 'c'],
             ylabel=['y (m)', 'z (m)'], number_y=5)
# Plot domain
problem.plot_domain('y', 'z', pareto=[False, False], labels=['y (m)', 'z (m)'])
# Store data
# timestr = time.strftime('%Y%m%d')
# fileObject = open('DOE_'+ self.driver + '_' + timestr,'wb')
fileObject = open('DOE_FullFactorial_20150828', 'wb')
pickle.dump(problem, fileObject)
fileObject.close()
