# Human Tool

> **Note**: The term Project Agent Builder refers to a BTP AI exploration project. All information on this page and about the project is confidential.

## Overview

The `human` tool type allows agents to request additional information from human users when needed. It facilitates a structured way for humans to provide input and approve agent actions, enhancing the collaboration between AI agents and human users.

## Type

```
type: human
```

## Purpose

This tool is useful when it's expected that a human needs to provide additional information during agent execution. When used, the Human Tool:

- Terminates the agent loop
- Returns the question back to the user
- Generates input fields that offer a structured way to parse the required information

## Implementation

You can identify a question to human in the response or in the history message type. The tool can interact with other tools through the `humanApproval` configuration.

When the `humanApproval` config value is set on a supported tool, a human approval will be required before a system change (create, update, delete) is performed. This creates a safety mechanism for critical operations.

## Integration with Other Tools

The Human Tool can be integrated with other tools that support the `humanApproval` parameter:

- [Hana](hana_tool.md) - For database operations
- [OData](odata_tool.md) - For OData service calls
- [OpenAPI](openapi_tool.md) - For REST API calls

When these tools are configured with `humanApproval: true`, they will require human confirmation before making system changes.

## Limitations and Hints

- Human in the loop is **highly recommended** for business-critical decisions and decisions based on critical data.
- Use the Human Tool with appropriate initial instructions to instruct the agent to request user feedback before certain critical decisions are made.
- Be aware that the human tool will interrupt the agent loop. The answer from the human tool must be provided via the `continueMessage` endpoint instead of `sendMessage`.

## Use Cases

1. **Data Validation**: Have humans verify data before it's committed to a system
2. **Decision Approval**: Get approval for important business decisions
3. **Information Gathering**: Collect additional information that the agent cannot determine on its own
4. **Error Correction**: Have humans intervene when the agent encounters unexpected situations
5. **Security Control**: Ensure sensitive operations require human approval

## API Integration

When implementing a client application that uses an agent with the Human Tool:

1. When the agent requires human input, the agent loop terminates
2. The application should present the question and input fields to the user
3. After receiving user input, the application should use the `continueMessage` endpoint (not `sendMessage`) to resume the agent loop with the user's response 