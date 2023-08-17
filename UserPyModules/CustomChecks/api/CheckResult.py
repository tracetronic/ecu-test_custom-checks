# Copyright (C) 2023 TraceTronic GmbH
#
# SPDX-License-Identifier: MIT

from dataclasses import dataclass


@dataclass
class CheckResult:
    """
    A check result for check violations.
    """

    message: str
