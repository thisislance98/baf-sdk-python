# Joule Function Tool

> **Note**: The term Project Agent Builder refers to a BTP AI exploration project. All information on this page and about the project is confidential.

## Overview

The `joulefunction` tool type allows agents to call deployed Joule functions as tools. This integration enables agents to leverage existing enterprise functionality deployed through SAP Joule.

## Type

```
type: joulefunction
```

## Status - Work in Progress

**Disclaimer**: This tool is **work in progress**. The feature flag will only be **activated** for **Joule** and selected **AI Frontrunner subaccounts**.

## Prerequisites

- Your subaccount must be subscribed to Joule
- Your **tenant** needs to be **onboarded to the tool** as it is currently hidden behind a **feature flag**

## Configuration

You need to provide additional tool configuration so that Joule can locate the function. This includes:

1. Tool configuration parameters that allow Joule to locate and call the function
2. A JSON Schema object as a tool resource that describes the input parameters of the Joule function

### Human Approval

If you want to confirm certain Joule function calls in a deterministic way, you can optionally configure the `humanApproval` property which always enforces a human approval. Make sure to have the Human Tool assigned in this case. 

The human approval message can be formatted using the `humanApprovalMessageFormattingPrompt` property.

### JSON Schema for Parameters

You must provide a [JSON Schema](https://json-schema.org/) object as a tool resource that describes the input parameters of the Joule function. Here's an example:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "itemName": {
      "type": "string",
      "description": "Name of the item that should be added to the shopping list"
    },
    "quantity": {
      "type": "number",
      "default": 1,
      "description": "Quantity of the item"
    }
  },
  "required": [
    "itemName"
  ],
  "additionalProperties": false
}
```

All required properties have a direct effect on the agent behavior and must be semantically meaningful. It is essential to provide meaningful property descriptions in the JSON Schema, otherwise, the agent might reason not to use the tool as it appears to be of no use.

## Limitations and Hints

- As Joule function executions take time, it is recommended to configure the agent to run asynchronously for tasks including Joule functions
- The server must respond within 2 minutes
- The tool is currently in work in progress state and access is limited

## Use Cases

- Integrating enterprise functionality from Joule into agent workflows
- Accessing backend systems and services via Joule functions
- Performing complex business operations that are implemented in Joule
- Extending agent capabilities with custom business logic 