# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Feature to CSV Table
# Author: Timm Nawrocki
# Last Updated: 2021-03-13
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Feature to CSV Table" is a function that converts a feature class attribute table to a csv file.
# ---------------------------------------------------------------------------

# Create a function to convert a feature class to csv
def feature_to_csv(input_feature, input_columns, output_file):
    """
        Description: converts a feature class attribute table to csv file
        Inputs: 'input_feature' -- path to a feature class
                'input_columns' -- an array containing the output column names
                'output_file' --  path where the csv file output will be stored
        Returned Value: Returns a csv table
        Preconditions: must have an existing feature class as input
        """

    # Import packages
    import arcpy
    import pandas as pd

    # Convert the feature class to a Numpy array
    feature_array = arcpy.da.FeatureClassToNumPyArray(input_feature, input_columns)

    # Convert the Numpy array to a Pandas data frame and save as csv file
    feature_data = pd.DataFrame(feature_array, columns = input_columns)
    feature_data.to_csv(output_file, header=True, index=False, sep=',', encoding='utf-8')
