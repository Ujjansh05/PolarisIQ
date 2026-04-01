import { useState, useEffect } from 'react';
import { Activity, CheckCircle2, Circle, Clock, RefreshCw, Zap, Database, Cpu } from 'lucide-react';
import { fetchLogs } from '../../services/api';
import type { LogEntry } from '../../types/api';

const ENGINE_COLORS: Record<string, string> = {
    duckdb: 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20',
    python_sklearn: 'text-amber-400 bg-amber-400/10 border-amber-400/20',
    polars: 'text-cyan-400 bg-cyan-400/10 border-cyan-400/20',
    visualization: 'text-purple-400 bg-purple-400/10 border-purple-400/20',
};

const ENGINE_ICONS: Record<string, React.ElementType> = {
    duckdb: Database,
    python_sklearn: Cpu,
    polars: Zap,
    visualization: Activity,
};

const PipelineMonitor = () => {
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const [loading, setLoading] = useState(true);

    const loadLogs = async () => {
        setLoading(true);
        try {
            const res = await fetchLogs(100);
            setLogs(res.logs);
        } catch {
            setLogs([]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { loadLogs(); }, []);

    // Compute summary stats
    const totalQueries = logs.length;
    const avgLatency = logs.length > 0
        ? Math.round(logs.reduce((sum, l) => sum + l.execution_time_ms, 0) / logs.length)
        : 0;
    const totalRows = logs.reduce((sum, l) => sum + (l.row_count || 0), 0);

    // Engine usage breakdown
    const engineCounts: Record<string, number> = {};
    logs.forEach(l => {
        engineCounts[l.engine] = (engineCounts[l.engine] || 0) + 1;
    });

    return (
        <div className="h-full flex flex-col gap-6 animate-in fade-in duration-500">
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Pipeline Monitor</h1>
                    <p className="text-slate-400">Query execution history and engine performance.</p>
                </div>
                <button
                    onClick={loadLogs}
                    disabled={loading}
                    className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors px-3 py-2 rounded-lg border border-cardBorder hover:border-slate-600"
                >
                    <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
                    Refresh
                </button>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="glass p-4 flex items-center gap-4">
                    <div className="p-2 rounded-lg bg-primary/20">
                        <Activity size={20} className="text-primary" />
                    </div>
                    <div>
                        <p className="text-xs text-slate-400">Total Queries</p>
                        <p className="text-xl font-bold text-white">{totalQueries}</p>
                    </div>
                </div>
                <div className="glass p-4 flex items-center gap-4">
                    <div className="p-2 rounded-lg bg-secondary/20">
                        <Clock size={20} className="text-secondary" />
                    </div>
                    <div>
                        <p className="text-xs text-slate-400">Avg Latency</p>
                        <p className="text-xl font-bold text-white">{avgLatency}ms</p>
                    </div>
                </div>
                <div className="glass p-4 flex items-center gap-4">
                    <div className="p-2 rounded-lg bg-emerald-500/20">
                        <Database size={20} className="text-emerald-400" />
                    </div>
                    <div>
                        <p className="text-xs text-slate-400">Rows Processed</p>
                        <p className="text-xl font-bold text-white">{totalRows.toLocaleString()}</p>
                    </div>
                </div>
                <div className="glass p-4 flex items-center gap-4">
                    <div className="p-2 rounded-lg bg-amber-500/20">
                        <Cpu size={20} className="text-amber-400" />
                    </div>
                    <div>
                        <p className="text-xs text-slate-400">Engines Used</p>
                        <p className="text-xl font-bold text-white">{Object.keys(engineCounts).length}</p>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-1 min-h-0">
                {/* Engine Breakdown */}
                <div className="glass p-6">
                    <h3 className="text-sm font-bold text-slate-300 mb-4 uppercase tracking-wider">Engine Usage</h3>
                    {Object.keys(engineCounts).length > 0 ? (
                        <div className="space-y-4">
                            {Object.entries(engineCounts)
                                .sort(([, a], [, b]) => b - a)
                                .map(([eng, count]) => {
                                    const Icon = ENGINE_ICONS[eng] || Zap;
                                    const pct = Math.round((count / totalQueries) * 100);
                                    return (
                                        <div key={eng} className="space-y-2">
                                            <div className="flex justify-between items-center text-sm">
                                                <span className="text-slate-300 flex items-center gap-2">
                                                    <Icon size={14} /> {eng}
                                                </span>
                                                <span className="text-slate-400 font-mono text-xs">{count} ({pct}%)</span>
                                            </div>
                                            <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                                                <div
                                                    className="h-full bg-primary rounded-full transition-all"
                                                    style={{ width: `${pct}%` }}
                                                />
                                            </div>
                                        </div>
                                    );
                                })}
                        </div>
                    ) : (
                        <p className="text-sm text-slate-500">No queries yet.</p>
                    )}
                </div>

                {/* Execution Log Table */}
                <div className="lg:col-span-3 glass p-6 flex flex-col overflow-hidden">
                    <h3 className="text-sm font-bold text-slate-300 mb-4 uppercase tracking-wider flex items-center gap-2">
                        <Activity size={16} className="text-primary" />
                        Execution Log
                    </h3>

                    {logs.length === 0 ? (
                        <div className="flex-1 flex items-center justify-center text-slate-500 text-sm">
                            No execution history yet. Run some queries first.
                        </div>
                    ) : (
                        <div className="flex-1 overflow-y-auto scrollbar-hide">
                            <div className="space-y-2">
                                {logs.map((log, i) => {
                                    const Icon = ENGINE_ICONS[log.engine] || Zap;
                                    const colorClass = ENGINE_COLORS[log.engine] || 'text-slate-400 bg-slate-400/10 border-slate-400/20';

                                    return (
                                        <div key={i} className="flex items-center gap-4 p-3 rounded-lg border border-cardBorder hover:bg-white/5 transition-colors">
                                            <div className="shrink-0">
                                                <CheckCircle2 size={16} className="text-emerald-500" />
                                            </div>

                                            <div className="flex-1 min-w-0">
                                                <div className="flex items-center gap-2 mb-1">
                                                    <span className={`text-xs px-2 py-0.5 rounded-full border ${colorClass} font-medium flex items-center gap-1`}>
                                                        <Icon size={10} /> {log.engine}
                                                    </span>
                                                    <span className="text-xs px-2 py-0.5 bg-primary/10 text-primary rounded-full border border-primary/20">
                                                        {log.intent}
                                                    </span>
                                                </div>
                                                <p className="text-xs text-slate-500 font-mono truncate">{log.timestamp}</p>
                                            </div>

                                            <div className="text-right shrink-0">
                                                <p className="text-sm text-white font-mono">{log.execution_time_ms}ms</p>
                                                <p className="text-xs text-slate-500">{log.row_count?.toLocaleString() || '—'} rows</p>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default PipelineMonitor;
