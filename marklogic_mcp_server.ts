import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import marklogic from "marklogic";
import { z } from "zod";

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
    authType: 'DIGEST'
} as const;

// Helper to create MarkLogic client
const getClient = () => {
    return new marklogic.Client(ML_CONFIG);
};

// Tool to read documents
server.tool(
    "readDocument",
    { uri: z.string() },
    async ({ uri }) => {
        const client = getClient();
        try {
            const result = await client.eval(`
                xdmp.toJSON(
                    cts.doc("${uri}").toObject()
                )
            `);
            
            return {
                content: [{
                    type: "text",
                    text: JSON.stringify(JSON.parse(result as string), null, 2)
                }]
            };
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

const transport = new StdioServerTransport();
server.connect(transport);
