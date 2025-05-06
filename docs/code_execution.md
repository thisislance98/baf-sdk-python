# Code Execution Tool

> **Note**: The term Project Agent Builder refers to a BTP AI exploration project. All information on this page and about the project is confidential.

## Overview

The `code` tool type allows agents to execute JavaScript code in a highly restricted sandbox environment. This tool is particularly useful if the agent needs to decode something or requires a dynamic calculation.

## Type

```
type: code
```

## Purpose

By enabling this tool, the agent can execute JavaScript code to perform operations such as:
- Decoding encoded data
- Performing dynamic calculations
- Manipulating strings
- Processing data structures
- Other programmatic tasks that can be solved with JavaScript

## Limitations and Hints

The code execution environment has several important limitations to be aware of:

- **Plain JavaScript Only**: The code must be written in plain JavaScript
- **Memory Constraints**: The code can allocate only a few MB of memory
- **Time Limit**: The running time must be less than 1 minute
- **Synchronous Execution**: The code must be synchronous (no async/await or Promises)
- **No Node.js APIs**: No access to Node.js APIs like file system or internet access
- **Limited Libraries**: Only selected libraries can be used:
  - Lodash
  - buffer.js
  - base64.js

## Use Cases

The code execution tool is useful for scenarios where the agent needs to:
1. Decode base64 strings
2. Parse and transform data
3. Perform complex calculations
4. Manipulate strings and text
5. Work with JSON data
6. Convert between data formats

## Security Considerations

The tool runs in a highly restricted JavaScript sandbox to ensure security. This means that the code cannot:
- Access the file system
- Make network requests
- Access environment variables
- Use potentially dangerous JavaScript features 