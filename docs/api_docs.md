# Project Agent Builder - API Access Documentation

## Table of Contents
1. [Structure Overview](#structure-overview)
2. [Setup](#setup)
3. [Authentication](#authentication)
4. [Agents](#agents)
5. [Send Messages](#send-messages)
6. [Continue Messages](#continue-messages)
7. [Cancel Chat](#cancel-chat)
8. [API Usage Example](#api-usage-example)

## Structure Overview

The API is structured in a hierarchical fashion. Each agent consists of **multiple chats** and **multiple tools**.

A tool can make use of several resources which are usually files like PDF documents. In addition, a tool might need to be configured (i.e., restricting a tool to a specific website). This configuration is represented by several **configuration values**.

A chat consists of multiple messages from the *user*, the *ai*, or the *system* which build up a **chat history**. In addition, a resource can be limited to be consumable only from a specific chat.

A message from the chat history consists of several detailed steps (the **trace**) that the agent has performed to answer the message. The trace represents a graph. Where the nodes are either tools or agents and the edges the tool/agent input/output values.

In addition, the message can have **input values** that the agent requested i.e., when using the human tool.

## Setup

### 1. Setup Subaccount Entitlements

| Landscape | Service |
|-----------|---------|
| Canary EU12 | Unified Agent Runtime [Dev] |
| Live US10 | Project Agent Builder |

a. Go to the [BTP control center for canary](https://int.controlcenter.ondemand.com/index.html#/uc2/global_accounts) and assign the service `unified-agent-runtime-dev` to your global account.

b. Add quota for the plan `default` and save the settings

c. Add entitlement for service plan `standard` to your desired subaccount

### 2. Create Project Agent Builder Service Instance

a. Create a new service instance of service `Project Agent Builder` and plan `default` and hit create as there are no parameters.

or when using the cloud foundry CLI:

```
cf create-service unified-agent-runtime-dev default uar
```

b. Create a service key for the newly created service instance which will later be used for API authentication

or when using the cloud foundry CLI:

```
cf csk uar key
```

## Authentication

You can authenticate to the APIs of the *Project Agent Builder* using a [JSON Web Token](https://jwt.io/). To obtain such a token, you must send a request to the authorization server with your credentials that are disclosed in your service key previously created in the setup section.

All the necessary information such as the API endpoint and credentials to obtain a token are contained in the service key. With the *ClientID*, the *ClientSecret* and the usual OAuth flow `client_credentials` in the body as form parameters, a POST request must be sent to the authentication server *URL* with the path `/oauth/token`. A corresponding request is depicted below.

**cURL example:**
```
curl --location --request POST 'https://d067837-75vbj506.authentication.eu12.hana.ondemand.com/oauth/token' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'grant_type=client_credentials' \
--data-urlencode 'client_id=sb-a3f9e3b7-f1df-4a72-ad72-68c301eb138c!b160017|unified-ai-agent!b268611' \
--data-urlencode 'client_secret=8613da52-1227-445a-bd54-1518ba629910$T6g3lTvqmN76MPHN5Px5fkbhW7tiDVWDnylokm7r-ms='
```

In the response, you receive an `access_token` which can be used to send requests to the *Project Agent Builder* service by passing the token in the authorization header as per bearer scheme.

**cURL example:**
```
curl --location --request GET 'https://unified-ai-agent-srv-unified-agent.c-1228ddd.stage.kyma.ondemand.com/api/v1/Agents' \
--header 'Authorization: Bearer <access_token>'
```

### Hint
- The *ClientID* and the *ClientSecret* contain special characters like '|' or '!'. Be aware the values need to be url encoded.
- When executing the command from a terminal ensure you are using `'` character instead of `"`. Double quotes might lead to a replacement of values as "$a" is treated as an environment variable.

## Send Messages

The `POST /Agents(agentId)/chats(chatId)/UnifiedAiAgentService.sendMessage` route allows you to send a message to your agent.

**cURL example:**
```
curl --location --request POST 'https://unified-ai-agent-srv-unified-agent.c-1228ddd.stage.kyma.ondemand.com/api/v1/Agents(agentId)/chats(chatId)/UnifiedAiAgentService.sendMessage' \
--header 'Authorization: Bearer <access_token>' \
--header 'Content-Type: application/json' \
--data '{"msg": "What is the capital of the United States?","outputFormat": "Markdown","outputFormatOptions": "use bold for city name","async": false,"returnTrace": true}'
```

### Parameters

| Parameter | Description | Required | Type | Possible Values | Default | Constraints |
|-----------|-------------|----------|------|-----------------|---------|------------|
| msg | Your message to the agent. | Yes | string |  |  |  |
| outputFormat | The output format of the response. | No | enum (string) | JSON, Markdown, Text | Markdown |  |
| outputFormatOptions | Additional output format options which should be considered. In case of JSON this must be a JSON schema. For Text or Markdown this could be some desired formatting prosa text. | Yes, if format is JSON | string | If format is JSON the value must be a JSON-Schema object |  |  |
| async | Whether the message should be processed asynchronously. As the response can take a while it is recommended to set to true. | No | boolean |  | false |  |
| destination | You can specify a SAP BTP destination as a callback to send updates and final/intermediate response back. | No | string |  | false | See the tips section below to see which payload needs to be accepted by the callback endpoint. |
| returnTrace | Whether the agent task processing trace should be returned. | No | string |  | false |  |

### Hint
- The `sendMessage` endpoint will return an error if tools or resources are not in state `ready`. You are responsible to check both tool-states and resource-states before you start sending questions/tasks to the agent.
- Be aware that the flow can get interrupted by a tool i.e. when asking for permission via the human tool. When the flow gets interrupted it needs to be either canceled or resumed with the continueMessage endpoint

### Async Execution
It is recommended to set `async` to `true`, as the connection can be interrupted or closed, and you have to deal with long-lasting requests. Then a `historyId` property will be returned pointing to the chat message that got send.

You can then poll for the answer by filtering the messages where the `previous/ID` equals the `historyId`.

**cURL example:**
```
curl --location --request GET 'https://unified-ai-agent-srv-unified-agent.c-1228ddd.stage.kyma.ondemand.com/api/v1/Agents(agentId)/chats(chatId)/history?$filter=previous/ID eq historyId' \
--header 'Authorization: Bearer <access_token>'
```

In addition, you can query the `state` of the chat.

**cURL example:**
```
curl --location --request GET 'https://unified-ai-agent-srv-unified-agent.c-1228ddd.stage.kyma.ondemand.com/api/v1/Agents(agentId)/chats(chatId)' \
--header 'Authorization: Bearer <access_token>'
```

### Callback
In addition to setting `async` to `true`, an SAP BTP `destination` can be specified optionally, which points to a callback url that is called with intermediate updates (thoughts, tool use etc...) and when the agent has a response ready. The destination url will be taken as is, without attaching an additional url segment.

The messages are send up to 3x with a timeout of 3s. If your service does not respond, the agent builder will ignore that. Be aware that a slow answer will degrade the agent performance.

| Parameter | Description | Type | Possible Values |
|-----------|-------------|------|----------------|
| tenantId | Tenant ID | string |  |
| agentId | Agent ID that produced this update | string |  |
| chatId | Chat ID that produced this update | string |  |
| historyId | History ID that produced this update | string |  |
| groupId | History group were this update belongs to | string |  |
| type | Lets you differentiate between different message types i.e. an agent thought or the final answer | enum (string) | start, agent, tool, toolResource, abort, error, answerForUser, questionForUser, questionForTool |
| msg | Update message | string / undefined |  |
| agentMessage | Legacy update message used for answerForUser, questionForUser, questionForTool | string / undefined |  |
| responseHistoryId | Reference to the result chat message produced by BAF | string / undefined |  |

#### Types:

| Type | Properties used | Description |
|------|----------------|-------------|
| start | msg | The agent started working on the task |
| agent | msg | The thought of the agent |
| tool | msg | The agent called a tool |
| toolResource | msg | A tool has consumed a resource i.e., a PDF document |
| abort | msg | The chat got aborted by the user or a timeout occurred |
| error | msg | During runtime, an unexpected error happened (might be technical) |
| answerForUser | agentMessage; responseHistoryId | The final answer for the user |
| questionForUser | agentMessage; responseHistoryId | Agent got interrupted because it has a question for the user (via human tool) |
| questionForTool | agentMessage; responseHistoryId | Agent got interrupted because a tool got called asynchronously (continueMessage flow) |

### JSON Output
When setting the output format to `JSON` it is required to pass a json schema object in the `outputFormatOptions`. The schema `type` must be `object`. The properties of the object should have self-explanatory names and descriptions.

Make sure that your schema allows the agent to report an error, e.g. by specifying default values on your properties and providing i.e. a `successful` property.

**JSON Schema example:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "description": "Calculation result object",
  "type": "object",
  "properties": {
    "calculationResult": {
      "type": "number",
      "description": "The final result of the calculation"
    }
  },
  "required": [
    "calculationResult"
  ],
  "additionalProperties": false
}
```

### Hint:
When using json as an output format, do not force the agent to fill every property.

## Agents

### Retrieve a list of Agents

The `GET /Agents` route allows you to retrieve a list of AI agents.

**cURL example:**
```
curl --location --request GET 'https://unified-ai-agent-srv-unified-agent.c-1228ddd.stage.kyma.ondemand.com/api/v1/Agents' \
--header 'Authorization: Bearer <access_token>' \
```

The response of the API is an array of objects. Each object has the following fields:

| Parameter | Description | Type | Possible Values |
|-----------|-------------|------|----------------|
| ID | ID of the agent. | string |  |
| createdAt | The exact time the agent was created. | date |  |
| modifiedAt | The exact time the agent was last modified. | date |  |
| name | The name of the agent. | string |  |
| type | The underlying agent type. | enum (string) | smart |
| safetyCheck | Adds additional checks to detect insulting prompts. | boolean |  |
| expertIn | Define in which topic the agent is an expert. (System role) | string |  |
| initialInstructions | Messages that used as initial instructions to the agent for each chat. (System role) | string |  |
| iterations | Maximum number of agent iterations. | number |  |
| baseModel | The specified model will be used for performing basic tasks in the agents' execution flow. | enum (string) | OpenAiGpt4oMini, OpenAiGpt4o |
| advancedModel | The specified model will be used for performing advanced tasks in the agents' execution flow. | enum (string) | OpenAiGpt4oMini, OpenAiGpt4o |
| preprocessingEnabled | Shows if preprocessing steps Direct Instructions, Decomposition, Planning are enabled | boolean |  |
| postprocessingEnabled | Shows if postprocessing step Refinement is enabled. | boolean |  |
| orchestrationModuleConfig | Shows orchestration module configuration. | object | Orchestration Module Config |

### Create an Agent

The `POST /Agents` route allows you to create AI agents for your use cases based on a simple JSON configuration.

**cURL example:**
```
curl --location --request POST 'https://unified-ai-agent-srv-unified-agent.c-1228ddd.stage.kyma.ondemand.com/api/v1/Agents' \
--header 'Authorization: Bearer <access_token>' \
--header 'Content-Type: application/json' \
--data '{"name": "Web Search Expert","type": "smart","safetyCheck": true,"expertIn": "You are an expert in searching the web","initialInstructions": "## WebSearch Tool Hint\nTry to append 'Wikipedia' to your search query","iterations": 20,"baseModel": "OpenAiGpt4oMini","advancedModel": "OpenAiGpt4o"}'
```

| Parameter | Description | Required | Type | Possible Values | Default | Constraints |
|-----------|-------------|----------|------|-----------------|---------|------------|
| name | The name of the agent. | Yes | string |  |  | < 5000 Characters; Unique among all Agents |
| type | The underlying agent type. | No | enum (string) | smart | smart |  |
| safetyCheck | Adds additional checks to detect insulting prompts. | No | boolean |  | false |  |
| expertIn | Define in which topic the agent is an expert. (System role) | No | string |  |  | < 5000 Characters |
| initialInstructions | Messages that used as initial instructions to the agent for each chat. (System role) | No | string |  |  |  |
| iterations | Maximum number of agent iterations. | No | number |  | 20 | 1 - 100 |
| baseModel | The specified model will be used for performing basic tasks in the agents' execution flow. | No | enum (string) | OpenAiGpt4oMini, OpenAiGpt4o | OpenAiGpt4oMini |  |
| advancedModel | The specified model will be used for performing advanced tasks in the agents' execution flow. | No | enum (string) | OpenAiGpt4oMini, OpenAiGpt4o | OpenAiGpt4o |  |
| defaultOutputFormat | The output format of the response. | No | enum (string) | JSON, Markdown, Text | Markdown |  |
| defaultOutputFormatOptions | Additional output format options which should be considered. In case of JSON this must be a JSON schema. For Text or Markdown this could be some desired formatting prosa text. | Yes, if format is JSON | string | If format is JSON the value must be a JSON-Schema object |  |  |
| preprocessingEnabled | Enables the preprocessing steps Direct Instructions, Decomposition, Planning. | No | boolean |  | true |  |
| postprocessingEnabled | Enables the postprocessing steps Refinement. | No | boolean |  | true |  |
| orchestrationModuleConfig | Allows to activate and configure some orchestration modules. (data masking, etc) | No | object | Orchestration Module Config | null | must be a valid configuration object |

### Retrieve an Agent

The `GET /Agents(agentId)` route allows you to retrieve an AI agent.

**cURL example:**
```
curl --location --request GET 'https://unified-ai-agent-srv-unified-agent.c-1228ddd.stage.kyma.ondemand.com/api/v1/Agents(agentId)' \
--header 'Authorization: Bearer <access_token>' \
--header 'Accept: application/json' \
```

### Update an Agent

The `PATCH /Agents(agentId)` route allows you to update an AI agent configuration. You can update specific properties by specifying them in the request body.

**cURL example:**
```
curl --location --request PATCH 'https://unified-ai-agent-srv-unified-agent.c-1228ddd.stage.kyma.ondemand.com/api/v1/Agents(agentId)' \
--header 'Authorization: Bearer <access_token>' \
--header 'Content-Type: application/json' \
--data '{"expertIn": "You are an expert in searching the web"}'
```

### Delete an Agent

The `DELETE /Agents(agentId)` route allows you to delete an agent. The deletion process might take a while.

**cURL example:**
```
curl --location --request DELETE 'https://unified-ai-agent-srv-unified-agent.c-1228ddd.stage.kyma.ondemand.com/api/v1/Agents(agentId)' \
--header 'Authorization: Bearer <access_token>'
```

## Continue Messages

The `POST /Agents(agentId)/chats(chatId)/UnifiedAiAgentService.continueMessage` route allows the agent to continue on an interrupted flow by providing missing data.

The agent loop interruption comes from a tool invocation that expects a longer processing time like the human tool. You can identify an interruption by investigating the history type of the last message for `questionForUser` or `questionForTool`.

When calling the `continueMessage` endpoint, the agent loop gets restored and the given observation will we treated as the tool response.

In case of an asynchronous bring-your-own-tool the endpoint must be called by the microservice behind the bring-your-own tool.

**cURL example:**
```
curl --location --request POST 'https://unified-ai-agent-srv-unified-agent.c-1228ddd.stage.kyma.ondemand.com/api/v1/Agents(agentId)/chats(chatId)/UnifiedAiAgentService.continueMessage' \
--header 'Authorization: Bearer <access_token>' \
--header 'Content-Type: application/json' \
--data '{"observation": "The capital of the United States is washington","historyId": "intermediate response history id","async": true}'
```

| Parameter | Description | Required | Type | Possible Values | Default | Constraints |
|-----------|-------------|----------|------|-----------------|---------|------------|
| observation | Output of the tool. | Yes | string |  |  |  |
| historyId | Id of an unanswered and not canceled message of type `questionForUser` or `questionForTool` message | Yes | string |  |  |  |
| async | Whether the message should be processed asynchronously. As the response can take a while it is recommended to set to `true`. | No | boolean |  | false |  |
| destination | You can override the sendMessage SAP BTP destination as a callback to send the intermediate updates/response back. | No | string |  | false | See the tips section below to see which payload needs to be accepted by the callback endpoint. |
| returnTrace | Whether the agent task processing trace should be returned. | No | string |  | false |  |

## Cancel Chat

The `POST /Agents(agentId)/chats(chatId)/UnifiedAiAgentService.cancel` route allows you to cancel the agent loop and brings you back to `sendMessage`.

**cURL example:**
```
curl --location --request POST 'https://unified-ai-agent-srv-unified-agent.c-1228ddd.stage.kyma.ondemand.com/api/v1/Agents(agentId)/chats(chatId)/UnifiedAiAgentService.cancel' \
--header 'Authorization: Bearer <access_token>' \
--header 'Content-Type: application/json' \
--data '{}'
```

## API Usage Example

### Prerequisites

- Agent Builder instance created and service credentials available
- NodeJs installed

### Example

The following example demonstrates how to:

- Fetch an authorization token, ensure the token is not outdated and attaches it to every request
- Creates an Agent with the Document Tool and a text document attached
- Waits for the tool and the resources to become ready
- Starts chatting and waits for the agentic response

#### Helper Functions

```typescript
import axios, {AxiosInstance} from 'axios'
class TokenFetching {
  constructor(
    private readonly tokenServiceUrl: string,
    private readonly clientId: string,
    private readonly clientSecret: string,
  ) {}
  private lastToken?: {
    token: string
    expiresAt: number
  }
  private getCurrentTimeInSeconds() {
    return Math.floor(Date.now() / 1000)
  }
  public async getToken(): Promise<string> {
    // Ensure token is not outdated
    if (
      !this.lastToken ||
      this.lastToken.expiresAt * 0.9 < this.getCurrentTimeInSeconds()
    ) {
      this.lastToken = await this.getNewAuthToken(
        this.tokenServiceUrl,
        this.clientId,
        this.clientSecret,
      )
    }
    return this.lastToken?.token
  }
  private async getNewAuthToken(
    tokenServiceUrl: string,
    clientId: string,
    clientSecret: string,
  ): Promise<{
    token: string
    expiresAt: number
  }> {
    const formData = {
      client_id: clientId,
      client_secret: clientSecret,
      grant_type: 'client_credentials',
    }
    // Fetch token from uaa
    const xsuaaResponseObj = await axios.post<{
      access_token: string
      expires_in: number
    }>(
      tokenServiceUrl,
      new URLSearchParams(formData),
      {
        headers: {
          'content-type': 'application/x-www-form-urlencoded',
          'accept': 'application/json',
        },
      })
    return {
      token: xsuaaResponseObj.data.access_token,
      expiresAt: this.getCurrentTimeInSeconds() + xsuaaResponseObj.data.expires_in,
    }
  }
}
export class AgentClient {
  constructor(
    private readonly tokenFetcher: TokenFetching,
    private readonly baseUrl: string,
  ) {}
  public createClient(): AxiosInstance {
    const instance = axios.create({
      baseURL: this.baseUrl,
      timeout: 1000 * 60 * 5,
    })
    // Add authorization header with token to each request
    instance.interceptors.request.use(
      async config => {
        const token = await this.tokenFetcher.getToken()
        config.headers.setAuthorization('Bearer ' + token)
        return config
      })
    return instance
  }
}
async function sleep(ms: number) {
  return await new Promise(resolve => setTimeout(resolve, ms))
}
```

#### Agents

```typescript
void (async () => {
  const credentials = {
    clientId: 'sb-554b3203-364f-4534-b089-816b98eea269!b312843|unified-ai-agent!b268611',
    clientSecret: 'cc21e9ec9-f8ea-4ac6-8d54-9636a255e374$2jrBzY1d-cfof3ljwl8NQOl3h9PsGs7QjuIByGKVJxo=',
    tokenUrl: 'https://unified-ai-agent-consumer-1-n1894ser.authentication.eu12.hana.ondemand.com/oauth/token', // /oauth/token
    apiUrl: 'https://unified-ai-agent-srv-unified-agent.c-1228ddd.stage.kyma.ondemand.com',
  }
  const tokenFetcher = new TokenFetching(
    credentials.tokenUrl,
    credentials.clientId,
    credentials.clientSecret,
  )
  const agentClient = new AgentClient(tokenFetcher, credentials.apiUrl)
  const client = agentClient.createClient()
  // Create Agent
  const createAgentResponse = await client.post<{
    ID: string
  }>('/api/v1/Agents', {
    name: 'Document Reader Agent',
  })
  // Add document tool to agent
  const createToolResponse = await client.post<{
    ID: string
  }>(`/api/v1/Agents(${createAgentResponse.data.ID})/tools`, {
    name: 'Doc Tool',
    type: 'document',
  })
  // Add a document to the document tool
  const addToolResource = await client.post<{
    ID: string
  }>(`/api/v1/Agents(${createAgentResponse.data.ID})/tools(${createToolResponse.data.ID})/resources`, {
    name: 'Price list',
    contentType: 'text/plain',
    data: Buffer.from('1. Apple: $1\n2. Banana: $2\n3. Cherry: $3\n').toString('base64'),
  })
  // Wait for resource to be ready
  let documentReady = false
  while (!documentReady) {
    await sleep(3000)
    const resource = await client.get<{
      state: string;
      lastError?: string
    }>(`/api/v1/Agents(${createAgentResponse.data.ID})/tools(${createToolResponse.data.ID})/resources(${addToolResource.data.ID})`)
    if (resource.data.state === 'error')
      throw new Error('Resource failed to load: ' + resource.data.lastError)
    documentReady = resource.data.state === 'ready'
  }
  // Wait for tool to be ready
  let toolReady = false
  while (!toolReady) {
    await sleep(3000)
    const tool = await client.get<{
      state: string;
      lastError?: string
    }>(`/api/v1/Agents(${createAgentResponse.data.ID})/tools(${createToolResponse.data.ID})`)
    if (tool.data.state === 'error')
      throw new Error('Tool failed to load: ' + tool.data.lastError)
    toolReady = tool.data.state === 'ready'
  }
  // Create chat
  const createChatResponse = await client.post<{
    ID: string
  }>(`/api/v1/Agents(${createAgentResponse.data.ID})/chats`, {
    name: 'Chat 1',
  })
  // Start chat
  const startChatResponse = await client.post<{
    historyId: string
  }>(`/api/v1/Agents(${createAgentResponse.data.ID})/chats(${createChatResponse.data.ID})/UnifiedAiAgentService.sendMessage`, {
    msg: 'What is the price of a banana?',
    async: true,
  })
  // Wait for the response
  let agentAnswer: string
  while (true) {
    const answers = await client.get<{
      value: Array<{
        content: string
      }>
    }>(`/api/v1/Agents(${createAgentResponse.data.ID})/chats(${createChatResponse.data.ID})/history?$filter=previous/ID eq ${startChatResponse.data.historyId}`)
    // No answer there yet
    if (answers.data.value.length === 0) {
      // Check if the chat is not in error state
      const chat = await client.get<{
        state: string
      }>(`/api/v1/Agents(${createAgentResponse.data.ID})/chats(${createChatResponse.data.ID})?$select=state`)
      if (chat.data.state === 'failed') {
        throw new Error('Chat failed')
      }
      await sleep(5000)
      continue
    }
    agentAnswer = answers.data.value[0].content
    break
  }
  console.log('Response:', agentAnswer)
})()
```