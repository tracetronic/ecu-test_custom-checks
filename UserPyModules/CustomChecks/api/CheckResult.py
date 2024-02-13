# Copyright (C) 2023 tracetronic GmbH
#
# SPDX-License-Identifier: MIT

from dataclasses import dataclass


@dataclass
class CheckResult:
    """
    A check result for check violations.
    """

    message: str
