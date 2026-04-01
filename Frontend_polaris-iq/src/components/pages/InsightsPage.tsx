import { useState, useEffect } from 'react';
import { Lightbulb, TrendingUp, AlertTriangle, BarChart3, LineChart, RefreshCw } from 'lucide-react';
import { fetchTables, fetchCorrelations, fetchStatistics } from '../../services/api';
import type { TableInfo, CorrelationEntry, StatisticEntry } from '../../types/api';

const InsightsPage = () => {
    const [tables, setTables] = useState<TableInfo[]>([]);
    const [selectedTable, setSelectedTable] = useState<string>('');
    const [correlations, setCorrelations] = useState<CorrelationEntry[]>([]);
    const [statistics, setStatistics] = useState<StatisticEntry[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchTables()
            .then(res => {
                setTables(res.tables);
                if (res.tables.length > 0) {
                    setSelectedTable(res.tables[0].name);
                }
            })
            .catch(() => setTables([]))
            .finally(() => setLoading(false));
    }, []);

    useEffect(() => {
        if (!selectedTable) return;
        setLoading(true);
        Promise.all([
            fetchCorrelations(selectedTable).catch(() => ({ correlations: [] })),
            fetchStatistics(selectedTable).catch(() => ({ statistics: [] })),
        ]).then(([corr, stats]) => {
            setCorrelations(corr.correlations);
            setStatistics(stats.statistics);
        }).finally(() => setLoading(false));
    }, [selectedTable]);

    const strongCorrelations = correlations.filter(c => c.correlation !== null && Math.abs(c.correlation) > 0.5);
    const weakCorrelations = correlations.filter(c => c.correlation !== null && Math.abs(c.correlation) <= 0.5);

    return (
        <div className="h-full flex flex-col gap-6 animate-in fade-in duration-500">
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Data Insights</h1>
                    <p className="text-slate-400">Correlations, statistics, and profiling from your data.</p>
                </div>
                <div className="flex gap-3 items-center">
                    <select
                        value={selectedTable}
                        onChange={e => setSelectedTable(e.target.value)}
                        className="bg-card/50 border border-cardBorder rounded-lg text-sm text-slate-200 px-3 py-2 focus:outline-none focus:border-primary"
                    >
                        {tables.map(t => (
                            <option key={t.name} value={t.name}>{t.name}</option>
                        ))}
                    </select>
                </div>
            </div>

            {loading ? (
                <div className="flex-1 flex items-center justify-center">
                    <RefreshCw size={24} className="text-primary animate-spin" />
                </div>
            ) : tables.length === 0 ? (
                <div className="flex-1 flex items-center justify-center text-slate-500">
                    No tables found. Ingest data first via Data Workspace or CLI.
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="md:col-span-2 space-y-6">
                        {/* Strong Correlations */}
                        {strongCorrelations.length > 0 && (
                            <div className="glass p-6">
                                <div className="flex items-start gap-4 mb-4">
                                    <div className="w-10 h-10 rounded-full bg-emerald-500/20 flex items-center justify-center shrink-0 border border-emerald-500/30">
                                        <TrendingUp className="text-emerald-400" size={20} />
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-bold text-white">Strong Correlations Found</h3>
                                        <p className="text-sm text-slate-400">
                                            {strongCorrelations.length} column pair{strongCorrelations.length !== 1 ? 's' : ''} with |r| &gt; 0.5
                                        </p>
                                    </div>
                                </div>
                                <div className="space-y-3">
                                    {strongCorrelations.map((c, i) => (
                                        <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-card/50 border border-cardBorder">
                                            <div className="flex items-center gap-2">
                                                <span className="text-sm font-medium text-slate-200">{c.column_x}</span>
                                                <span className="text-xs text-slate-500">↔</span>
                                                <span className="text-sm font-medium text-slate-200">{c.column_y}</span>
                                            </div>
                                            <span className={`text-sm font-bold px-2 py-0.5 rounded-full ${
                                                c.correlation! > 0
                                                    ? 'text-emerald-400 bg-emerald-400/10'
                                                    : 'text-rose-400 bg-rose-400/10'
                                            }`}>
                                                r = {c.correlation!.toFixed(4)}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Weak/No Correlations */}
                        {weakCorrelations.length > 0 && (
                            <div className="glass p-6">
                                <div className="flex items-start gap-4 mb-4">
                                    <div className="w-10 h-10 rounded-full bg-amber-500/20 flex items-center justify-center shrink-0 border border-amber-500/30">
                                        <AlertTriangle className="text-amber-400" size={20} />
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-bold text-white">Weak Correlations</h3>
                                        <p className="text-sm text-slate-400">
                                            {weakCorrelations.length} pair{weakCorrelations.length !== 1 ? 's' : ''} with |r| ≤ 0.5
                                        </p>
                                    </div>
                                </div>
                                <div className="space-y-2">
                                    {weakCorrelations.map((c, i) => (
                                        <div key={i} className="flex items-center justify-between p-2 px-3 rounded-lg bg-card/30 text-sm">
                                            <span className="text-slate-400">{c.column_x} ↔ {c.column_y}</span>
                                            <span className="text-slate-500 font-mono">{c.correlation?.toFixed(4) ?? '—'}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {correlations.length === 0 && (
                            <div className="glass p-6 text-center text-slate-500">
                                <p>No correlations available for this table.</p>
                                <p className="text-xs mt-1">Ensure the table has numeric columns and was profiled during ingestion.</p>
                            </div>
                        )}
                    </div>

                    {/* Right: Statistics Summary */}
                    <div className="space-y-6">
                        <div className="glass p-6">
                            <h3 className="text-sm font-bold text-slate-300 mb-4 uppercase tracking-wider flex items-center gap-2">
                                <Lightbulb size={16} className="text-secondary" /> Column Statistics
                            </h3>
                            {statistics.length > 0 ? (
                                <div className="space-y-4">
                                    {statistics.map((s, i) => (
                                        <div key={i} className="p-3 rounded-lg bg-card/50 border border-cardBorder">
                                            <div className="flex items-center gap-2 mb-2">
                                                <BarChart3 className="text-primary w-4 h-4" />
                                                <p className="text-sm text-white font-medium truncate">{s.column}</p>
                                            </div>
                                            <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs">
                                                <div className="flex justify-between">
                                                    <span className="text-slate-500">Mean</span>
                                                    <span className="text-slate-300 font-mono">{s.mean?.toFixed(2) ?? '—'}</span>
                                                </div>
                                                <div className="flex justify-between">
                                                    <span className="text-slate-500">Std</span>
                                                    <span className="text-slate-300 font-mono">{s.std?.toFixed(2) ?? '—'}</span>
                                                </div>
                                                <div className="flex justify-between">
                                                    <span className="text-slate-500">Min</span>
                                                    <span className="text-slate-300 font-mono">{s.min?.toFixed(2) ?? '—'}</span>
                                                </div>
                                                <div className="flex justify-between">
                                                    <span className="text-slate-500">Max</span>
                                                    <span className="text-slate-300 font-mono">{s.max?.toFixed(2) ?? '—'}</span>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <p className="text-sm text-slate-500">No statistics available.</p>
                            )}
                        </div>

                        <div className="glass p-6">
                            <h3 className="text-sm font-bold text-slate-300 mb-4 uppercase tracking-wider flex items-center gap-2">
                                <LineChart size={16} className="text-accent" /> Summary
                            </h3>
                            <div className="space-y-3 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-slate-400">Table</span>
                                    <span className="text-white font-medium">{selectedTable}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-slate-400">Numeric Columns</span>
                                    <span className="text-white font-medium">{statistics.length}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-slate-400">Correlation Pairs</span>
                                    <span className="text-white font-medium">{correlations.length}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-slate-400">Strong (|r| &gt; 0.5)</span>
                                    <span className="text-emerald-400 font-bold">{strongCorrelations.length}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default InsightsPage;
