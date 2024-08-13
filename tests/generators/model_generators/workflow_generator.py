from json import loads
from typing import Any, Dict, List

from mmisp.db.models.workflow import Workflow
from mmisp.workflows.fastapi import json_dict_to_workflow_entity


def generate_workflows() -> List[Workflow]:
    json_workflows = []
    json_workflows.append(attribute_after_save_workflow())
    json_workflows.append(event_after_save_workflow())

    workflows: List[Workflow] = []
    for json_workflow in json_workflows:
        workflow: Workflow = json_dict_to_workflow_entity(json_workflow)
        workflows.append(
            Workflow(
                name=workflow.name,
                description=workflow.description,
                timestamp=workflow.timestamp,
                data=workflow.data,
                trigger_id=workflow.trigger_id,
            )
        )
    return workflows


def genrerate_workflow_with_id(id: int) -> Workflow:
    workflow = loads("""{
    "Workflow": {
        "id": "78132549",
        "uuid": "17fa92d1-7b40-444c-8629-a0686965d38b",
        "name": "Workflow for testing",
        "description": "",
        "timestamp": "1718632138",
        "enabled": false,
        "counter": "0",
        "trigger_id": "attribute-after-save",
        "debug_enabled": false,
        "data": {
            "1": {
                "class": "block-type-trigger",
                "data": {
                    "id": "attribute-after-save",
                    "scope": "attribute",
                    "name": "Attribute After Save",
                    "description": "This trigger is called after an Attribute has been saved in the database",
                    "icon": "cube",
                    "inputs": 0,
                    "outputs": 1,
                    "blocking": false,
                    "misp_core_format": true,
                    "trigger_overhead": 3,
                    "trigger_overhead_message": "This trigger is called each time an Attribute has been saved. [...]",
                    "is_misp_module": false,
                    "is_custom": false,
                    "expect_misp_core_format": false,
                    "version": "0.1",
                    "icon_class": "",
                    "multiple_output_connection": false,
                    "support_filters": false,
                    "saved_filters": [
                        {
                            "text": "selector",
                            "value": ""
                        },
                        {
                            "text": "value",
                            "value": ""
                        },
                        {
                            "text": "operator",
                            "value": ""
                        },
                        {
                            "text": "path",
                            "value": ""
                        }
                    ],
                    "params": [],
                    "module_type": "trigger",
                    "html_template": "trigger",
                    "disabled": false
                },
                "id": 1,
                "inputs": [],
                "outputs": {
                    "output_1": {
                        "connections": []
                    }
                },
                "pos_x": 0,
                "pos_y": 0,
                "typenode": false
            }
        },
        "listening_triggers": [
            {
                "id": "attribute-after-save",
                "scope": "attribute",
                "name": "Attribute After Save",
                "description": "This trigger is called after an Attribute has been saved in the database",
                "icon": "cube",
                "inputs": 0,
                "outputs": 1,
                "blocking": false,
                "misp_core_format": true,
                "trigger_overhead": 3,
                "trigger_overhead_message": "This trigger is called each time an Attribute has been saved. [...]",
                "is_misp_module": false,
                "is_custom": false,
                "expect_misp_core_format": false,
                "version": "0.1",
                "icon_class": "",
                "multiple_output_connection": false,
                "support_filters": false,
                "saved_filters": [
                    {
                        "text": "selector",
                        "value": ""
                    },
                    {
                        "text": "value",
                        "value": ""
                    },
                    {
                        "text": "operator",
                        "value": ""
                    },
                    {
                        "text": "path",
                        "value": ""
                    }
                ],
                "params": [],
                "module_type": "trigger",
                "html_template": "trigger",
                "disabled": false
            }
        ]
    }
}""")
    workflow["Workflow"]["id"] = id
    return json_dict_to_workflow_entity(workflow)


