# Copyright (C) 2023 TraceTronic GmbH
#
# SPDX-License-Identifier: MIT

from enum import Enum


class CheckType(Enum):
    """
    Enum for type of test item
    """
    PACKAGE = 'PACKAGE_CHECK'
    ANALYSIS = 'ANALYSIS_PACKAGE_CHECK'
    PROJECT = 'PROJECT_CHECK'
