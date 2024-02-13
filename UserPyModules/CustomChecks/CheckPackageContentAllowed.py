# Copyright (C) 2023 tracetronic GmbH
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
# ParameterKeys.SEARCH_DEPTH


class CheckPackageContentAllowed(AbstractPackageCheck):
    """
    Check Package for allowed test steps
    ========================

    Description
    -----------

    Checks whether the target package only consists of the specified test steps
    in the configured package layers.

    Instructions:
    -----------
    to configure this test in the config.yaml, add allowed TestStep-Types in
    AllowList Parameter and the considered SearchDepth, if no SearchDepth is configured,
    all package layers are checked.


    Return messages:
    ---------------------
     - "Not allowed content of type <ts_type> in line <ts_line>!"
    """

    def __init__(self, internalApi):  # pylint: disable=W0613
        """
        Constructor
        """
        super().__init__()
        self.checkResults = []

    # needs to be there, leave untouched
    def GetName(self) -> str:
        """
        Name to be shown in UI and used in the config.yaml
        """
        return type(self).__name__

    def check(self, test_item, parameters) -> List:
        allow_list = parameters.get(pk.ALLOWLIST)
        search_depth = parameters.get(pk.SEARCH_DEPTH)

        if not allow_list:
            return [CheckResult(
                f'Parameter {pk.ALLOWLIST!r} not configured '
                f'for the check {self.GetName()!r} in the config. '
                f'Please check {self.config.config_rel_path!r}!')]

        if not search_depth:
            search_depth = float('inf')

        for test_step in self.get_test_steps_of_item(test_item):
            self.check_test_step(test_step=test_step,
                                 layer=0,
                                 allow_list=allow_list,
                                 search_depth=search_depth)

        return self.checkResults

    def check_test_step(self, test_step, layer, allow_list, search_depth) -> None:
        """
        Check if the test step is allowed by the defined allow list;
        checks child test steps recursively as well for the given search depth

        Parameters
        ----------
        test_step: TestStep object
            the test step item
        layer: int
            the current package layer
        allow_list: List[str]
            allowed test step types
        search_depth: int
            the search depth

        Returns
        -------
        None
        """
        if layer >= search_depth:
            return

        if test_step.GetType() not in allow_list:
            self.checkResults.append(CheckResult(
                f"Not allowed content of type {test_step.GetType()} in line "
                f"{test_step.GetLineNo()}!"))

        for child in self.get_test_steps_of_item(test_step):
            self.check_test_step(test_step=child,
                                 layer=layer + 1,
                                 allow_list=allow_list,
                                 search_depth=search_depth)

    def get_test_steps_of_item(self, item) -> List:
        """
        Gets the test steps of the target item

        Parameters
        ----------
        item: Package object or TestStep object
            tha package or test step item

        Returns
        -------
        test step items
        """
        try:
            return item.GetTestSteps(skipDisabledSteps=False,
                                     recursive=False,
                                     whiteList=None,
                                     blackList=None)
        except AttributeError:
            # test step does not have test step children
            return []
