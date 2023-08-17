# Copyright (C) 2023 TraceTronic GmbH
#
# SPDX-License-Identifier: MIT

from .AbstractCheck import AbstractCheck


class AbstractProjectCheck(AbstractCheck):
    """
    Base class for all Project checks.
    """

    def __init__(self):
        """
        Constructor.
        """
        super().__init__()  # pylint: disable=W0246

    def Run(self, project):  # pylint: disable=W0237
        """
        Checks the given project and returns the checked results.
        """

        return super().Run(project)  # pylint: disable=W0246
