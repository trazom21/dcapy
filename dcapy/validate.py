"""
Decision Curve Analysis

Functions for validating and cleaning up data/inputs to the
decision curve analyzer

Author: Matthew Black
"""


def dca_input_validation(data, outcome, predictors,
                      x_start, x_stop, x_by,
                      probability, harm, intervention_per):
    """Performs input validation for the dca function
    Checks all relevant parameters, raises a ValueError if input is not valid
    
    Returns:
    --------
    A tuple of length 4 (data, predictors, probability, harm) where each is the
    newly updated or initialized version of its original input
    """
    data.dropna(axis=0)  #trim out cases with missing data
    #outcome must be coded as 0/1
    if (max(data[outcome]) > 1) or (min(data[outcome]) < 0):
        raise ValueError("outcome cannot be less than 0 or greater than 1")
    
    #x_start, x_stop, and x_by must be between 0 and 1
    if x_start > 1 or x_start < 0:
        raise ValueError("x_start must be between 0 and 1")
    if x_stop > 1 or x_stop < 0:
        raise ValueError("x_stop must be between 0 and 1")
    if x_by >= 1 or x_by <= 0:
        raise ValueError("x_by must be between 0 and 1")
    #x start must be less than x_stop
    if x_start >= x_stop:
        raise ValueError("x_stop must be larger than x_start")

    #if probability is specified, len must match # of predictors
    #if not specified, initialize the probability parameter
    if probability is not None: 
        #check if the number of probabilities matches the number of predictors
        if len(predictors) != len(probability):
            raise DCA_Error("Number of probabilites must match number of predictors")
        #validate and possibly convert predictors based on probabilities
        data = _validate_predictors(data, outcome, predictors, probability)
    else:
        probability = [True]*len(predictors)

    #if harm is specified, len must match # of predictors
    #if not specified, initialize the harm parameter
    if harm is not None:
        if len(predictors) != len(harm):
            raise DCA_Error("Number of harms must match number of predictors")
    else:
        harm = [0]*len(predictors)

    return data, predictors, probability, harm  #return any mutated objects


def _validate_predictors(data, outcome, predictors, probability):
    """Validates that each probability element is a boolean value and that
    all probabilities are between 0 and 1. If probability values are not b/t
    0 and 1, convert them using logistic regression
    """
    for i in range(0, len(predictors)):
        #validate that the value is a boolean
        if not isinstance(probability[i], bool):
            raise ValueError("Each element of probability list must be a boolean")
        #validate that the predictor name isn't 'all' or 'none'
        if predictor[i] in ["all", "none"]:
            raise ValueError("prediction names cannot be equal to 'all' or 'none'")

        if probability[i] == True:
            #validate that any predictors with probability TRUE are b/t 0 and 1
            if (max(data[predictors[i]]) > 1) or (min(data[predictors[i]]) < 0):
                raise ValueError("{} must be between 0 and 1"
                                .format(predictors[i]))
        else:
            #predictor is not a probability, convert with logistic regression
            model = sm.Logit(data[outcome], data[predictors[i]])
            data[predictors[i]] = model.fit().y_pred
    
    return data