# Copyright (C) 2023 tracetronic GmbH
#
# SPDX-License-Identifier: MIT

# encoding: ISO-8859-1 # pylint: disable=C2503
"""
Wrapper for importing ecu.test ApiClient of currently running ecu.test version.
"""

try:
    from log import SPrint, WPrint, EPrint
except:
    from logging import info as SPrint, warning as WPrint, error as EPrint

API_HANDLER = None

ECU_TEST_ENV = {"ECU-TEST.exe", "ecu.test.exe", "ecu-test_daemon"}


def get_api():
    """
    Returns an instance of the ecu.test api
    """
    global API_HANDLER  # pylint: disable=W0603
    if API_HANDLER is None:
        from application.api.Api import Api  # pylint: disable=E0401
        API_HANDLER = Api()

    return API_HANDLER


def get_object_api():
    """
    Gets the Object API of ecu.test.

    Returns
    -------
        object api handler

    """

    return get_api().ObjectApi


class ObjApiProvider():
    """
    Class to inherit from to have access to the object api
    """

    def __init__(self):
        self._obj_api = None

    @property
    def obj_api(self):
        """

        Returns
        -------
            ecu.test Object API

        """
        if self._obj_api is None:
            self._obj_api = get_object_api()
        return self._obj_api

    @property
    def pkg_api(self):
        """

        Returns
        -------
            PackageApi from the ecu.test Object API

        """
        return self.obj_api.PackageApi

    @property
    def ta_api(self):
        """

        Returns
        -------
            TraceAnalysisApi from the ecu.test Object API

        """
        return self.pkg_api.TraceAnalysisApi

    @property
    def map_api(self):
        """

        Returns
        -------
            MappingApi from the PackageApi

        """
        return self.pkg_api.MappingApi

    @property
    def prj_api(self):
        """

        Returns
        -------
            ProjectApi from the ecu.test Object API

        """
        return self.obj_api.ProjectApi

    @property
    def comp_api(self):
        """

        Returns
        -------
            ComponentApi from the ProjectApi

        """
        return self.prj_api.ComponentApi
