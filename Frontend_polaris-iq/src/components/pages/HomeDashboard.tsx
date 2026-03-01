import { ArrowUpRight, ArrowDownRight, Activity, Users, Zap, Database } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const data = [
    { name: 'Mon', queries: 4000, latency: 240 },
    { name: 'Tue', queries: 3000, latency: 139 },
    { name: 'Wed', queries: 2000, latency: 980 },
    { name: 'Thu', queries: 2780, latency: 390 },
    { name: 'Fri', queries: 1890, latency: 480 },
    { name: 'Sat', queries: 2390, latency: 380 },
    { name: 'Sun', queries: 3490, latency: 430 },
];

interface StatCardProps {
    title: string;
    value: string;
    change: string;
    isPositive: boolean;
    icon: React.ElementType;
    trend: string;
}

const StatCard = ({ title, value, change, isPositive, icon: Icon, trend }: StatCardProps) => (
    <div className="glass-neon p-6 relative group overflow-hidden">
        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <Icon size={48} className="text-primary" />
        </div>
        <div className="flex justify-between items-start mb-4 relative z-10">
            <h3 className="text-sm font-medium text-slate-400">{title}</h3>
            <div className="p-2 rounded-lg bg-white/5 border border-white/10">
                <Icon size={16} className="text-secondary" />
            </div>
        </div>
        <div className="flex items-baseline gap-2 relative z-10">
            <h2 className="text-3xl font-bold text-white tracking-tight">{value}</h2>
            <div className={`flex items-center text-xs font-medium px-2 py-0.5 rounded-full ${isPositive ? 'text-emerald-400 bg-emerald-400/10' : 'text-rose-400 bg-rose-400/10'}`}>
                {isPositive ? <ArrowUpRight size={14} className="mr-1" /> : <ArrowDownRight size={14} className="mr-1" />}
                {change}
            </div>
        </div>
        <p className="text-xs text-slate-500 mt-2">{trend} vs last week</p>
    </div >
);

const HomeDashboard = () => {
    return (
        <div className="space-y-6 animate-in fade-in duration-500 slide-in-from-bottom-4">
            <div>
                <h1 className="text-3xl font-bold tracking-tight text-white mb-2">System Overview</h1>
                <p className="text-slate-400">Monitoring AI Query engine and OLAP performance metrics.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard title="Active Queries" value="2,845" change="+12.5%" isPositive={true} icon={Zap} trend="Increased" />
                <StatCard title="Avg Latency" value="142ms" change="-8.2%" isPositive={true} icon={Activity} trend="Decreased" />
                <StatCard title="Data Processed" value="4.2 PB" change="+1.2%" isPositive={true} icon={Database} trend="Increased" />
                <StatCard title="Active Users" value="842" change="-2.4%" isPositive={false} icon={Users} trend="Decreased" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 glass p-6">
                    <div className="flex justify-between items-center mb-6">
                        <div>
                            <h3 className="text-lg font-bold text-white">Query Volume vs Latency</h3>
                            <p className="text-sm text-slate-400">7-day performance metrics</p>
                        </div>
                    </div>
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                <defs>
                                    <linearGradient id="colorQueries" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                                    </linearGradient>
                                    <linearGradient id="colorLatency" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#a855f7" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#a855f7" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                                <XAxis dataKey="name" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                                <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#11121e', borderColor: 'rgba(99, 102, 241, 0.2)', borderRadius: '8px', color: '#fff' }}
                                    itemStyle={{ color: '#e2e8f0' }}
                                />
                                <Area type="monotone" dataKey="queries" stroke="#6366f1" strokeWidth={2} fillOpacity={1} fill="url(#colorQueries)" />
                                <Area type="monotone" dataKey="latency" stroke="#a855f7" strokeWidth={2} fillOpacity={1} fill="url(#colorLatency)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="glass p-6 flex flex-col">
                    <h3 className="text-lg font-bold text-white mb-2">System Health</h3>
                    <p className="text-sm text-slate-400 mb-6">Real-time infrastructure status</p>

                    <div className="space-y-6 flex-1">
                        <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                                <span className="text-slate-300 font-medium">Query Engine</span>
                                <span className="text-emerald-400 font-bold">99.9%</span>
                            </div>
                            <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                                <div className="h-full bg-emerald-500 shadow-[0_0_10px_#10b981]" style={{ width: '99.9%' }}></div>
                            </div>
                        </div>

                        <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                                <span className="text-slate-300 font-medium">OLAP Database</span>
                                <span className="text-emerald-400 font-bold">98.5%</span>
                            </div>
                            <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                                <div className="h-full bg-emerald-500 shadow-[0_0_10px_#10b981]" style={{ width: '98.5%' }}></div>
                            </div>
                        </div>

                        <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                                <span className="text-slate-300 font-medium">AI Reasoning Layer</span>
                                <span className="text-amber-400 font-bold">85.2%</span>
                            </div>
                            <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                                <div className="h-full bg-amber-500 shadow-[0_0_10px_#f59e0b]" style={{ width: '85.2%' }}></div>
                            </div>
                        </div>

                        <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                                <span className="text-slate-300 font-medium">Data Pipelines</span>
                                <span className="text-emerald-400 font-bold">100%</span>
                            </div>
                            <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                                <div className="h-full bg-emerald-500 shadow-[0_0_10px_#10b981]" style={{ width: '100%' }}></div>
                            </div>
                        </div>
                    </div>

                    <div className="mt-6 p-4 rounded-xl bg-primary/10 border border-primary/20 flex items-start gap-3">
                        <Zap className="text-primary mt-0.5 flex-shrink-0" size={18} />
                        <div>
                            <h4 className="text-sm font-medium text-white">AI Optimization Suggested</h4>
                            <p className="text-xs text-slate-400 mt-1">Reasoning layer latency can be improved by warming up cluster nodes.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default HomeDashboard;
