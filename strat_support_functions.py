###########################################################################

# DESCRIPTION
# Library of supporting functions for strategies



# # 1) Load modules

import numpy
# import datetime




# 2) Collection of support functions

def avger(series,periods):
    # Load modules
    # import numpy as np
    
    # Function 
    return numpy.mean(numpy.concatenate([series[-periods:-1],[series[-1]]]))
    