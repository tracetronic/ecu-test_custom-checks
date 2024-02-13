# Copyright (C) 2023 tracetronic GmbH
#
# SPDX-License-Identifier: MIT

import re

from ..api.CheckResult import CheckResult
from .CheckType import CheckType
from .ConfigKeys import ParameterKeys as pk

def check_attributes(test_item, check_type, config, parameters):
    """
    Generic attribute checker, which proceeds conditionally, depending on different test_item types

    Parameters
    ----------
    test_item - Package or Project(from Object API)
    check_type - check type corresponding to test_item (value of enum CheckType)
    config - the current config.yaml object
    parameters - the parameters from the config.yaml for the attribute check

    Returns
    -------
    check results for unsuccessful checks as a list of CheckResult

    """

    # get all attibutes (dict of name and value pairs) from object
    attr_item_dict = test_item.Attributes.GetNamesAndValues()

    param_keys_in_attr = []
    param_keys_not_in_attr = []

    for key in parameters.keys():
        if key in attr_item_dict:
            param_keys_in_attr.append(key)
        else:
            param_keys_not_in_attr.append(key)

    # init clean check result list
    checkResults = []

    # go through all parameters also found in test_item attributes - check: does it have allowed
    # values?
    for key in param_keys_in_attr:
        value = parameters[key]

        if isinstance(value, bool):
            if len(attr_item_dict[key]) == 0 and value is True:
                checkResults.append(CheckResult(f'"{key}" must not be empty!'))
            elif len(attr_item_dict[key]) != 0 and value is False:
                checkResults.append(CheckResult(f'"{key}" must not be set!'))

        # scheme for validating selection attributes
        elif isinstance(value, list):
            # Convert the comma separated string into a set
            # Check if the set of values provided in the project is a subset of the config values
            if not set(attr_item_dict[key].split(",")).issubset(value):
                checkResults.append(CheckResult(f'"{key}" no valid option out of: {str(value)}'))

        # Scheme for applying a regex pattern to an attribute value
        elif isinstance(value, dict):
            # Check if the necessary fields exist
            if pk.REGEX_PATTERN not in value:
                checkResults.append(CheckResult(f'No field: "{pk.REGEX_PATTERN}" was provided!'))
                continue

            regex = value[pk.REGEX_PATTERN]
            # Check if a valid pattern was provided
            try:
                re.compile(regex)
            except re.error:
                checkResults.append(CheckResult(f'{regex} is not a valid pattern! '
                                                f'Check "{config.config_rel_path}"!'))
                continue

            ### CheckPackageAttributes
            if check_type == CheckType.PACKAGE.value:
                # Check if key is set
                if len(attr_item_dict[key]) == 0:
                    checkResults.append(CheckResult(f'"{key}" must not be empty!'))
                # Check if pattern matches the provided value
                elif not re.search(regex, str(attr_item_dict.get(key))):
                    # check if message for pattern should be more specific
                    if pk.CUSTOM_MESSAGE in value:
                        msg = f'"{key}" does not match pattern. "{value.get(pk.CUSTOM_MESSAGE)}"'
                    else:
                        msg = f'"{key}" does not match pattern: "{regex}"'
                    checkResults.append(CheckResult(msg))

            ### CheckProjectAttributes
            elif check_type == CheckType.PROJECT.value:
                # Check if pattern matches the provided value
                if not re.search(regex, str(attr_item_dict.get(key))):
                    if pk.CUSTOM_MESSAGE in value:
                        msg = f'"{key}" does not match pattern: {value.get(pk.REGEX_DESCRIPTION)}'
                    else:
                        msg = f'"{key}" does not match conditions: {regex}'
                    checkResults.append(CheckResult(msg))

    # go through all parameters not found in test_item attributes
    for key in param_keys_not_in_attr:
        value = parameters[key]

        ### CheckPackageAttributes
        if check_type == CheckType.PACKAGE.value:
            if isinstance(value, bool) and value is True:
                checkResults.append(CheckResult(f'"{key}" must not be empty!'))

            elif isinstance(value, list) and value:
                checkResults.append(CheckResult(f'"{key}" must not be empty! Allowed options: '
                                                f'{str(value)}'))

            elif isinstance(value, dict):
                # check if message for value should be more specific
                if pk.CUSTOM_MESSAGE in value:
                    msg = f'"{key}" must not be empty! {value.get(pk.CUSTOM_MESSAGE)}'
                else:
                    msg = f'"{key}" must not be empty! Intended pattern: ' \
                              f'"{value.get(pk.REGEX_PATTERN)}"'
                checkResults.append(CheckResult(msg))

        ### CheckProjectAttributes
        if check_type == CheckType.PROJECT.value:
            if value is not False:
                checkResults.append(CheckResult(f'"{key}" must not be empty'))

    return checkResults
