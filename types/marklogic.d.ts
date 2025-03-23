declare module 'marklogic' {
    export interface ConnectionParams {
        host: string;
        port: number;
        user: string;
        password: string;
        database?: string;
        authType?: 'DIGEST' | 'BASIC';
    }

    export interface ResponseSelector {
        result(): Promise<any>;
        stream(): any;
    }

    export interface DatabaseClient {
        eval(xquery: string): ResponseSelector;
        documents: {
            read(options: any): ResponseSelector;
            write(options: any): ResponseSelector;
            remove(uris: string[]): ResponseSelector;
        };
    }

    export function createDatabaseClient(config: ConnectionParams): DatabaseClient;
}

export default marklogic; 