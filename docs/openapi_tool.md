# OpenAPI Tool

> **Note**: The term Project Agent Builder refers to a BTP AI exploration project. All information on this page and about the project is confidential.

## Overview

The `openapi` tool type allows agents to make calls to APIs defined using OpenAPI specifications, giving them the ability to interact with a wide range of REST services.

## Type

```
type: openapi
```

## Purpose

This tool is useful for making calls to any API that has an OpenAPI specification. It enables agents to:
- Call REST APIs that follow the OpenAPI/Swagger specification
- Access public and private services 
- Perform CRUD operations through standardized REST endpoints

## Configuration

The JSON specification file must be set as a resource to the tool with `contentType: application/json`. YAML specifications are currently not supported. You can use the [swagger editor](https://editor.swagger.io/) to convert from YAML to JSON.

### Enhanced Descriptions

To provide further custom descriptions for the API and make it easier for the language model to find the correct endpoint, you can use the `llmDescription` property for both endpoints and endpoint parameters. This allows you to provide additional context that might not be available in the original JSON schema.

## Security Warning

**WARNING**: By default, the agent can execute any defined endpoint in the OpenAPI spec including POST, PATCH, PUT etc. Since the agent is not a deterministic system, there is a chance that these operations could be executed unintentionally.

Two approaches to mitigate this risk:

1. **Human Approval**: If you can propagate questions to a user, set the `humanApproval` config flag to deterministically always ask back via the Human Tool before a CUD (Create, Update, Delete) operation is performed. 
   - The Human Tool must be assigned to the agent
   - The human approval message can be formatted using the `humanApprovalMessageFormattingPrompt` property

2. **Restricted Access**: If you cannot implement human approval, you should either:
   - Restrict the user associated with the provided destination
   - Remove potentially harmful endpoints from the OpenAPI spec

## Limitations and Hints

- Only JSON request bodies are supported
- Headers must be provided manually (see destination configuration [here](https://sap.github.io/cloud-sdk/docs/js/features/connectivity/destinations#additional-headers-and-query-parameters-on-destinations))
- Use of destination service is recommended for setting headers and for accessing secure URLs
- When setting `humanApproval` to `true`, the Human Tool needs to be assigned to the agent as well
- Do **not** only rely on the Initial Instructions field to guide the agent about asking for confirmation when performing CUD operations
- The server must respond within 2 minutes

## Use Cases

- Integration with third-party REST APIs
- Accessing SAP and non-SAP services through standardized interfaces
- Building agents that can interact with multiple backend systems
- Performing complex operations through well-defined API endpoints 