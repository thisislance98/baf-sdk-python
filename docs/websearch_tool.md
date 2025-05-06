# Websearch Tool

> **Note**: The term Project Agent Builder refers to a BTP AI exploration project. All information on this page and about the project is confidential.

## Overview

The `websearch` tool type allows agents to search the internet, enabling them to access up-to-date information and data from websites.

## Type

```
type: websearch
```

## Purpose

This tool is useful for enabling agents to:
- Search for information on the internet
- Access current data and resources from websites
- Query specific websites when a domain constraint is provided

## Configuration

The tool can be configured to limit searches to specific domains:

```json
"config": [
    {
        "name": "site", // Optional, design time. Restrict the sites that the search engine should consider
        "value": "wikipedia.org, sap.com"
    }
]
```

## Functionality

The tool utilizes Bing search engine to query for search results. When a domain constraint is provided in the configuration, search results will be limited to the specified websites.

## Limitations and Hints

- The tool uses a headless browser to search the web, which means JavaScript-based websites are supported
- The agent cannot interact with websites (e.g., cannot click on elements)
- Website content consumption may vary:
  - The agent might consume information that is not directly visible to humans
  - The agent might consume less information if a website is not fully loaded
- Websites are formatted differently, which may affect how the agent interprets the content

## Use Cases

- Retrieving current information on specific topics
- Gathering data from trusted websites specified in the domain constraints
- Accessing latest documentation, articles, or news
- Augmenting agent knowledge with real-time web information 