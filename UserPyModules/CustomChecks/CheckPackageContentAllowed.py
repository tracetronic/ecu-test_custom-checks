# Copyright (C) 2023 TraceTronic GmbH
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-
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

# keys declared in "parameters" in config.yaml
# ParameterKeys.ALLOWLIST


class CheckPackageContentAllowed(AbstractPackageCheck):
    """
    Check Package Content
    =================================

    Description
    -----------

    Checks whether the package has forbidden content via an allowlist.


    Specifics and Results
    ---------------------

    Checks for following forbidden test steps:

    - To-Do test step
    - Pre- or Postcondition

    Return messages:

    - "Not allowed content of type <ts_type> in line <ts_line>!"


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
        # init clean check result list
        checkResults = []

        # Check for not allowed content
        ts_list = test_item.GetTestSteps(recursive=True)
        allowedContent = parameters[pk.ALLOWLIST]

        if not allowedContent:
            return checkResults

        for testStep in ts_list:
            if testStep.GetType() not in allowedContent:
                checkResults.append(
                CheckResult(f"Not allowed content of type {testStep.GetType()} in line "
                            f"{testStep.GetLineNo()}!"))
        return checkResults
