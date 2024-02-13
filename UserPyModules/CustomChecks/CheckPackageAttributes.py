# Copyright (C) 2023 tracetronic GmbH
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-
from typing import List

from .api.AbstractPackageCheck import AbstractPackageCheck
from .helper.CheckType import CheckType
from .helper.CheckAttributes import check_attributes

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


class CheckPackageAttributes(AbstractPackageCheck):
    """
    Check Package Attributes
    =========================

    Description
    -----------

    Checks whether all package attributes are set according to YAML config.

    Specifics and Results
    ---------------------

    Instructions:

    Specify the attributes to be checked in the YAML configuration file according to the following
    pattern. Three types of checks are possible

    1. Check if a value should exist for a specific attribute or if attributes should be left empty:
        <attribute name>: True, False

    2. Check if a selected attribute value is in a list of allowed choices:
        <attribute name>:
            [<choice one>, <choice two>, ...]

    3. Check if an attribute matches a specific pattern
        <attribute name>:
            "RegexPattern": <your pattern>
            ("RegexDescription": <description for error print>) optional

    Return messages:

    - "<attribute name> must not be empty"
    - "<attribute name> must not be set"
    - "<attribute name> no valid option out of: <attributes options>"
    - <attribute name> must not be empty! <CustomMessage>
    - <attribute name> must not be empty! Intended pattern: <RegexPattern>
    - <attribute name> must not be empty! Allowed options: <list>
    - <attribute name> does not match pattern. <CustomMessage>
    - <attribute name> does not match pattern: <RegexPattern>
    - "No field: 'RegexPattern' was provided!"
    - "<Provided pattern> is not a valid pattern!"

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
        return check_attributes(test_item, MODULE_TYPE, self.config, parameters)
