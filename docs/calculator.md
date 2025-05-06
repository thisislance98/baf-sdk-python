# Calculator Tool

> **Note**: The term Project Agent Builder refers to a BTP AI exploration project. All information on this page and about the project is confidential.

## Overview

The `calculator` tool type allows agents to perform mathematical calculations. This is a built-in tool that doesn't require any special configuration.

## Type

```
type: calculator
```

## Purpose

By enabling this tool, the agent can perform mathematical calculations that would otherwise be difficult for the language model to handle accurately.

## Hint

- Always prefer a calculator over asking the language model (LLM) directly, as tokenization makes it hard for the LLM to calculate correctly.

## Use Cases

The calculator tool is particularly useful for scenarios involving:
- Complex mathematical operations
- Financial calculations
- Statistical analysis
- Any numerical computation where precision is required

## Limitations

The calculator tool is limited to standard mathematical operations and may not handle specialized scientific or engineering calculations that require specific libraries or functions. 