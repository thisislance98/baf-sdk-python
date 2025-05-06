# Project Agent Builder Tools Overview

> **Note**: The term Project Agent Builder refers to a BTP AI exploration project. All information on this page and about the project is confidential.

## What are Agent Tools?

An Agent Tool, sometimes referred to as an 'action' in the realm of Artificial Intelligence (AI), denotes a specific function or activity carried out by an AI agent in response to inputs from its environment. This could range from producing a particular response in a chatbot conversation, making recommendations, or interacting with other systems. Generally, the chosen tool or action aims to maximize the achievement of predefined AI goals, such as problem-solving or user experience optimization.

To gain a programmatic understanding of how agent, tool, and resource initialization is done, refer to `tests/integration/api.test.ts`.

## Available Tools

The following tools are available:

| Tool | Summary | Type | Instances per agent |
|------|---------|------|---------------------|
| Bring You Own | Connect your own tool via REST | `bringyourown` | 10 |
| Document | Let the agent read a whole document like a PDF. No images supported. | `document` | 1 |
| Calculator | Agents are bad at math, so use this tool if math is involved | `calculator` | 1 |
| Websearch | Let the agent perform a Google search to answer a query | `websearch` | 1 |
| OpenAPI | Call REST endpoints | `openapi` | 4 |
| Hana | Let the agent perform SQL queries for HANA | `hana` | 4 |
| Human | Let the agent ask you back if information is missing | `human` | 1 |
| OData | Call OData endpoints | `odata` | 4 |
| Code Execution | Execute simple JavaScript code | `code` | 1 |

## Tool Configuration

Some tools may need a `config`, and some require `resources`. Generally, a `config` is a set of value pairs used to set up a tool, like a URL or a name. The `resources` are required for providing complex inputs to tools, such as PDFs, Open-API files, etc. **Note that a resource must always be encoded as a base64 string**.

**Note:** The tool name, which should be a short, precise description of its specific function, must be unique amongst all existing tools an agent possesses. 