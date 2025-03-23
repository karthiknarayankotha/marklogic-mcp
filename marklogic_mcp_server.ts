import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import * as marklogicModule from "marklogic";
import { z } from "zod";

// Use type assertion for marklogic module
const marklogic = marklogicModule as any;

const server = new McpServer({
    name: "MarkLogic Explorer",
    version: "1.0.0"
});

// MarkLogic connection configuration
const ML_CONFIG = {
    host: "localhost",
    port: 8000,
    user: "admin",
    password: "admin",
    authType: 'DIGEST' as const
} as const;

// Helper to create MarkLogic client
const getClient = () => {
    return marklogic.createDatabaseClient(ML_CONFIG);
};

// Tool to read documents
server.tool(
    "readDocument",
    { uri: z.string() },
    async ({ uri }) => {
        const client = getClient();
        try {
            // Using eval with result() to get the actual result
            const result = await client.eval(`
                const doc = cts.doc("${uri}");
                if (doc) {
                    xdmp.toJSON({
                        exists: true,
                        content: doc.toObject(),
                        uri: "${uri}"
                    });
                } else {
                    xdmp.toJSON({
                        exists: false,
                        uri: "${uri}"
                    });
                }
            `).result();
            
            // Check if the document exists in the result
            if (result && result.length > 0 && result[0].value.exists) {
                return {
                    content: [{
                        type: "text",
                        text: JSON.stringify(result[0].value.content, null, 2)
                    }]
                };
            } else {
                return {
                    content: [{
                        type: "text",
                        text: `Document not found: ${uri}`
                    }],
                    isError: true
                };
            }
        } catch (err: unknown) {
            const error = err as Error;
            return {
                content: [{
                    type: "text",
                    text: `Error reading document: ${error.message}`
                }],
                isError: true
            };
        }
    }
);

// Tool to create documents
server.tool(
    "createDocument",
    {
        uri: z.string(),
        content: z.record(z.any()),
        collections: z.array(z.string()).optional(),
        permissions: z.array(z.object({
            role: z.string(),
            capabilities: z.array(z.string())
        })).optional()
    },
    async ({ uri, content, collections, permissions }) => {
        const client = getClient();
        try {
            // First check if document already exists
            const checkResult = await client.eval(`
                cts.doc("${uri}") != null
            `).result();
            
            if (checkResult && checkResult[0] && checkResult[0].value === true) {
                return {
                    content: [{
                        type: "text",
                        text: `Document already exists at URI: ${uri}`
                    }],
                    isError: true
                };
            }
            
            // Prepare write options
            const writeOptions: any = {
                uri: uri,
                content: content,
                contentType: 'application/json'
            };
            
            // Add collections if provided
            if (collections && collections.length > 0) {
                writeOptions.collections = collections;
            }
            
            // Add permissions if provided
            if (permissions && permissions.length > 0) {
                writeOptions.permissions = permissions;
            }
            
            // Create document
            const result = await client.documents.write(writeOptions).result();
            
            return {
                content: [{
                    type: "text",
                    text: `Document created successfully at URI: ${uri}`
                }]
            };
        } catch (err: unknown) {
            const error = err as Error;
            return {
                content: [{
                    type: "text",
                    text: `Error creating document: ${error.message}`
                }],
                isError: true
            };
        }
    }
);

// Tool to update documents
server.tool(
    "updateDocument",
    {
        uri: z.string(),
        content: z.record(z.any()),
        merge: z.boolean().optional(),
        collections: z.array(z.string()).optional(),
        permissions: z.array(z.object({
            role: z.string(),
            capabilities: z.array(z.string())
        })).optional()
    },
    async ({ uri, content, merge = false, collections, permissions }) => {
        const client = getClient();
        try {
            // First check if document exists
            const checkResult = await client.eval(`
                cts.doc("${uri}") != null
            `).result();
            
            if (!checkResult || !checkResult[0] || checkResult[0].value !== true) {
                return {
                    content: [{
                        type: "text",
                        text: `Document not found at URI: ${uri}`
                    }],
                    isError: true
                };
            }
            
            if (merge) {
                // If merge is true, get existing content and merge with new content
                const existingContent = await client.eval(`
                    const doc = cts.doc("${uri}");
                    if (doc) {
                        xdmp.toJSON(doc.toObject());
                    } else {
                        xdmp.toJSON({});
                    }
                `).result();
                
                if (existingContent && existingContent.length > 0) {
                    const existingObj = existingContent[0].value;
                    content = { ...existingObj, ...content };
                }
            }
            
            // Prepare write options
            const writeOptions: any = {
                uri: uri,
                content: content,
                contentType: 'application/json'
            };
            
            // Add collections if provided
            if (collections && collections.length > 0) {
                writeOptions.collections = collections;
            }
            
            // Add permissions if provided
            if (permissions && permissions.length > 0) {
                writeOptions.permissions = permissions;
            }
            
            // Update document
            const result = await client.documents.write(writeOptions).result();
            
            return {
                content: [{
                    type: "text",
                    text: `Document updated successfully at URI: ${uri}`
                }]
            };
        } catch (err: unknown) {
            const error = err as Error;
            return {
                content: [{
                    type: "text",
                    text: `Error updating document: ${error.message}`
                }],
                isError: true
            };
        }
    }
);

// Tool to delete documents
server.tool(
    "deleteDocument",
    { uri: z.string() },
    async ({ uri }) => {
        const client = getClient();
        try {
            // First check if document exists
            const checkResult = await client.eval(`
                cts.doc("${uri}") != null
            `).result();
            
            if (!checkResult || !checkResult[0] || checkResult[0].value !== true) {
                return {
                    content: [{
                        type: "text",
                        text: `Document not found at URI: ${uri}`
                    }],
                    isError: true
                };
            }
            
            // Delete document
            const result = await client.documents.remove(uri).result();
            
            return {
                content: [{
                    type: "text",
                    text: `Document deleted successfully: ${uri}`
                }]
            };
        } catch (err: unknown) {
            const error = err as Error;
            return {
                content: [{
                    type: "text",
                    text: `Error deleting document: ${error.message}`
                }],
                isError: true
            };
        }
    }
);

// Tool to query documents
server.tool(
    "queryDocuments",
    { 
        query: z.string(),
        limit: z.number().optional().default(10),
        offset: z.number().optional().default(0)
    },
    async ({ query, limit, offset }) => {
        const client = getClient();
        try {
            // Using eval with result() to get the query results
            const result = await client.eval(`
                const results = [];
                const docs = cts.search(${query});
                let count = 0;
                let skip = ${offset};
                let max = ${limit};
                
                for (const doc of docs) {
                    if (skip > 0) {
                        skip--;
                        continue;
                    }
                    if (count >= max) {
                        break;
                    }
                    results.push({
                        uri: xdmp.nodeUri(doc),
                        content: doc.toObject()
                    });
                    count++;
                }
                
                xdmp.toJSON({
                    results: results,
                    total: cts.estimate(${query}),
                    returned: count
                });
            `).result();
            
            if (result && result.length > 0) {
                return {
                    content: [{
                        type: "text",
                        text: JSON.stringify(result[0].value, null, 2)
                    }]
                };
            } else {
                return {
                    content: [{
                        type: "text",
                        text: "No results found"
                    }]
                };
            }
        } catch (err: unknown) {
            const error = err as Error;
            return {
                content: [{
                    type: "text",
                    text: `Error executing query: ${error.message}`
                }],
                isError: true
            };
        }
    }
);

const transport = new StdioServerTransport();
server.connect(transport);
