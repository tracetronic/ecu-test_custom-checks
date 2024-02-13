# Copyright (C) 2023 tracetronic GmbH
#
# SPDX-License-Identifier: MIT

import os
import shutil
from io import open
from yaml import safe_load

try:
    from tts.core.logging import WPrint
    from tts.core.api.internalApi.Api import Api
    api = Api()
except:
    from logging import warning as WPrint


# folder name for the configuration file
CONFIGURATION_FOLDER = 'CustomChecks'

# name of the configuration file:
CONFIGURATION_FILE = 'config.yaml'
CONFIGURATION_TEMPLATE_FILE = 'config_template.yaml'

JSON_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "required": [
        "CheckPackageGeneralInformation",
        "CheckPackageContentNotEmpty",
        "CheckPackageForbiddenContent",
        "CheckPackageStructure"
    ],
    "type": "object",
    "properties": {
        "CheckPackageGeneralInformation": {
            "required": [
                "Execution",
                "Parameters"
            ],
            "type": "object",
            "properties": {
                "Execution": {
                    "type": "boolean"
                },
                "Parameters": {
                    "required": [
                        "Version",
                        "Description",
                        "TestCaseFlag"
                    ],
                    "type": "object",
                    "properties": {
                        "Version": {
                            "required": [
                                "RegexPattern",
                                "RegexDescription"
                            ],
                            "type": "object",
                            "properties": {
                                "RegexPattern": {
                                    "type": "string"
                                },
                                "RegexDescription": {
                                    "type": "string"
                                }
                            },
                            "additionalProperties": False
                        },
                        "Description": {
                            "type": "boolean"
                        },
                        "TestCaseFlag": {
                            "type": "boolean"
                        }
                    },
                    "additionalProperties": False
                }
            },
            "additionalProperties": False
        },
        "CheckPackageContentNotEmpty": {
            "required": [
                "Execution",
                "Parameters"
            ],
            "type": "object",
            "properties": {
                "Execution": {
                    "type": "boolean"
                },
                "Parameters": {
                    "type": "string"
                }
            },
            "additionalProperties": False
        },
        "CheckPackageForbiddenContent": {
            "required": [
                "Execution",
                "Parameters"
            ],
            "type": "object",
            "properties": {
                "Execution": {
                    "type": "boolean"
                },
                "Parameters": {
                    "type": "string"
                }
            },
            "additionalProperties": False
        },
        "CheckPackageStructure": {
            "required": [
                "Execution",
                "Parameters"
            ],
            "type": "object",
            "properties": {
                "Execution": {
                    "type": "boolean"
                },
                "parameters": {
                    "required": [
                        "TestStepLimit",
                        "StartStop"
                    ],
                    "type": "object",
                    "properties": {
                        "TestStepLimit": {
                            "type": "integer"
                        },
                        "StartStop": {
                            "required": [
                                "Trace",
                                "Stimulus",
                                "Simulation"
                            ],
                            "type": "object",
                            "properties": {
                                "Trace": {
                                    "type": "boolean"
                                },
                                "Stimulus": {
                                    "type": "boolean"
                                },
                                "Simulation": {
                                    "type": "boolean"
                                }
                            },
                            "additionalProperties": False
                        }
                    },
                    "additionalProperties": False
                }
            },
            "additionalProperties": False
        }
    },
    "additionalProperties": False
}


class Configuration:
    """
    A class to represent the CustomChecks configuration (config.yaml).

    Attributes
    ----------
    config_rel_path : str
        name of the check
    config : list of dict
        input from yaml file

    Methods
    -------
    get_all_checks(custom_check_name):
        Return all checks from yaml
    get_check_parameters(check_name):
        Return parameters
    get_check_conditions(custom_check_name, check):
        Get all conditions for the given check
    """

    def __init__(self):
        """
        Constructor
        """

        self.config, self.config_rel_path = self.initialize_config()

    def get_all_checks(self, custom_check_name):
        """
        Get the list of detail check conditions.

        Parameters
        ----------
        custom_check_name : str
            Name of the check.

        Returns
        -------
            dictionary with check details
        """
        checks = {}

        for check in self.config[custom_check_name]:
            checks[check] = self.config[custom_check_name][check]

        return checks

    def get_check_conditions(self, custom_check_name, check):
        """
        Get all conditions for the given check.

        Parameters
        ----------
        custom_check_name : str
            Name of the check.

        check : dict
            Dictionary with all items of the check

        Returns
        -------
            Conditions of the check
        """
        try:
            return self.config[custom_check_name][check]['Conditions']
        except:
            return []

    def get_check_parameters(self, custom_check_name, check):
        """
        Get all parameters for the given check.

        Parameters
        ----------
        custom_check_name : str
            Name of the check.

        check : dict
            Dictionary with all items of the check

        Returns
        -------
            Parameters of the check
        """
        try:
            return self.config[custom_check_name][check]['Parameters']
        except:
            raise KeyError((f'No configuration parameters/attributes provided for '
                             f'{custom_check_name} '
                             f'check in "{self.config_rel_path}"!'))

    def initialize_config(self, ref_config_folder=CONFIGURATION_FOLDER,
                          ref_config_path=CONFIGURATION_FILE,
                          ref_config_template_path=CONFIGURATION_TEMPLATE_FILE):

        """
        Initializes the Configuration.

        Parameters
        ----------
        ref_config_folder: str
            path to the folder of the reference configuration
        ref_config_path: str
            path to the reference configuration file
        ref_config_template_path: str
            path to the reference template configuration file

        Returns
        -------
        tuple (object of used configuration, relative path of the used configuration)

        """

        parameter_path = api.GetSetting('parameterPath')
        config_template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                            ref_config_template_path)
        config_path = os.path.join(parameter_path, ref_config_folder, ref_config_path)

        # store relative path for config file
        config_rel_path = os.path.relpath(config_path,
                                          api.GetSetting('workspacePath')
                                          .removesuffix('ECU-TEST')
                                          .removesuffix('ecu.test'))

        # create config file from template if file not found under parameters in ecu.test
        # workspace
        if not os.path.exists(config_path):
            if not os.path.exists(os.path.join(parameter_path, ref_config_folder)):
                os.mkdir(os.path.join(parameter_path, ref_config_folder))
            shutil.copy(config_template_path, config_path)
            WPrint(f'Using a default config for the CustomChecks. Please modify your '
                   f'CustomCheck configuration file '
                   f'{ref_config_path} in "{config_rel_path}"!')


        # get configuration from yaml
        with open(config_path, 'r') as stream:
            config = safe_load(stream)

        return config, config_rel_path
