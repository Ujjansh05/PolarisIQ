import { Database, Search, Filter, HardDrive, Table2, Calendar, Hash, Type, AlignLeft } from 'lucide-react';

const datasets = [
    { id: 1, name: 'telemetry_events', schema: 'events', rows: '4.2B', size: '1.2 TB', updated: '2m ago' },
    { id: 2, name: 'user_profiles', schema: 'public', rows: '12.5M', size: '4.5 GB', updated: '1h ago' },
    { id: 3, name: 'payment_transactions', schema: 'finance', rows: '840M', size: '210 GB', updated: '15m ago' },
    { id: 4, name: 'product_catalog', schema: 'inventory', rows: '450K', size: '1.2 GB', updated: '1d ago' },
];

const columns = [
    { name: 'event_id', type: 'UUID', icon: Hash, nulls: '0%', distinct: '100%' },
    { name: 'timestamp', type: 'TIMESTAMP', icon: Calendar, nulls: '0%', distinct: '99.8%' },
    { name: 'user_id', type: 'VARCHAR', icon: Type, nulls: '2.4%', distinct: '45.2%' },
    { name: 'event_type', type: 'VARCHAR', icon: Type, nulls: '0%', distinct: '12' },
    { name: 'properties', type: 'JSONB', icon: AlignLeft, nulls: '15.2%', distinct: '...' },
    { name: 'revenue', type: 'DECIMAL', icon: Hash, nulls: '85.4%', distinct: '1.2M' },
];

const DataWorkspace = () => {
    return (
        <div className="h-full flex flex-col gap-6 animate-in fade-in duration-500">
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Data Workspace</h1>
                    <p className="text-slate-400">Explore, profile, and manage your connected datasets.</p>
                </div>
                <div className="flex gap-3">
                    <div className="relative group">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                        <input
                            type="text"
                            placeholder="Search datasets..."
                            className="pl-9 pr-4 py-2 bg-card/50 border border-cardBorder rounded-lg text-sm text-slate-200 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary w-64 transition-all"
                        />
                    </div>
                    <button className="p-2 border border-cardBorder rounded-lg bg-card/50 text-slate-300 hover:text-white hover:border-slate-500 transition-colors">
                        <Filter size={18} />
                    </button>
                </div>
            </div>

            <div className="flex gap-6 flex-1 min-h-0">
                {/* Left Sidebar: Dataset List */}
                <div className="w-1/3 glass flex flex-col overflow-hidden">
                    <div className="p-4 border-b border-cardBorder bg-white/5 font-medium flex gap-2 items-center text-slate-200">
                        <Database size={16} className="text-primary" />
                        Connected Sources
                    </div>
                    <div className="flex-1 overflow-y-auto p-3 space-y-2 scrollbar-hide">
                        {datasets.map((ds, idx) => (
                            <div
                                key={ds.id}
                                className={`p-3 rounded-lg border cursor-pointer transition-all ${idx === 0
                                        ? 'border-primary/50 bg-primary/10 shadow-[inset_0_0_20px_rgba(99,102,241,0.05)]'
                                        : 'border-cardBorder bg-card/30 hover:bg-card/80 hover:border-slate-600'
                                    }`}
                            >
                                <div className="flex justify-between items-start mb-2">
                                    <h3 className={`font-medium ${idx === 0 ? 'text-primary' : 'text-slate-300'}`}>
                                        {ds.schema}.{ds.name}
                                    </h3>
                                    <span className="text-xs text-slate-500 bg-slate-800 px-1.5 py-0.5 rounded">{ds.updated}</span>
                                </div>
                                <div className="flex gap-4 text-xs text-slate-400">
                                    <span className="flex items-center gap-1"><Table2 size={12} /> {ds.rows} rows</span>
                                    <span className="flex items-center gap-1"><HardDrive size={12} /> {ds.size}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Right Area: Schema Explorer */}
                <div className="flex-1 flex flex-col gap-4">
                    <div className="glass p-6 flex flex-col">
                        <div className="flex justify-between items-start pb-6 border-b border-cardBorder">
                            <div>
                                <div className="flex items-center gap-3 mb-1">
                                    <h2 className="text-xl font-bold text-white">events.telemetry_events</h2>
                                    <span className="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider text-emerald-400 bg-emerald-400/10 border border-emerald-400/20">LIVE</span>
                                </div>
                                <p className="text-sm text-slate-400">Main clickstream and application telemetry event table.</p>
                            </div>
                            <button className="text-primary hover:text-primary-light text-sm font-medium transition-colors">
                                Query Table
                            </button>
                        </div>

                        <div className="pt-6">
                            <h3 className="text-sm font-bold text-slate-300 mb-4 uppercase tracking-wider">Schema & Statistics</h3>
                            <div className="w-full overflow-x-auto rounded-lg border border-cardBorder">
                                <table className="w-full text-left text-sm whitespace-nowrap">
                                    <thead className="bg-white/5 text-slate-400 font-medium">
                                        <tr>
                                            <th className="px-4 py-3">Column Name</th>
                                            <th className="px-4 py-3">Type</th>
                                            <th className="px-4 py-3 text-right">Null %</th>
                                            <th className="px-4 py-3 text-right">Distinct Values</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-cardBorder bg-card/30">
                                        {columns.map(col => {
                                            const Icon = col.icon;
                                            return (
                                                <tr key={col.name} className="hover:bg-white/5 transition-colors">
                                                    <td className="px-4 py-3 font-medium text-slate-200 flex items-center gap-2">
                                                        <Icon size={14} className="text-slate-500" />
                                                        {col.name}
                                                    </td>
                                                    <td className="px-4 py-3">
                                                        <span className="text-[10px] px-1.5 py-0.5 bg-slate-800 text-slate-300 rounded font-mono border border-slate-700">
                                                            {col.type}
                                                        </span>
                                                    </td>
                                                    <td className="px-4 py-3 text-right text-slate-400">{col.nulls}</td>
                                                    <td className="px-4 py-3 text-right text-slate-400">{col.distinct}</td>
                                                </tr>
                                            );
                                        })}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>

                    <div className="glass p-6 flex-1 flex flex-col justify-center items-center text-center">
                        <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4 shadow-neon">
                            <Table2 className="text-primary w-8 h-8" />
                        </div>
                        <h3 className="text-lg font-bold text-white mb-2">Data Preview Available</h3>
                        <p className="text-sm text-slate-400 max-w-sm mb-6">Select "Query Table" to open this dataset in the AI Query Studio, or preview the top 100 rows instantly.</p>
                        <button className="bg-white/10 hover:bg-white/20 text-white border border-white/20 px-4 py-2 rounded-lg font-medium text-sm transition-all">
                            Preview Data
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DataWorkspace;
