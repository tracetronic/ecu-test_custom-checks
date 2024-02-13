# Copyright (C) 2023 tracetronic GmbH
#
# SPDX-License-Identifier: MIT

from abc import ABC, abstractmethod
from typing import List

from ..helper.RunHelper import package_type, get_check_activity
from ..helper.Configuration import Configuration


class AbstractCheck(ABC):
    """
    Base class for all checks. The 'GetName' and 'check' methods need to be implemented in the
    actual checks.
    """

    def __init__(self):
        """
        Constructor.
        """
        self.config = Configuration()

    @abstractmethod
    def GetName(self) -> str:
        """
        Will always be implemented in the custom check as
        return type(self).__name__ and returns the name of the class type.
        Belongs to the CustomChecks interface for ecu.test.

        Returns
        -------

        """
        raise NotImplementedError


    @abstractmethod
    def check(self, test_item, parameters) -> List:
        """
        Needs to be implemented in the custom check (template method)

        Parameters
        ----------
        test_item: item from Object API
            generic test item; Package, Project or AnalysisPackage
        parameters: any
            the Parameters entry from config.yaml

        Returns
        -------
        list of CheckResult (empty if no violation was found)

        """
        raise NotImplementedError

    def Run(self, test_item):
        """
        Executes the checks. Uses the template method 'check', which must be implemented in the
        check modules. Belongs to the CustomChecks interface for ecu.test.

        Parameters
        ----------
        test_item: item from Object API
            generic test item; Package, Project or AnalysisPackage

        Returns
        -------
            list of CheckResult (empty if no violation was found)

        """
        check_results = []

        check_name = self.GetName()

        is_active, active_checks = get_check_activity(self.config.get_all_checks(check_name))

        if not is_active:
            return check_results

        for check in active_checks:

            # internal conditions check for the package type
            if package_type(check_name, test_item, check):

                # returns a list of the parameters configured in config file
                parameters = self.config.get_check_parameters(check_name, check)
                check_results.extend(self.check(test_item, parameters))

        return check_results
