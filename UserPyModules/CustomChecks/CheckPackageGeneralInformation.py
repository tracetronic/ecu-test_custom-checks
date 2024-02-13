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
# ParameterKeys.DESCRIPTION
# ParameterKeys.CHECK
# ParameterKeys.MINLENGTH
# ParameterKeys.REGEX_PATTERN
# ParameterKeys.CUSTOM_MESSAGE
# ParameterKeys.TESTCASEFLAG
# ParameterKeys.VERSION


class CheckPackageGeneralInformation(AbstractPackageCheck):
    """
    Check Package General Information
    =================================

    Description
    -----------

    Checks whether the general package information are valid.


    Specifics and Results
    ---------------------

    Checks the following fields:

    - Package description
    - Package version
    - Package test case flag

    Return messages:

    - "Description must not be empty!"
    - "Description insufficient. Should contain at least <value> characters!"
    - "Description should contain pattern.<CustomMessage>"
    - "Description should contain pattern: <RegexPattern>"
    - "TestCaseFlag must be set!"
    - "TestCaseFlag must not be set!"
    - "'<RegexPattern>' is not a valid regular expression pattern. Check <config file>!"
    - "'<Version>' does not match pattern <RegexPattern>"


    Limitations
    -----------

    - When more flags are added in the config, the source code needs to be extended

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
        # init clean check result list
        checkResults = []

        # Check the Description
        if pk.DESCRIPTION in parameters.keys() and parameters[pk.DESCRIPTION].get(pk.CHECK) is True:
            checkResults.extend(self.check_description(test_item, parameters[pk.DESCRIPTION]))

        # Check the TestCaseFlag
        if pk.TESTCASEFLAG in parameters.keys():
            checkResults.extend(self.check_test_case_flag(test_item, parameters[pk.TESTCASEFLAG]))

        # Check the Version
        if pk.VERSION in parameters.keys():
            checkResults.extend(self.check_version(test_item, parameters[pk.VERSION]))

        return checkResults

    def check_description(self, package, description):
        """
        Checks the description

        Parameters
        ----------
        package: Package object
            the package
        description: dict
            Description entry in the configuration

        Returns
        -------
        check results

        """
        checkResults = []
        desc_len = len(package.GetDescription())

        # Check if description is empty
        if desc_len == 0:
            checkResults.append(
                CheckResult('Description must not be empty!'))
            return checkResults

        # Check if description contains at least MINLENGTH characters
        if pk.MINLENGTH in description:
            min_desc_len = description[pk.MINLENGTH]
            if desc_len < min_desc_len:
                checkResults.append(CheckResult(f'Description insufficient. '
                                                f'Should contain at least {min_desc_len} '
                                                f'characters!'))

        # Check if descriptions contains the declared pattern
        if pk.REGEX_PATTERN in description:
            regex = description.get(pk.REGEX_PATTERN)
            try:
                re.compile(regex)
            except re.error:
                checkResults.append(CheckResult(f'"{regex}" is not a valid pattern. '
                                                f'Check "{self.config.config_rel_path}"!'))
            else:
                # if re.compile is successful the description check will be performed
                if not re.search(regex, package.GetDescription()):
                    # check if message for pattern should be more specific
                    if pk.CUSTOM_MESSAGE in description:
                        msg = f'Description should contain pattern. ' \
                              f'{description.get(pk.CUSTOM_MESSAGE)}'
                    else:
                        msg = f'Description should contain pattern: "{regex}"'
                    checkResults.append(CheckResult(msg))

        return checkResults

    def check_test_case_flag(self, package, tc_flag):
        """
        Checks whether the test case flag is set

        Parameters
        ----------
        package: Package object
            the package
        tc_flag: bool
            tc_flag from the configuration

        Returns
        -------
        check results

        """
        checkResults = []

        if tc_flag is True and not package.HasTestCaseFlag():
            checkResults.append(CheckResult('"Test case" flag must be set!'))

        elif tc_flag is False and package.HasTestCaseFlag():
            checkResults.append(CheckResult('"Test case" flag must not be set!'))

        return checkResults

    def check_version(self, package, version):
        """
        Checks the version

        Parameters
        ----------
        package: Package object
            the package
        version: any
            entry from the configuration

        Returns
        -------
        check results

        """
        checkResults = []

        # Check if version must be set at all
        if isinstance(version, bool):
            if not package.GetVersion() and version:
                checkResults.append(CheckResult('Version must be set!'))
            elif version is False:
                WPrint('Version check is disabled!')
            return checkResults

        # check whether version is set when it should be
        if not package.GetVersion():
            checkResults.append(CheckResult('Version must be set!'))
            return checkResults

        # Check if given regex pattern is valid, given that the version is set
        regex = version.get(pk.REGEX_PATTERN)
        try:
            re.compile(regex)
        except re.error:
            checkResults.append(CheckResult(f'"{regex}" is not a valid pattern. '
                                            f'Check "{self.config.config_rel_path}"!'))
            return checkResults

        # Check if pattern matches the provided value
        if not re.search(regex, package.GetVersion()):
            # check if message for pattern should be more specific
            if pk.CUSTOM_MESSAGE in version:
                msg = f'Version "{package.GetVersion()}" does not match pattern. ' \
                      f'{version.get(pk.CUSTOM_MESSAGE)}'
            else:
                msg = f'Version "{package.GetVersion()}" does not match pattern: "{regex}"'
            checkResults.append(CheckResult(msg))

        return checkResults
