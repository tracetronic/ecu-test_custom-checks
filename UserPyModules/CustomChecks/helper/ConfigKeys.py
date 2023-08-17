# Copyright (C) 2023 TraceTronic GmbH
#
# SPDX-License-Identifier: MIT

from dataclasses import dataclass

@dataclass(frozen=True)
class ParameterKeys:
    """
    This class supplies all possible config parameter keys used in the CustomChecks as constants.
    """
    ALLOWLIST = 'Allowlist'
    DENYLIST = 'Denylist'
    CHECK = 'Check'
    CUSTOM_MESSAGE = 'CustomMessage'
    DESCRIPTION = 'Description'
    FUNCTION = 'Function'
    LOCALVAR = 'LocalVar'
    UNDEFINED = 'Undefined'
    MINLENGTH = 'MinLength'
    NAME = 'Name'
    NUMBER_OF_RELEVANT_CHARACTERS = 'NumberOfRelevantCharacters'
    ORDER = 'Order'
    PARAMETER = 'Parameter'
    REGEX_DESCRIPTION = 'RegexDescription'
    REGEX_PATTERN = 'RegexPattern'
    RETURNVALUE = 'ReturnValue'
    SORT_METHOD = 'SortMethod'
    TESTCASEFLAG = 'TestCaseFlag'
    VERSION = 'Version'
    ALLOW_UNDEFINED = 'AllowUndefinedVariables'

@dataclass(frozen=True)
class ConditionKeys:
    """
    This class supplies all possible config condition keys used in the CustomChecks as constants.
    """
    PROJECT_NAME = 'ProjectName'
    PACKAGE_NAME = 'PackageName'
    PROJECT_FOLDER = 'ProjectFolder'
    PACKAGE_FOLDER = 'PackageFolder'
    PACKAGE_PROPERTIES = 'PackageProperties'
    REGEX_PATTERN = 'RegexPattern'
    TESTCASEFLAG = 'TestCaseFlag'
    ENABLED = 'Enabled'
