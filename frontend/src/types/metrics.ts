export interface Metric {
  timestamp: string;
  value: number;
  source: string;
}

export interface MetricsState {
  hederaTxCount: Metric[];
  hederaUSDC: Metric[];
  greedFearIndex: Metric[];
  loading: boolean;
  error: string | null;
} 