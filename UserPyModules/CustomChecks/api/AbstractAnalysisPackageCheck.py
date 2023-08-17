# Copyright (C) 2023 TraceTronic GmbH
#
# SPDX-License-Identifier: MIT

from .AbstractCheck import AbstractCheck


class AbstractAnalysisPackageCheck(AbstractCheck):
    """
    Base class for all AnalysisPackage checks.
    """

    def Run(self, analysisPackage): # pylint: disable=W0237
        """
        Checks the given analysis package and returns the checked results.
        """

        return super().Run(analysisPackage)
