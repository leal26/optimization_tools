"""
Created on Mar  9 14:58:25 2014
Last update Jul 20 16:26:40 2015
@author: Pedro Leal
"""
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                       Import necessary modules
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import subprocess as sp
import os  # To check for already existing files and delete them
import numpy as np
import math
import shutil  # Modules necessary for saving multiple plots
import datetime
import time
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                           Core Functions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def output_reader(filename, separator='\t', output=None,  # noqa C901
                  rows_to_skip=0, header=0, delete=False, structure=False,
                  type_structure=None):
    """Function that opens files of any kind.

    Able to skip rows and read headers if necessary.

    Inputs:
        - filename: just the name of the file to read.

        - separator: Main kind of separator in file. The code will
          replace any variants of this separator for processing. Extra
          components such as end-line, kg m are all eliminated. Separator
          can also be a list of separators to use

        - output: defines what the kind of file we are opening to
          ensure we can skip the right amount of lines. By default it
          is None so it can open any other file.

        - rows_to_skip: amount of rows to initialy skip in the file. If
          the output is different then None, for the different types of
          files it is defined as:
          - Polar files = 10
          - Dump files = 0
          - Cp files = 2
          - Coordinates = 1

        - header: The header list will act as the keys of the output
          dictionary. For the function to work, a header IS necessary.
          If not specified by the user, the function will assume that
          the header can be found in the file that it is opening.

        - delete: if True, deletes file read.

        - structure: the file that he is being read has a given structure. For
          a file with the following structure:
                0
                0 0
                0.0996174 0.00873875
                1
                0.0996174 0.00873875
                0.199258 0.0172063
          For the case where the header:
                >> header = ['element', 'x1', 'y1', 'x2', 'y2']
          A possible structure is:
                >> structure = [['element'], ['x1', 'y1'], ['x2', 'y2']]

        - type_structure: ['string', 'time', 'float', 'time', 'float']

    Output:
        - Dictionary with all the header values as keys

    Created on Thu Mar 14 2014
    @author: Pedro Leal
    """
    if header != 0:
        if type_structure is None:
            type_structure = len(header)*['float']

    def format_output(variable, type_structure):
        if type_structure is None:
            return float(variable)
        if type_structure == 'seconds':
            try:
                seconds = time.strptime(variable.split('.')[0], '%H:%M:%S')
                miliseconds = (float(variable.split('.')[1])
                               * 0.1**len(variable.split('.')[1]))
                total = (miliseconds
                         + datetime.timedelta(hours=seconds.tm_hour,
                                              minutes=seconds.tm_min,
                                              seconds=seconds.tm_sec
                                              ).total_seconds())

            except:  # noqa E722
                seconds = time.strptime(variable.split('.')[0], '%M:%S')
                miliseconds = (float(variable.split('.')[1])
                               * 0.1**len(variable.split('.')[1]))
                total = (miliseconds
                         + datetime.timedelta(hours=seconds.tm_hour,
                                              minutes=seconds.tm_min,
                                              seconds=seconds.tm_sec
                                              ).total_seconds())
            return total
        elif type_structure == 'string':
            return variable
        elif type_structure == 'float':
            return float(variable)

    # In case we are using an XFOIL file, we define the number of rows
    # skipped
    if output == 'Polar' or output == 'Alfa_L_0':
        rows_to_skip = 10
    elif output == 'Dump':
        rows_to_skip = 0
    elif output == 'Cp':
        rows_to_skip = 2
    elif output == 'Coordinates':
        rows_to_skip = 1
    # n is the amount of lines to skip
    Data = {}
    if header != 0:
        header_done = True
        for head in header:
            Data[head] = []
    else:
        header_done = False
    count_skip = 0

    # Add the possibility of more than one separator
    if type(separator) != list:
        separator_list = [separator]
    else:
        separator_list = separator
    structure_count = 0
    with open(filename, "r") as myfile:
        # Jump first lines which are useless
        for line in myfile:
            if count_skip < rows_to_skip:
                count_skip += 1
                # Basically do nothing
            elif header_done is False:
                # If the user did not specify the header the code will
                # read the first line after the skipped rows as the
                # header
                if header == 0:
                    # Open line and replace anything we do not want (
                    # variants of the separator and units)
                    for separator in separator_list:
                        line = line.replace(
                            separator
                            + separator
                            + separator
                            + separator
                            + separator
                            + separator,
                            ' '
                        ).replace(
                            separator
                            + separator
                            + separator
                            + separator
                            + separator,
                            ' '
                        ).replace(
                            separator
                            + separator
                            + separator
                            + separator,
                            ' '
                        ).replace(
                            separator
                            + separator
                            + separator,
                            ' '
                        ).replace(
                            separator
                            + separator,
                            ' '
                        ).replace(
                            separator,
                            ' '
                        ).replace(
                            "\n", ""
                        ).replace(
                            "(kg)", ""
                        ).replace(
                            "(m)", ""
                        ).replace(
                            "(Pa)", ""
                        ).replace(
                            "(in)", ""
                        ).replace(
                            "#", ""
                        )
                    header = line.split(' ')
                    n_del = header.count('')
                    for n_del in range(0, n_del):
                        header.remove('')
                    for head in header:
                        Data[head] = []
                    # To avoid having two headers, we assign the False
                    # value to header which will not let it happen
                    header_done = True
                # If the user defines a list of values for the header,
                # the code reads it and creates libraries with it.
                elif type(header) == list:
                    for head in header:
                        Data[head] = []
                    header_done = True
                if type_structure is None:
                    type_structure = len(header)*['float']
            else:
                if structure is False:
                    for separator in separator_list:
                        line = line.replace(
                            separator
                            + separator
                            + separator,
                            ' '
                        ).replace(
                            separator
                            + separator,
                            ' '
                        ).replace(
                            separator,
                            ' '
                        ).replace(
                            "\n", ""
                        ).replace(
                            '---------', ''
                        ).replace(
                            '--------', ''
                        ).replace(
                            '-------', ''
                        ).replace(
                            '------', ''
                        )

                    line_components = " -".join(line.rsplit("-", 1))
                    line_components = line_components.split(' ')
                    #line_components = line.split(' ')

                    n_del = line_components.count('')
                    for n in range(0, n_del):
                        line_components.remove('')

                    if line_components != []:
                        for j in range(0, len(header)):

                            try:
                                Data[header[j]].append(
                                    format_output(line_components[j],
                                                  type_structure[j]))
                            except:  # noqa E722
                                print('Error when recording for: ')
                                print('Line components:', line_components)
                                print('type structure:', type_structure)
                                print('index:', j)
                                print('header:', header)
                                raise ValueError('Something went wrong')
                # Use structure code
                else:
                    current_structure = structure[structure_count]

                    line = line.replace(
                        separator
                        + separator
                        + separator,
                        ' '
                    ).replace(
                        separator
                        + separator,
                        ' '
                    ).replace(
                        separator,
                        ' '
                    ).replace(
                        "\n", ""
                    ).replace(
                        '---------', ''
                    ).replace(
                        '--------', ''
                    ).replace(
                        '-------', ''
                    ).replace(
                        '------', ''
                    ).replace('-', ' -'
                              )

                    line_components = " -".join(line.rsplit("-", 1))
                    line_components = line_components.split(' ')
                    #line_components = line.split(' ')

                    n_del = line_components.count('')
                    for n in range(0, n_del):
                        line_components.remove('')

                    if line_components != []:
                        for j in range(0, len(line_components)):
                            Data[current_structure[j]].append(
                                format_output(line_components[j],
                                              type_structure[j]))
                        structure_count += 1
                        if structure_count == len(structure):
                            structure_count = 0
                # else DO NOTHING!
    # If delete file True, remove file from directory
    if delete:
        os.remove(filename)
    return Data
