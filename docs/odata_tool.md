# OData Tool

> **Note**: The term Project Agent Builder refers to a BTP AI exploration project. All information on this page and about the project is confidential.

## Overview

The `odata` tool type allows agents to interact with OData services, enabling integration with SAP and other systems that expose OData endpoints.

## Type

```
type: odata
```

## Purpose

This tool is useful for calling your OData services. It enables agents to:
- Query data from OData services
- Create, update, or delete data through OData endpoints
- Interact with SAP S/4HANA and other OData-enabled systems

## Configuration

Use SAP Destination service to configure your access to the OData service. The destination can then be provided in the tool configuration of the OData tool.

### Metadata Handling

You can add the edmx metadata document base64 encoded with content type `application/xml` as a resource to the tool. If no metadata resource is provided, the xml metadata document will be fetched from `/$metadata`.

## Security Warning

**WARNING**: By default, the agent can execute arbitrary endpoints including POST, PATCH, PUT etc. Since the agent is not a deterministic system, there is a chance that these operations could be executed unintentionally.

Two approaches to mitigate this risk:

1. **Human Approval**: If you can propagate questions to a user, set the `humanApproval` config flag to deterministically always ask back via the Human Tool before a CUD (Create, Update, Delete) operation is performed. 
   - The Human Tool must be assigned to the agent
   - The human approval message can be formatted using the `humanApprovalMessageFormattingPrompt` property

2. **Restricted User**: If you cannot implement human approval, restrict the user associated with the provided destination credentials to only have the necessary permissions.

## Connecting to S/4HANA OData Services

To connect to an OData service from S/4HANA:

1. Ensure that a communication arrangement exists to enable communication between S/4HANA and BTP
2. Set up a communication scenario by following [this guide](https://help.sap.com/docs/SAP_S4HANA_CLOUD/4fc8d03390c342da8a60f8ee387bca1a/4efaa144b2864db3b49db54242581620.html)
3. Use the BTP destination service to save your S/4 OData credentials and the path to your OData service

## Limitations and Hints

- When setting `humanApproval` to `true`, the Human Tool needs to be assigned to the agent as well
- Do **not** only rely on the Initial Instructions field to guide the agent about asking for confirmation when performing CUD operations
- When there is no XML resource attached to the tool, the OData XML metadata will be fetched from `/$metadata`
- The server must respond within 2 minutes

## Use Cases

- Querying business data from SAP S/4HANA systems
- Creating, updating, or deleting records in OData-enabled systems
- Integrating with SAP and non-SAP OData services
- Building agents that can interact with enterprise systems 