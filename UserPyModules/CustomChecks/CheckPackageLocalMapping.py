# Copyright (C) 2023 TraceTronic GmbH
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-
from typing import List

from .api.AbstractPackageCheck import AbstractPackageCheck
from .api.CheckResult import CheckResult
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


# keys declared in "parameters" in config.yaml:
# ParameterKeys.DENYLIST

class CheckPackageLocalMapping(AbstractPackageCheck):
    """
    Check Local Package Mapping
    =================================

    Description
    -----------

    Checks whether the package has forbidden mapping types in its local mapping via a denylist.


    Specifics and Results
    ---------------------

    Instructions:

    Specify the forbidden mapping types in the YAML configuration file

    Return messages:

    - "mapping item with name '<mapping name>' is of type '<mapping type>' which is forbidden!"


    Limitations
    -----------

    """

    def __init__(self, internalApi):  # pylint: disable=W0613
        """
        Constructor
        """
        super().__init__()

    def GetName(self) -> str:
        """
        Name to be shown in UI and used in the config.yaml
        """
        return type(self).__name__

    def check(self, test_item, parameters) -> List[CheckResult]:
        checkResults = []
        checkResults.extend(self.check_package_mapping_types(test_item, parameters))
        return checkResults

    def check_package_mapping_types(self, package, parameters) -> List[CheckResult]:
        """
        Check a package for forbidden mapping types in local mapping

        Parameters
        ----------
        package: Package object
            the package
        parameters: Dict
            the custom check parameters

        Returns
        -------
        check results
        """
        checkResults = []

        deny_list = parameters.get(pk.DENYLIST)

        if not deny_list:
            return [CheckResult(
                f'Parameter {pk.DENYLIST!r} not configured for the check {self.GetName()!r} '
                f'in the config. Please check {self.config.config_rel_path!r}!')]

        local_mapping = package.GetMapping()

        for mapping_item in local_mapping.GetItems():
            checkResults.extend(
                self.check_mapping_item_mapping_type(mapping_item, deny_list)
            )

        return checkResults

    def check_mapping_item_mapping_type(self, mapping_item, deny_list) -> List[CheckResult]:
        """
        Check a single mapping item for forbidden types

        Parameters
        ----------
        mapping_item: Mapping item object
            the mapping item
        deny_list: List
            list of forbidden mapping types

        Returns
        -------
        check results
        """
        checkResults = []
        mapping_type = mapping_item.GetAccessType()

        if mapping_type in deny_list:
            checkResults.append(CheckResult(
                f'Mapping item with name {mapping_item.GetReferenceName()!r} '
                f'is of type {mapping_type!r} which is forbidden!'))

        return checkResults
