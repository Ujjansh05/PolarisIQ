// types/api.ts

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
  image_url?: string;
}

export interface ToolQueryResponse {
  tool_result: string;
  metadata: {
    mode: string;
    table: string;
  };
  image_url?: string;
}

export interface HealthResponse {
  status: string;
  uptime_seconds: number;
  model_loaded: boolean;
  db_path: string;
}

export interface TableInfo {
  name: string;
  rows: number;
  columns: number;
}

export interface TablesResponse {
  tables: TableInfo[];
}

export interface ColumnInfo {
  name: string;
  type: string;
  nullable: boolean;
  null_percent?: number;
}

export interface SchemaResponse {
  table_name: string;
  columns: ColumnInfo[];
  row_count: number;
}

export interface PreviewResponse {
  table_name: string;
  columns: string[];
  rows: Record<string, unknown>[];
  total: number;
}

export interface IngestResponse {
  status: string;
  table_name: string;
  rows: number;
  columns: number;
}

export interface StatsResponse {
  table_count: number;
  total_rows: number;
  query_count: number;
  avg_latency_ms: number;
  uptime_seconds: number;
}

export interface LogEntry {
  timestamp: string;
  intent: string;
  engine: string;
  row_count: number;
  execution_time_ms: number;
}

export interface LogsResponse {
  logs: LogEntry[];
}

export interface CorrelationEntry {
  column_x: string;
  column_y: string;
  correlation: number | null;
}

export interface CorrelationsResponse {
  table_name: string;
  correlations: CorrelationEntry[];
}

export interface StatisticEntry {
  column: string;
  mean: number | null;
  std: number | null;
  min: number | null;
  max: number | null;
}

export interface StatisticsResponse {
  table_name: string;
  statistics: StatisticEntry[];
}
