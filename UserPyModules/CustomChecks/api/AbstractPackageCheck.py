# Copyright (C) 2023 TraceTronic GmbH
#
# SPDX-License-Identifier: MIT

from .AbstractCheck import AbstractCheck


class AbstractPackageCheck(AbstractCheck):
    """
    Base class for all Package checks.
    """

    def __init__(self):
        """
        Constructor.
        """
        super().__init__()  # pylint: disable=W0246

    def Run(self, package):  # pylint: disable=W0237
        """
        Checks the given package and returns the checked results.
        """

        return super().Run(package)  # pylint: disable=W0246
