export interface QueryRequest {
  query: string;
  table: string;
}

export interface QueryMetadata {
  intent: string;
  engine_used: string;
}

export interface QueryResponse {
  explanation: string;
  metadata: QueryMetadata;
}
