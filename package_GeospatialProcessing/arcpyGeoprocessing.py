# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Arcpy Geoprocessing Wrapper
# Author: Timm Nawrocki
# Last Updated: 2019-10-29
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Arcpy Geoprocessing Wrapper" is a function that wraps other arcpy functions for standardization, input and output checks, and error reporting.
# ---------------------------------------------------------------------------

# Define a wrapper function for arcpy geoprocessing tasks
def arcpy_geoprocessing(geoprocessing_function, check_output = True, check_input = True, **kwargs):
    """
    Description: wraps arcpy geoprocessing and data access functions for file checks, message reporting, and errors.
    Inputs: geoprocessing function -- any arcpy geoprocessing or data access processing steps defined as a function that receive ** kwargs arguments.
            check_output -- boolean input to control if the function should check if the output already exists prior to executing geoprocessing function
            check_input -- boolean input to control if the function should check if the inputs already exist prior to executing geoprocessing function
            **kwargs -- key word arguments that are used in the wrapper and passed to the geoprocessing function
                'input_array' -- if check_input == True, then the input datasets must be passed as an array
                'output_array' -- if check_output == True, then the output datasets must be passed as an array
    Returned Value: Function returns messages, warnings, and errors from geoprocessing functions.
    Preconditions: geoprocessing function and kwargs must be defined, this function does not conduct any geoprocessing on its own
    """

    # Import packages
    import arcpy

    try:
        # If check_output is True, then check if output exists and warn of overwrite if it does
        if check_output == True:
            for output_data in kwargs['output_array']:
                if arcpy.Exists(output_data) == True:
                    print(f"{output_data} already exists and will be overwritten.")
        # If check_input is True, then check if inputs exist and quit if any do not
        if check_input == True:
            for input_data in kwargs['input_array']:
                if arcpy.Exists(input_data) != True:
                    print(f'{input_data} does not exist. Check that environment workspace is correct.')
                    quit()
        # Execute geoprocessing function if all input data exists
        out_process = geoprocessing_function(**kwargs)
        # Provide results report
        try:
            msg_count = out_process.messageCount
            print(out_process.getMessage(msg_count - 1))
        except:
            print(out_process)
    # Provide arcpy errors for execution error
    except arcpy.ExecuteError as err:
        print(arcpy.GetMessages())
        quit()