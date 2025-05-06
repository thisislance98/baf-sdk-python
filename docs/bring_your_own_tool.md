# Bring Your Own Tool

> **Note**: The term Project Agent Builder refers to a BTP AI exploration project. All information on this page and about the project is confidential.

## Overview

The `bringyourown` tool type allows you to extend the agent runtime with your own custom tools by providing a REST service that follows the BringYourOwnTool interface. This gives you flexibility to create specialized tools beyond the standard set of tools provided by the Project Agent Builder.

## Implementation Requirements

At minimum, you must implement two mandatory endpoints:
- `/metadata` - Provides the agent with information about your tool
- `/callback` - Handles execution requests when the agent decides to use your tool

## Namespacing

The namespace is optional and makes it possible to expose multiple tools under the same service/destination. The agent runtime will call the tool's endpoints with the namespace as a prefix.

## Human Approval

If you want to confirm certain BringYourOwnTool executions in a deterministic way, you can optionally configure the `humanApproval` property which always enforces a human approval. Make sure to have the Human Tool assigned in this case. The human approval message can be formatted using the `humanApprovalMessageFormattingPrompt` property.

## HTTP Callbacks

### Metadata (Mandatory)

This endpoint provides the agent with the necessary information about the tool. All required properties have a direct effect on the agent behavior and must be semantically meaningful.

The `schema` property inside the response must be a stringified JSON Schema of an **object**. Example schema:

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

The simpler the schema, the easier it is for the agent to call the tool. The endpoint will be called by the agent runtime as soon as the scheduler starts working on the task.

Required response properties:
- `name`
- `description`
- `schema`

The `async` property defaults to `false` if not specified.

### Callback (Mandatory)

The callback endpoint will be called by the agent runtime when the agent decides to execute the tool.

The `toolInput` property inside the HTTP request is a JSON stringified object guaranteed to match the `schema` from the `/metadata` endpoint.

The `response` string property of the HTTP response has a direct effect on the agent behavior and must be semantically meaningful. The returned text should be markdown. Remove as much noise as possible - short and crisp responses are highly recommended. Do not return large amounts of text like giant JSON payloads as this will flood the context and lead to errors.

The callback must return within 2 minutes, otherwise it will be treated as an error.

If the data provided by the agent contains unexpected values, use the `response` parameter to provide a meaningful error message that guides the agent in the right direction. The status code should still be 200, otherwise the agent will get the erroneous HTTP status code back, which might lead to confusion.

#### Asynchronous Callbacks

When using `async`, the agent loop will be interrupted and the `response` parameter value will be treated as a temporary message for the user. You are responsible for sending an answer using the `continueMessage` endpoint to continue the agent loop. The required `historyId` parameter matches the `callbackHistoryId` from the BYOT callback endpoint.

### Config Changed (Optional)

If you want to be notified about changes in the tool configuration, you can implement the configuration change endpoint to receive updates.

To report an error back, you can set the error code (must not be 404 and > 300) and provide an error reason by returning an `error` property.

### Tool Resources Changed (Optional)

In case you want to be notified about changes in the tool resources, you can implement this resource change endpoint.

To report an error back, you can set the error code (must not be 404 and > 300) and provide an error reason by returning an `error` property.

## Hints

- You can use the given IDs (tenant, agent, chat, tool) to create and retrieve a session
- Use the given IDs to request needed resources/configs etc. via the agent runtime OData API
- Use short and precise input to the agent
- Be aware that the async BYO tool will interrupt the agent loop. The answer from the tool must be provided via the `continueMessage` endpoint instead of `sendMessage`
- The server must respond within 2 minutes

## Examples

For implementation examples, refer to:
- [Minimal TypeScript CAP Example](https://github.com/SAP-samples/project-agent-builder-samples/tree/main/minimal-bring-your-own-tool-typescript)
- [Minimal Python Example](https://github.com/SAP-samples/project-agent-builder-samples/tree/main/minimal-bring-your-own-tool-python) 