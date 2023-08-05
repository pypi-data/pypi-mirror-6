# ======================= QuantGo Copyright Notice ============================
# Copyright 2013 QuantGo, LLC.  All rights reserved.
# Permission to use solely inside a QuantGo Virtual Quant Lab
# Written By: Nikolay
# Date: 12-12.2013
# ======================= QuantGo Copyright Notice ============================

main_parser_schema = {
    "main": {
        "additionalProperties": False,
        "name": "Main",
        "description": "Service cli tool.",
        "usage": "service <action> [--host, --port, --name, --params, --save-file, --no-update, --help]",
        "properties": {
            "host": {
                "name": "host",
                "description": "Server address to send request to. Normally: service.quantgo.com.",
                "required": False,
                "type": "string"
            },
            "port": {
                "name": "Port",
                "description": "Service server port. Default: 9999.",
                "required": False,
                "type": "integer"
            },
            "save-file": {
                "name": "SaveFile",
                "description": "File to save output to.",
                "required": False,
                "type": "string"
            },
            "no-update": {
                "name": "NoUpdate",
                "description": "Disable software update check.",
                "required": False,
                "type": "boolean"
            },
            "help": {
                "name": "Help",
                "description": "Print this help message.",
                "required": False,
                "type": "help"
            },
            "debug": {
                "name": "Debug",
                "description": "Enable DEBUG mode.",
                "required": False,
                "type": "boolean"
            }
        },
        "type": "object"
    }
}

commands = {
    "get-data": {
        "additionalProperties": False,
        "name": "Get-Data",
        "description": "Get data for service name. Use --name parameter for service name.",
        "properties": {
            "name": {
                "name": "ServiceName",
                "description": "Name of service to be requested.",
                "required": True,
                "type": "string"
            },
            "params": {
                "name": "Parameters",
                "description": "Parameters for service name.",
                "required": False,
                "type": "string"
            }
        },
        "type": "object"
    },
    "get-service-specific": {
        "additionalProperties": False,
        "name": "Get-Data",
        "description": "Get specific service data. Use --name parameter for service name.",
        "properties": {
            "name": {
                "name": "ServiceName",
                "description": "Name of service to be requested.",
                "required": True,
                "type": "string"
            },
            "params": {
                "name": "Parameters",
                "description": "Parameters for service name.",
                "required": False,
                "type": "string"
            }
        },
        "type": "object"
    },
    "list":{
        "additionalProperties": False,
        "name": "List",
        "description": "List all services.",
        "type": "boolean",
        "required":False
    },
    "available":{
        "additionalProperties": False,
        "name": "Available",
        "description": "List services available for user.",
        "type": "boolean",
        "required":False
    },
    "description":{
        "additionalProperties": False,
        "name": "Description",
        "description": "Description of a service. Use --name parameter for service name.",
        "properties": {
            "name": {
                "name": "ServiceName",
                "description": "Name of service to be requested.",
                "required": True,
                "type": "string"
            }
        },
        "type": "object"
    }
}
