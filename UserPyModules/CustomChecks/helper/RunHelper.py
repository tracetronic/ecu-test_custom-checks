# Copyright (C) 2023 TraceTronic GmbH
#
# SPDX-License-Identifier: MIT

import re
from . import ecu_test_api
from . import Configuration
from .ConfigKeys import ConditionKeys as ck

try:
    from tts.core.logging import SPrint, WPrint, EPrint, DPrint  # pylint: disable=E0401
    api = ecu_test_api.get_api()
    pkgApi = api.ObjectApi.PackageApi
except:
    from logging import info as SPrint, warning as WPrint, error as EPrint, debug as DPrint

# keys declared in "conditions" in config.yaml:
# ConditionKeys.PROJECT_NAME
# ConditionKeys.PACKAGE_NAME
# ConditionKeys.PROJECT_FOLDER
# ConditionKeys.PACKAGE_FOLDER
# ConditionKeys.PACKAGE_PROPERTIES
# ConditionKeys.REGEX_PATTERN
# ConditionKeys.TESTCASEFLAG
# ConditionKeys.ENABLED


def check_conditions(check_name, check_object, check) -> bool:
    """
    Checks whether the conditions of the check_object to execute a specific check are fulfilled.
    These conditions are specified under the respective 'Conditions' section in the config.yaml.

    Parameters
    ----------
    check_name: Current CustomCheck name
    check_object: ECU-TEST Package-Object, Project-Object from Object Api
    check: Current type of package that gets checked for conditions

    Returns
    -------
    True if all conditions are fulfilled for this package
    """
    # check conditions in detail for the given package
    result_list = [True]  # init with True if no conditions are defined in config.yaml
    conditions = Configuration.Configuration().get_check_conditions(check_name, check)

    for condition in conditions:
        # check package name pattern
        if condition in (ck.PACKAGE_NAME, ck.PROJECT_NAME):
            regex = conditions[condition][ck.REGEX_PATTERN]
            if re.search(regex, check_object.GetName()):
                result_list.append(True)
            else:
                result_list.append(False)
        # check package path pattern
        elif condition in (ck.PACKAGE_FOLDER, ck.PROJECT_FOLDER):
            regex = conditions[condition][ck.REGEX_PATTERN]
            if re.search(regex, check_object.GetFilename()):
                result_list.append(True)
            else:
                result_list.append(False)
        # check package properties
        elif condition == ck.PACKAGE_PROPERTIES:
            testCaseFlag = check_object.HasTestCaseFlag()
            if conditions[condition][ck.TESTCASEFLAG] == testCaseFlag:
                result_list.append(True)
            else:
                result_list.append(False)
        # error handling
        else:
            WPrint(f'Condition "{condition}" is not implemented!')

    return all(result_list)


def get_check_activity(check):
    """
    Parameters
    ----------
    check: Current check configurations in config file

    Returns
    -------
    True if check is set active in config or flag is missing
    Check configurations with the 'Enabled' flag removed
    """
    try:
        is_active = check.pop(ck.ENABLED)
        return is_active, check

    except:
        return True, check


def package_type(check_name, check_object, check) -> bool:
    """
    Parameters
    ----------
    check_name: Current CustomCheck name
    check_object: ECU-TEST-Package-Object from Object Api
    check: Current type of package that gets checked for conditions

    Returns
    -------
    True if check_conditions was successful
    """

    DPrint(3, f'Internal check "{check}"')
    # check if the conditions are True
    if check_conditions(check_name, check_object, check):
        DPrint(3, f'"{check_object.GetName()}", conditions are {True}. Check is running.')
    else:
        DPrint(3, f'"{check_object.GetName()}", conditions are {False}. Check will not be '
                  f'performed.')
        return False
    return True
