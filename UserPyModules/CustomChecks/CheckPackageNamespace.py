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
# ParameterKeys.REGEX_PATTERN
# ParameterKeys.CUSTOM_MESSAGE


class CheckPackageNamespace(AbstractPackageCheck):
    """
    Check Package Namespace
    ========================

    Description
    -----------

    Checks whether the package file name is valid.


    Instructions:
    -----------
    Specify the pattern of the checked packages in the YAML configuration file as Regex.
    The parameter for this check is called <RegexPackageName> in the config.yaml.


    Return messages:
    ---------------------
     - "Please save the package <package_name>. Could not find folder location!"
     - "<RegexPattern> is not a valid pattern!"
     - "<PackageName> does not follow name pattern. <CustomMessage>"
     - "<PackageName> does not follow name pattern: <Regex>"


    Limitations
    -----------

    ...

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
        """
        Checks if package name matches regex pattern
        """
        # init clean check result list
        checkResults = []

        package_name = test_item.GetName()
        # Determine package type based on file location
        if test_item.GetFilename() is None:
            checkResults.append(
                CheckResult(f'Please save the package "{package_name}". Could not find folder '
                            f'location!'))
        else:
            try:
                regex = parameters[pk.REGEX_PATTERN]
                re.compile(regex)
            except KeyError:
                checkResults.append(CheckResult(f'No pattern configuration provided. '
                                                f'Please check "{self.config.config_rel_path}"!'))
            except re.error:
                checkResults.append(CheckResult(
                    f'"{parameters[pk.REGEX_PATTERN]}" is not a valid pattern. Check '
                    f'"{self.config.config_rel_path}"!'))
            else:
                # if re.compile is successful the package name check will be performed
                if not re.match(regex, package_name):
                    # check if message for pattern should be more specific
                    if pk.CUSTOM_MESSAGE in parameters:
                        msg = f'{package_name} does not follow name pattern. ' \
                              f'{parameters.get(pk.CUSTOM_MESSAGE)}'
                    else:
                        msg = f'{package_name} does not follow name pattern: "{regex}"'
                    checkResults.append(CheckResult(msg))

        return checkResults