def event_after_save_workflow() -> Dict[str, Any]:
    return loads("""{
        "Workflow": {
        "id": "16",
        "uuid": "b0afa8b4-4d88-4d83-a9d9-4ef0a4548667",
        "name": "Workflow for trigger event-after-save-new",
        "description": "",
        "timestamp": "1714826096",
        "enabled": false,
        "counter": "5",
        "trigger_id": "event-after-save-new",
        "debug_enabled": false,
        "data": {
            "1": {
                "id": 1,
                "name": "Event After Save New",
                "data": {
                    "id": "event-after-save-new",
                    "scope": "event",
                    "name": "Event After Save New",
                    "description": "This trigger is called after a new Event has been saved in the database",
                    "icon": "envelope",
                    "inputs": 0,
                    "outputs": 1,
                    "blocking": false,
                    "misp_core_format": true,
                    "trigger_overhead": 1,
                    "trigger_overhead_message": "",
                    "is_misp_module": false,
                    "is_custom": false,
                    "expect_misp_core_format": false,
                    "version": "0.1",
                    "icon_class": "",
                    "multiple_output_connection": false,
                    "support_filters": false,
                    "saved_filters": {
                        "selector": "",
                        "value": "",
                        "operator": "",
                        "path": ""
                    },
                    "module_type": "trigger",
                    "html_template": "trigger",
                    "disabled": true,
                    "node_uid": "9p07ghnbao96m9",
                    "indexed_params": [],
                    "previous_module_version": "0.1",
                    "module_version": "0.1"
                },
                "class": "block-type-trigger",
                "typenode": false,
                "inputs": [],
                "outputs": {
                    "output_1": {
                        "connections": [
                            {
                                "node": "5",
                                "output": "input_1"
                            }
                        ]
                    }
                },
                "pos_x": -533,
                "pos_y": 72
            },
            "5": {
                "id": 5,
                "name": "Publish Event",
                "data": {
                    "node_uid": "93k77777dor0fmigm3axd0c",
                    "indexed_params": [],
                    "saved_filters": {
                        "selector": "",
                        "value": "",
                        "operator": "",
                        "path": ""
                    },
                    "module_type": "action",
                    "id": "publish-event",
                    "name": "Publish Event",
                    "multiple_output_connection": false,
                    "previous_module_version": "?",
                    "module_version": "0.1"
                },
                "class": "block-type-default",
                "typenode": false,
                "inputs": {
                    "input_1": {
                        "connections": [
                            {
                                "node": "1",
                                "input": "output_1"
                            }
                        ]
                    }
                },
                "outputs": {
                    "output_1": {
                        "connections": []
                    }
                },
                "pos_x": -41.69268749284265,
                "pos_y": 49.43030168580975
            }
        },
        "listening_triggers": [
            {
                "id": "event-after-save-new",
                "scope": "event",
                "name": "Event After Save New",
                "description": "This trigger is called after a new Event has been saved in the database",
                "icon": "envelope",
                "inputs": 0,
                "outputs": 1,
                "blocking": false,
                "misp_core_format": true,
                "trigger_overhead": 1,
                "trigger_overhead_message": "",
                "is_misp_module": false,
                "is_custom": false,
                "expect_misp_core_format": false,
                "version": "0.1",
                "icon_class": "",
                "multiple_output_connection": false,
                "support_filters": false,
                "saved_filters": [
                    {
                        "text": "selector",
                        "value": ""
                    },
                    {
                        "text": "value",
                        "value": ""
                    },
                    {
                        "text": "operator",
                        "value": ""
                    },
                    {
                        "text": "path",
                        "value": ""
                    }
                ],
                "params": [],
                "module_type": "trigger",
                "html_template": "trigger",
                "disabled": false
            }
        ]
    }
    }""")


def attribute_after_save_workflow() -> Dict[str, Any]:
    return loads("""{
    "Workflow": {
        "id": "1347617125",
        "uuid": "17fa92d1-7b40-444c-8629-a0686965d38b",
        "name": "Workflow for trigger attribute-after-save",
        "description": "",
        "timestamp": "1718632138",
        "enabled": false,
        "counter": "0",
        "trigger_id": "attribute-after-save",
        "debug_enabled": false,
        "data": {
            "1": {
                "class": "block-type-trigger",
                "data": {
                    "id": "attribute-after-save",
                    "scope": "attribute",
                    "name": "Attribute After Save",
                    "description": "This trigger is called after an Attribute has been saved in the database",
                    "icon": "cube",
                    "inputs": 0,
                    "outputs": 1,
                    "blocking": false,
                    "misp_core_format": true,
                    "trigger_overhead": 3,
                    "trigger_overhead_message": "This trigger is called each time an Attribute has been saved. [...]",
                    "is_misp_module": false,
                    "is_custom": false,
                    "expect_misp_core_format": false,
                    "version": "0.1",
                    "icon_class": "",
                    "multiple_output_connection": false,
                    "support_filters": false,
                    "saved_filters": [
                        {
                            "text": "selector",
                            "value": ""
                        },
                        {
                            "text": "value",
                            "value": ""
                        },
                        {
                            "text": "operator",
                            "value": ""
                        },
                        {
                            "text": "path",
                            "value": ""
                        }
                    ],
                    "params": [],
                    "module_type": "trigger",
                    "html_template": "trigger",
                    "disabled": false
                },
                "id": 1,
                "inputs": [],
                "outputs": {
                    "output_1": {
                        "connections": []
                    }
                },
                "pos_x": 0,
                "pos_y": 0,
                "typenode": false
            }
        },
        "listening_triggers": [
            {
                "id": "attribute-after-save",
                "scope": "attribute",
                "name": "Attribute After Save",
                "description": "This trigger is called after an Attribute has been saved in the database",
                "icon": "cube",
                "inputs": 0,
                "outputs": 1,
                "blocking": false,
                "misp_core_format": true,
                "trigger_overhead": 3,
                "trigger_overhead_message": "This trigger is called each time an Attribute has been saved. [...]",
                "is_misp_module": false,
                "is_custom": false,
                "expect_misp_core_format": false,
                "version": "0.1",
                "icon_class": "",
                "multiple_output_connection": false,
                "support_filters": false,
                "saved_filters": [
                    {
                        "text": "selector",
                        "value": ""
                    },
                    {
                        "text": "value",
                        "value": ""
                    },
                    {
                        "text": "operator",
                        "value": ""
                    },
                    {
                        "text": "path",
                        "value": ""
                    }
                ],
                "params": [],
                "module_type": "trigger",
                "html_template": "trigger",
                "disabled": false
            }
        ]
    }
}""")
