import { useState, useEffect } from 'react';
import { ArrowUpRight, ArrowDownRight, Activity, Zap, Database, Clock, RefreshCw } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { fetchStats, fetchLogs, fetchHealth } from '../../services/api';
import type { StatsResponse, LogEntry, HealthResponse } from '../../types/api';

interface StatCardProps {
    title: string;
    value: string;
    icon: React.ElementType;
    subtitle: string;
    accentColor?: string;
}

const StatCard = ({ title, value, icon: Icon, subtitle, accentColor = 'primary' }: StatCardProps) => (
    <div className="glass-neon p-6 relative group overflow-hidden">
        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <Icon size={48} className={`text-${accentColor}`} />
        </div>
        <div className="flex justify-between items-start mb-4 relative z-10">
            <h3 className="text-sm font-medium text-slate-400">{title}</h3>
            <div className="p-2 rounded-lg bg-white/5 border border-white/10">
                <Icon size={16} className="text-secondary" />
            </div>
        </div>
        <h2 className="text-3xl font-bold text-white tracking-tight relative z-10">{value}</h2>
        <p className="text-xs text-slate-500 mt-2">{subtitle}</p>
    </div>
);

const HomeDashboard = () => {
    const [stats, setStats] = useState<StatsResponse | null>(null);
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const [health, setHealth] = useState<HealthResponse | null>(null);
    const [loading, setLoading] = useState(true);

    const loadData = async () => {
        setLoading(true);
        try {
            const [s, l, h] = await Promise.all([
                fetchStats().catch(() => null),
                fetchLogs(20).catch(() => ({ logs: [] })),
                fetchHealth().catch(() => null),
            ]);
            if (s) setStats(s);
            setLogs(l.logs);
            if (h) setHealth(h);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { loadData(); }, []);

    // Build chart data from logs (group by intent)
    const chartData = logs.slice().reverse().map((log, i) => ({
        name: `Q${i + 1}`,
        latency: log.execution_time_ms,
        rows: log.row_count || 0,
    }));

    const formatUptime = (seconds: number) => {
        if (seconds < 60) return `${Math.round(seconds)}s`;
        if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
        return `${Math.round(seconds / 3600)}h ${Math.round((seconds % 3600) / 60)}m`;
    };

    return (
        <div className="space-y-6 animate-in fade-in duration-500 slide-in-from-bottom-4">
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-white mb-2">System Overview</h1>
                    <p className="text-slate-400">Live monitoring of your PolarisIQ engine.</p>
                </div>
                <button
                    onClick={loadData}
                    disabled={loading}
                    className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors px-3 py-2 rounded-lg border border-cardBorder hover:border-slate-600"
                >
                    <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
                    Refresh
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard
                    title="Total Queries"
                    value={stats ? stats.query_count.toLocaleString() : '—'}
                    icon={Zap}
                    subtitle="Queries processed since start"
                />
                <StatCard
                    title="Avg Latency"
                    value={stats ? `${stats.avg_latency_ms}ms` : '—'}
                    icon={Activity}
                    subtitle="Average query execution time"
                />
                <StatCard
                    title="Data Tables"
                    value={stats ? stats.table_count.toString() : '—'}
                    icon={Database}
                    subtitle={stats ? `${stats.total_rows.toLocaleString()} total rows` : 'No data'}
                />
                <StatCard
                    title="Uptime"
                    value={stats ? formatUptime(stats.uptime_seconds) : '—'}
                    icon={Clock}
                    subtitle="Engine running time"
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 glass p-6">
                    <div className="flex justify-between items-center mb-6">
                        <div>
                            <h3 className="text-lg font-bold text-white">Query Performance</h3>
                            <p className="text-sm text-slate-400">
                                {logs.length > 0 ? `Last ${logs.length} queries` : 'No queries yet'}
                            </p>
                        </div>
                    </div>
                    <div className="h-[300px] w-full">
                        {chartData.length > 0 ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                    <defs>
                                        <linearGradient id="colorLatency" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                                    <XAxis dataKey="name" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                                    <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#11121e', borderColor: 'rgba(99, 102, 241, 0.2)', borderRadius: '8px', color: '#fff' }}
                                        itemStyle={{ color: '#e2e8f0' }}
                                    />
                                    <Area type="monotone" dataKey="latency" name="Latency (ms)" stroke="#6366f1" strokeWidth={2} fillOpacity={1} fill="url(#colorLatency)" />
                                </AreaChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="h-full flex items-center justify-center text-slate-500 text-sm">
                                Run some queries to see performance data here.
                            </div>
                        )}
                    </div>
                </div>

                <div className="glass p-6 flex flex-col">
                    <h3 className="text-lg font-bold text-white mb-2">System Health</h3>
                    <p className="text-sm text-slate-400 mb-6">Real-time engine status</p>

                    <div className="space-y-6 flex-1">
                        <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                                <span className="text-slate-300 font-medium">Backend Status</span>
                                <span className={health?.status === 'online' ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'}>
                                    {health?.status === 'online' ? 'Online' : 'Offline'}
                                </span>
                            </div>
                            <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                                <div
                                    className={`h-full ${health?.status === 'online' ? 'bg-emerald-500 shadow-[0_0_10px_#10b981]' : 'bg-rose-500'}`}
                                    style={{ width: health?.status === 'online' ? '100%' : '0%' }}
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                                <span className="text-slate-300 font-medium">LLM Model</span>
                                <span className={health?.model_loaded ? 'text-emerald-400 font-bold' : 'text-amber-400 font-bold'}>
                                    {health?.model_loaded ? 'Loaded' : 'Not Loaded'}
                                </span>
                            </div>
                            <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                                <div
                                    className={`h-full ${health?.model_loaded ? 'bg-emerald-500 shadow-[0_0_10px_#10b981]' : 'bg-amber-500'}`}
                                    style={{ width: health?.model_loaded ? '100%' : '30%' }}
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                                <span className="text-slate-300 font-medium">DuckDB</span>
                                <span className="text-emerald-400 font-bold">Active</span>
                            </div>
                            <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                                <div className="h-full bg-emerald-500 shadow-[0_0_10px_#10b981]" style={{ width: '100%' }} />
                            </div>
                        </div>
                    </div>

                    {health && (
                        <div className="mt-6 p-4 rounded-xl bg-primary/10 border border-primary/20 flex items-start gap-3">
                            <Zap className="text-primary mt-0.5 flex-shrink-0" size={18} />
                            <div>
                                <h4 className="text-sm font-medium text-white">Engine Active</h4>
                                <p className="text-xs text-slate-400 mt-1">
                                    Database: {health.db_path} | Uptime: {formatUptime(health.uptime_seconds)}
                                </p>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Recent Query Log */}
            {logs.length > 0 && (
                <div className="glass p-6">
                    <h3 className="text-lg font-bold text-white mb-4">Recent Queries</h3>
                    <div className="overflow-x-auto rounded-lg border border-cardBorder">
                        <table className="w-full text-left text-sm">
                            <thead className="bg-white/5 text-slate-400 font-medium">
                                <tr>
                                    <th className="px-4 py-3">Time</th>
                                    <th className="px-4 py-3">Intent</th>
                                    <th className="px-4 py-3">Engine</th>
                                    <th className="px-4 py-3 text-right">Rows</th>
                                    <th className="px-4 py-3 text-right">Latency</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-cardBorder">
                                {logs.slice(0, 10).map((log, i) => (
                                    <tr key={i} className="hover:bg-white/5 transition-colors">
                                        <td className="px-4 py-3 text-slate-400 text-xs font-mono">{log.timestamp}</td>
                                        <td className="px-4 py-3">
                                            <span className="text-xs px-2 py-0.5 bg-primary/10 text-primary rounded-full border border-primary/20">
                                                {log.intent}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3">
                                            <span className="text-xs px-2 py-0.5 bg-secondary/10 text-secondary rounded-full border border-secondary/20">
                                                {log.engine}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3 text-right text-slate-300">{log.row_count?.toLocaleString() || '—'}</td>
                                        <td className="px-4 py-3 text-right text-slate-300 font-mono">{log.execution_time_ms}ms</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
};

export default HomeDashboard;
