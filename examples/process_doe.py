from optimization_tools.DOE import DOE


def convert_to_MPa(x):
    return x/1e6


problem = DOE(levels=5, driver='Full Factorial')

problem.load('FullFactorial.txt',
             variables_names=['Al0', 'Al1'],
             outputs_names=['Weight', 'Lift', 'Drag', 'MaxMises',
                            'DispTip', 'EigenValue'])
problem.find_influences(not_zero=True)
problem.find_nadir_utopic(not_zero=True)
print('Nadir: ', problem.nadir)
print('Utopic: ', problem.utopic)

problem.plot(xlabel=['$A_{l_0}$', '$A_{l_1}$'],
             ylabel=['Weight (N)', 'Lift (N)', 'Drag (N)',
                     'Max\nVonMises \n Stress (MPa)',
                     'Trailing edge\nDisplace-\nment (m)',
                     'Buckling\nEigenvalue'],
             process={"MaxMises": convert_to_MPa}, number_y=5)

# Plot domain
problem.plot_domain('Weight', 'Drag', pareto=[False, False])
