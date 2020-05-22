# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Cross-validate Classifier
# Author: Timm Nawrocki
# Last Updated: 2020-05-14
# Usage: Must be executed in an Anaconda 3 installation.
# Description: "Cross-validate Classifier" is a function that creates a cross-validation object for an XGBoost Classifier to be used in Bayesian Optimization.
# ---------------------------------------------------------------------------

# Define a function to format site data
def crossvalidate_classifier(parameters):
    """
    Description: creates a set of sampling points aligned with Area of Interest from points and buffered points
    Inputs: 'work_geodatabase' -- path to a file geodatabase that will serve as the workspace
            'input_array' -- an array containing the site table (must be first) and the area of interest
            'output_array' -- an array containing the output feature class
    Returned Value: Returns a point feature class with selected raster points labeled by site code
    Preconditions: the initial site table must be created from database queries
    """

    # Import packages
    import numpy as np
    from xgboost import XGBClassifier
    from sklearn.model_selection import cross_val_score
    from sklearn.model_selection import KFold

    # Define a 10-fold cross validation split method
    cv_splits = KFold(n_splits=10, shuffle=False, random_state=314)
    # Define the search parameter set
    parameters = parameters[0]
    # Define the cross validator
    score = cross_val_score(
        XGBClassifier(max_depth=int(parameters[0]),
                     learning_rate=parameters[1],
                     n_estimators=50,
                     verbosity=0,
                     objective='binary:logistic',
                     booster='gbtree',
                     n_jobs=4,
                     gamma=parameters[2],
                     min_child_weight=int(parameters[3]),
                     max_delta_step=int(parameters[4]),
                     subsample=parameters[5],
                     colsample_bytree=parameters[6],
                     colsample_bylevel=parameters[7],
                     reg_alpha=parameters[8],
                     reg_lambda=parameters[9],
                     scale_pos_weight=parameters[10]),
        X_bayesian, y_bayesian, scoring='roc_auc', cv=cv_splits).mean()
    # Convert the mean score to array and return the inverse of the array for minimization
    score = np.array(score)
    return -score
