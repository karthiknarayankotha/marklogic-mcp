# MarkLogic MCP Server

This project implements a Model Context Protocol (MCP) server for MarkLogic, providing CRUD operations and querying capabilities for documents.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure MarkLogic connection:
Edit the following variables in `marklogic_mcp_server.ts`:
```typescript
const ML_CONFIG = {
    host: "localhost",  // Your MarkLogic host
    port: 8000,         // Your MarkLogic port
    user: "admin",      // Your MarkLogic username
    password: "admin",  // Your MarkLogic password
    authType: 'DIGEST' as const
} as const;
```

3. Compile TypeScript:
```bash
npx tsc
```

4. Run the server:
```bash
node dist/marklogic_mcp_server.js
```

## Features

### 1. Read Documents
Read documents from MarkLogic by URI:
```typescript
// Using MCP client
mcpClient.readDocument({ uri: "/path/to/document.json" });
```

### 2. Create Documents
Create new documents in MarkLogic with optional collections and permissions:
```typescript
// Using MCP client
mcpClient.createDocument({
  uri: "/path/to/document.json",
  content: { title: "Example", content: "Hello World" },
  collections: ["my-collection"],
  permissions: [
    { role: "rest-reader", capabilities: ["read"] },
    { role: "rest-writer", capabilities: ["update"] }
  ]
});
```

### 3. Update Documents
Update existing documents, with optional merge capability:
```typescript
// Using MCP client
mcpClient.updateDocument({
  uri: "/path/to/document.json",
  content: { updatedField: "New Value" },
  merge: true,  // Merges with existing content instead of replacing
  collections: ["my-collection", "updated-docs"]
});
```

### 4. Delete Documents
Delete documents by URI:
```typescript
// Using MCP client
mcpClient.deleteDocument({ uri: "/path/to/document.json" });
```

### 5. Query Documents
Query documents using MarkLogic's cts.query with pagination:
```typescript
// Using MCP client
mcpClient.queryDocuments({
  query: 'cts.andQuery([cts.collectionQuery("my-collection")])',
  limit: 10,
  offset: 0
});
```

## Project Structure

- `marklogic_mcp_server.ts` - Main server implementation with MCP tools
- `dist/` - Compiled JavaScript files
- `types/` - TypeScript type definitions
- `tsconfig.json` - TypeScript configuration

## Using as a Library

You can import this code as a library in your TypeScript/JavaScript projects:

```typescript
import { createClient } from './path/to/mcp-client';

const mcpClient = createClient({
  host: "localhost",
  port: 8000,
  user: "your-username",
  password: "your-password"
});

// Now use the client to interact with MarkLogic
mcpClient.readDocument({ uri: "/some/document.json" })
  .then(result => console.log(result))
  .catch(error => console.error(error));
``` 