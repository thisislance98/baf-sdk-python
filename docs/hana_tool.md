# Hana Tool

> **Note**: The term Project Agent Builder refers to a BTP AI exploration project. All information on this page and about the project is confidential.

## Overview

The `hana` tool type allows agents to interact with SAP HANA databases, enabling SQL queries and operations against HANA data sources.

## Type

```
type: hana
```

## Purpose

This tool is useful when the agent needs to interact with your HANA database. It allows the agent to:
- Query data from tables and views
- Execute SQL statements
- Analyze database schemas
- Perform data operations

## Requirements

- The database user must have permission to query the `sys.TABLE_COLUMNS` and `sys.VIEW_COLUMNS` tables
- HANA credentials must be passed as a tool config
- The HANA credentials are stored in SAP credential store service

## Security Warning

**WARNING**: By default, the agent can execute arbitrary statements including potentially destructive operations like DELETE, DROP TABLE, etc. Since the agent is not a deterministic system, there is a chance that these operations could be executed unintentionally.

Two approaches to mitigate this risk:

1. **Human Approval**: If you can propagate questions to a user, set the `humanApproval` config flag to deterministically always ask back via the Human Tool before a CUD (Create, Update, Delete) operation is performed. 
   - The Human Tool must be assigned to the agent
   - The human approval message can be formatted using the `humanApprovalMessageFormattingPrompt` property

2. **Restricted User**: If you cannot implement human approval, restrict the HANA user to only have the permissions required for the intended operations.

## Schema Semantics

You can pass table/column relation semantics by adding an `application/json` resource to help the agent understand the database structure.

## Limitations and Hints

- It is **highly recommended** to add schema semantics to help the agent make use of data relations
- When setting `humanApproval` to `true`, the Human Tool needs to be assigned to the agent as well
- Do **not** only rely on the Initial Instructions field to guide the agent about asking for confirmation when performing CUD operations
- If `sys.TABLE_COLUMNS` and `sys.VIEW_COLUMNS` have more than 1000 rows (transposed columns), performance will decrease as the rows passed to the language model will be cut off
- If your database has more than 250 tables/views, it will be truncated to 250 tables/views - in this case, provide specific instructions about which tables should be considered

## Use Cases

- Querying business data from HANA databases
- Analyzing database structures and relationships
- Generating reports based on database content
- Performing data validation or transformation operations
- Integrating SAP HANA data with agent capabilities 