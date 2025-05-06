# Document Tool

> **Note**: The term Project Agent Builder refers to a BTP AI exploration project. All information on this page and about the project is confidential.

## Overview

The `document` tool type allows agents to consume and process entire documents. This capability enables agents to analyze, extract information from, and respond to questions about document content.

## Type

```
type: document
```

## Purpose

By enabling this tool, the agent can read and process whole documents that are passed as **base64 encoded** tool resources. The agent can then analyze the document content and provide insights, summaries, or answer questions about the document.

## Supported File Formats

The following resource formats are allowed:

| File format | Resource `contentType` |
|-------------|------------------------|
| docx        | application/docx       |
| pdf         | application/pdf        |
| markdown    | text/markdown          |
| txt         | text/plain             |
| xlsx        | application/xlsx       |
| csv         | text/csv               |

## Document Tool Limitations

- The maximum file size allowed is 10MB.
- Images within documents are ignored.

## Implementation Hints

1. **Resource Naming**: The name of the resource is also used. Ensure the name of the resource describes the content in a few words (≤ 5 words).

2. **Document Processing**: The document tool will hand over the full document to the agent. If the document is larger than the context size, it will be summarized. No vectorization will be performed.

3. **Encoding Requirement**: The document must be provided as base64 encoded.

## Use Cases

The Document Tool is useful for scenarios such as:

1. Extracting specific information from documents
2. Summarizing lengthy documents
3. Analyzing textual content (e.g., reports, articles, research papers)
4. Processing spreadsheet data
5. Answering questions about document content

## Integration with Other Tools

For best results, the Document Tool can be combined with other tools such as:
- Calculator Tool for numerical analysis of document data
- Code Execution Tool for processing extracted data 
- Human Tool for clarification on document contents 