# Copyright (C) 2023 tracetronic GmbH
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-
import re
from typing import List

from .api.CheckResult import CheckResult
from .api.AbstractPackageCheck import AbstractPackageCheck
from .helper.CheckType import CheckType
from .helper.ConfigKeys import ParameterKeys as pk

try:
    from tts.core.logging import SPrint, WPrint, EPrint
    from tts.core.api.internalApi.Api import Api
    api = Api()
except:
    from logging import info as SPrint, warning as WPrint, error as EPrint

# module type: mandatory
MODULE_TYPE = CheckType.PACKAGE.value

# keys declared in "parameters" in config.yaml:
# ParameterKeys.ORDER
# ParameterKeys.SORT_METHOD
# ParameterKeys.NUMBER_OF_RELEVANT_CHARACTERS
# ParameterKeys.PARAMETER
# ParameterKeys.RETURNVALUE
# ParameterKeys.LOCALVAR
# ParameterKeys.FUNCTION
# ParameterKeys.NAME
# ParameterKeys.DESCRIPTION
# ParameterKeys.REGEX_PATTERN
# ParameterKeys.CUSTOM_MESSAGE
# ParameterKeys.ALLOW_UNDEFINED


class CheckPackageVariables(AbstractPackageCheck):
    """
    Check Package Variables
    =========================

    Description
    -----------

    - Checks for each variable:
        - Whether the name matches the provided pattern
        - Whether the variable description matches the provided pattern
    - Checks whether the variables are sorted alphabetically. Following parameters must be
    specified:
        - Sort method (ascending or descending)
        - Number of relevant characters from the beginning of each variable. With 0, False or None,
        full variable names are considered.

    Specifics and Results
    ---------------------

    - Detailed information for invalid configuration
        - Required variables
        - Required parameters
        - Validation of the parameters (Type check, Regex Pattern compile)

    Limitations
    -----------

    """

    def __init__(self, internalApi):  # pylint: disable=W0613
        """
        Constructor to load the check parameters from config.yaml
        """
        super().__init__()

    def GetName(self) -> str:
        """
        Name to be shown in UI and used in the config.yaml
        """
        return type(self).__name__

    def check(self, test_item, parameters) -> List:
        checkResults = []
        checkResults.extend(self.check_variable(test_item, parameters))
        checkResults.extend(self.check_variable_order(test_item, parameters))
        return checkResults

    def get_var_type(self, variable):
        """
        Determines the type of a variable (Local Var, Function, Parameter, Return value)

        Parameters
        ----------
        variable: the variable to be checked

        Returns
        -------
        The type of the variable, or None if no matching type was found.

        """

        variable_is_parameter = variable.IsParameter()
        variable_is_return = variable.IsReturn()
        #variable_name = variable.GetName() # keep for possible future use
        variable_type = variable.GetType()

        if variable_type != pk.FUNCTION:
            if variable_is_parameter and not variable_is_return:
                return pk.PARAMETER
            if variable_is_return and not variable_is_parameter:
                return pk.RETURNVALUE
            if not (variable_is_parameter or variable_is_return):
                return pk.LOCALVAR
            return None


        if not (variable_is_parameter or variable_is_return):
            return pk.FUNCTION

        return None

        # This code is unreachable by the current logic, but should be kept.
        #EPrint(f'Variable type is not supported: {variablename} - {variable_type} - \
        #         P_{variable_is_parameter} - R_{variable_is_return}')

    def check_unused_variable(self, package):
        """
        Checks if package contains unused variables

        Parameters
        ----------
        package: the package to be checked

        Returns
        -------
        check results

        """

        # init clean check result list
        checkResults = []

        unused_varibles_list = []
        unused_varibles = []

        try:
            unused_varibles = package.GetUnusedVariables()
        except AttributeError:
            pass

        # API returns a list
        if unused_varibles:
            for variable in unused_varibles:
                unused_varibles_list.append(variable.GetName())
            checkResults.append(CheckResult(f'Unused variables detected: {unused_varibles_list}'))

        return checkResults

    def check_variable(self, package, parameters):
        """
        Checks name and description of a given variable.

        Parameters
        ----------
        variable: the package to be checked
        parameters: contains the expected values (name and description) of the checked parameters

        Returns
        -------
        check results

        """

        # init clean check result list
        checkResults = []

        checkResults.extend(self.check_unused_variable(package))

        if pk.ALLOW_UNDEFINED in parameters:
            allow_undefined_variable = parameters[pk.ALLOW_UNDEFINED]
        else:
            allow_undefined_variable = False

        for variable in package.GetVariables():
            if not allow_undefined_variable:
                checkResults.extend(self.check_undefined_type(variable))
            var_type = self.get_var_type(variable)
            if var_type is None:
                checkResults.extend(self.check_variable_type(variable))
            else:
                if pk.NAME in parameters[var_type]:
                    checkResults.extend(self.check_variable_name(variable, parameters))
                if pk.DESCRIPTION in parameters[var_type]:
                    checkResults.extend(self.check_variable_description(variable, parameters))

        return checkResults

    def check_variable_order(self, package, parameters):
        """
        Checks the order of the variable list.

        Parameters
        ----------
        variable: the package to be checked
        parameters: contains the expected ordering

        Returns
        -------
        check results

        """

        # init clean check result list
        checkResults = []

        # check the Description
        sortMethod = parameters[pk.ORDER][pk.SORT_METHOD]
        relevantChars = parameters[pk.ORDER][pk.NUMBER_OF_RELEVANT_CHARACTERS]
        checkResultSuffix = ''

        # get list of package variable
        variableNames = []
        for variable in package.GetVariables():
            variableNames.append(variable.GetName())

        # truncate list of variable names after the number of relevant characters
        if relevantChars and relevantChars != 'None':
            variableNames = [v[:relevantChars] for v in variableNames]
            checkResultSuffix = f', considering the first {relevantChars} characters'
        sortedVariableNames = variableNames.copy()

        # check config and sort list
        if sortMethod == 'None':
            SPrint('Sort check is disabled!')

        elif sortMethod == 'ascending':
            sortedVariableNames.sort(reverse=False, key=str.casefold)
            # check order ascending
            if sortedVariableNames != variableNames:
                checkResults.append(CheckResult(f'Variables are not sorted in ascending '
                                                f'order{checkResultSuffix}!'))

        elif sortMethod == 'descending':
            sortedVariableNames.sort(reverse=True, key=str.casefold)
            # check order descending
            if sortedVariableNames != variableNames:
                checkResults.append(CheckResult(f'Variables are not sorted in descending '
                                                f'order{checkResultSuffix}!'))

        else:
            checkResults.append(CheckResult(f'Sort method "{sortMethod}" is not supported!'))

        return checkResults

    def check_variable_name(self, variable, parameters):
        """
        Checks name of a given variable.

        Parameters
        ----------
        variable: the variable to be checked
        parameters: contains the expected name

        Returns
        -------
        check results

        """

        # init clean check result list
        checkResults = []

        var_type = self.get_var_type(variable)
        param_var_name = parameters[var_type][pk.NAME]

        variablename = variable.GetName()

        # check variable name
        regex = param_var_name.get(pk.REGEX_PATTERN)
        try:
            re.compile(regex)
        except re.error:
            checkResults.append(CheckResult(f'"{regex}" is not a '
                                            f'valid pattern. Check '
                                            f'"{self.config.config_rel_path}"!'))
            return checkResults

        try:
            param_var_name = parameters[var_type][pk.NAME]
            if not re.match(param_var_name.get(pk.REGEX_PATTERN), variablename):
                if pk.CUSTOM_MESSAGE in param_var_name:
                    msg = f'Variable "{variablename}" does not match pattern. ' \
                        f'{param_var_name.get(pk.CUSTOM_MESSAGE)}'
                else:
                    msg = f'Variable "{variablename}" does not match pattern: ' \
                        f'"{param_var_name.get(pk.REGEX_PATTERN)}"'
                checkResults.append(CheckResult(msg))

        except TypeError:
            WPrint(f'Expected string or byte-like object: {variablename}')

        finally:
            return checkResults  # pylint: disable=W0150

    def check_variable_description(self, variable, parameters):  # pylint: disable=R1710
        """
        Checks the description of the variables.

        Parameters
        ----------
        variable: the variable to be checked
        parameters: contains the expected description

        Returns
        -------
        check results

        """
        checkResults = []

        var_type = self.get_var_type(variable)
        param_desc = parameters[var_type][pk.DESCRIPTION]

        variablename = variable.GetName()

        # check variable description
        regex = param_desc.get(pk.REGEX_PATTERN)
        try:
            re.compile(regex)
        except re.error:
            checkResults.append(CheckResult(f'"{regex}" '
                                            f'is not a valid pattern. Check '
                                            f'"{self.config.config_rel_path}"!'))
            return checkResults

        if not pk.DESCRIPTION in parameters[var_type]:
            return checkResults

        # check if a variable has a description
        if param_desc.get(pk.REGEX_PATTERN):
            if variable.GetDescription() is None or len(variable.GetDescription()) == 0:
                checkResults.append(CheckResult(f'Description for {var_type} "{variablename}" '
                                                f'should not be empty'))
                return checkResults

            # check if description follows declared pattern
            if not re.match(param_desc.get(pk.REGEX_PATTERN), variable.GetDescription()):
                if pk.CUSTOM_MESSAGE in param_desc:
                    msg = f'Description for {var_type} "{variablename}": ' \
                          f'[{variable.GetDescription()}] does not match pattern. ' \
                          f'{param_desc.get(pk.CUSTOM_MESSAGE)}'
                else:
                    msg = f'Description for {var_type} "{variablename}": ' \
                                  f'[{variable.GetDescription()}] does not match pattern: ' \
                                  f'"{param_desc.get(pk.REGEX_PATTERN)}"'
                checkResults.append(CheckResult(msg))

            return checkResults

    def check_variable_type(self, variable):
        """
        Checks type consistency of a given variable.

        Parameters
        ----------
        variable: the variable to be checked

        Returns
        -------
        check results

        """

        # init clean check result list
        checkResults = []

        variablename = variable.GetName()

        if variable.GetType() == pk.FUNCTION:
            checkResults.append(CheckResult(
                f'Function "{variablename}" is not allowed to be "Parameter" or "ReturnValue"'))
        else:
            checkResults.append(CheckResult(
                f'Variable "{variablename}" may be only of type "Parameter" OR "ReturnValue"'))

        return checkResults

    def check_undefined_type(self, variable):
        """
        Checks varaible type is not undefined.

        Parameters
        ----------
        variable: the variable to be checked

        Returns
        -------
        check results

        """

        # init clean check result list
        checkResults = []

        variablename = variable.GetName()

        if variable.GetType() == pk.UNDEFINED:
            checkResults.append(CheckResult(
                f'Variable type for "{variablename}" should not be "{pk.UNDEFINED}"'))      

        return checkResults
