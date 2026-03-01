import { Lightbulb, TrendingUp, AlertTriangle, CheckCircle, PieChart, BarChart3, LineChart } from 'lucide-react';

const InsightsPage = () => {
    return (
        <div className="h-full flex flex-col gap-6 animate-in fade-in duration-500">
            <div>
                <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Automated Insights</h1>
                <p className="text-slate-400">AI-generated findings and recommendations based on recent data patterns.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="md:col-span-2 space-y-6">
                    <div className="glass p-6 group">
                        <div className="flex items-start gap-4">
                            <div className="w-10 h-10 rounded-full bg-emerald-500/20 flex items-center justify-center shrink-0 border border-emerald-500/30">
                                <TrendingUp className="text-emerald-400" size={20} />
                            </div>
                            <div className="flex-1">
                                <div className="flex justify-between items-start mb-2">
                                    <h3 className="text-lg font-bold text-white group-hover:text-emerald-400 transition-colors">Unexpected Revenue Spike in EU-West Region</h3>
                                    <span className="text-xs font-medium px-2 py-1 bg-emerald-500/10 text-emerald-400 rounded-full border border-emerald-500/20">98% Confidence</span>
                                </div>
                                <p className="text-sm text-slate-300 mb-4 leading-relaxed">
                                    PolarisIQ detected a 42% anomalous increase in revenue for the 'Enterprise Software' category in the eu-west-1 region between 14:00 and 18:00 UTC over the last 3 days. Correlation analysis suggests this is highly tied to the recent V2.4 feature release.
                                </p>
                                <div className="flex flex-wrap gap-2 mt-4">
                                    <button className="text-xs text-primary bg-primary/10 border border-primary/20 px-3 py-1.5 rounded-lg hover:bg-primary/20 transition-colors">View Correlated Events</button>
                                    <button className="text-xs text-slate-300 bg-white/5 border border-white/10 px-3 py-1.5 rounded-lg hover:bg-white/10 transition-colors">Generate Report</button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="glass p-6 group">
                        <div className="flex items-start gap-4">
                            <div className="w-10 h-10 rounded-full bg-amber-500/20 flex items-center justify-center shrink-0 border border-amber-500/30">
                                <AlertTriangle className="text-amber-400" size={20} />
                            </div>
                            <div className="flex-1">
                                <div className="flex justify-between items-start mb-2">
                                    <h3 className="text-lg font-bold text-white group-hover:text-amber-400 transition-colors">Data Quality Drift Detected</h3>
                                    <span className="text-xs font-medium px-2 py-1 bg-amber-500/10 text-amber-400 rounded-full border border-amber-500/20">84% Confidence</span>
                                </div>
                                <p className="text-sm text-slate-300 mb-4 leading-relaxed">
                                    The null rate for the <code className="bg-slate-800 px-1 py-0.5 rounded text-accent text-xs">user_agent</code> column in the <code className="bg-slate-800 px-1 py-0.5 rounded text-accent text-xs">telemetry_events</code> table has increased from 0.05% to 4.2% over the last 24 hours. This usually indicates a tracking SDK integration issue on mobile clients.
                                </p>
                                <div className="flex flex-wrap gap-2 mt-4">
                                    <button className="text-xs text-primary bg-primary/10 border border-primary/20 px-3 py-1.5 rounded-lg hover:bg-primary/20 transition-colors">Open Data Profiler</button>
                                    <button className="text-xs text-slate-300 bg-white/5 border border-white/10 px-3 py-1.5 rounded-lg hover:bg-white/10 transition-colors">Acknowledge</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="space-y-6">
                    <div className="glass p-6">
                        <h3 className="text-sm font-bold text-slate-300 mb-4 uppercase tracking-wider flex items-center gap-2">
                            <Lightbulb size={16} className="text-secondary" /> Key Metrics Summary
                        </h3>

                        <div className="space-y-4">
                            <div className="flex items-center gap-3 p-3 rounded-lg bg-card/50 border border-cardBorder">
                                <PieChart className="text-primary w-5 h-5 shrink-0" />
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm text-white font-medium truncate">Customer Segmentation</p>
                                    <p className="text-xs text-slate-400">Enterprise users up by 12%</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-3 p-3 rounded-lg bg-card/50 border border-cardBorder">
                                <LineChart className="text-secondary w-5 h-5 shrink-0" />
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm text-white font-medium truncate">Churn Prediction</p>
                                    <p className="text-xs text-slate-400">Overall risk decreased 2.1%</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-3 p-3 rounded-lg bg-card/50 border border-cardBorder">
                                <BarChart3 className="text-accent w-5 h-5 shrink-0" />
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm text-white font-medium truncate">Query Performance</p>
                                    <p className="text-xs text-slate-400">95th percentile under 200ms</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="glass p-6">
                        <h3 className="text-sm font-bold text-slate-300 mb-4 uppercase tracking-wider flex items-center gap-2">
                            <CheckCircle size={16} className="text-emerald-400" /> Actions Taken
                        </h3>
                        <ul className="space-y-3 relative before:absolute before:inset-y-0 before:left-2 before:w-0.5 before:bg-slate-800">
                            <li className="relative pl-6">
                                <div className="absolute left-[3px] top-1.5 w-1.5 h-1.5 rounded-full bg-slate-500 ring-4 ring-card"></div>
                                <p className="text-xs text-slate-300">Optimized Materialized Views</p>
                                <p className="text-[10px] text-slate-500 mt-0.5">2 hours ago</p>
                            </li>
                            <li className="relative pl-6">
                                <div className="absolute left-[3px] top-1.5 w-1.5 h-1.5 rounded-full bg-slate-500 ring-4 ring-card"></div>
                                <p className="text-xs text-slate-300">Generated weekly summary report</p>
                                <p className="text-[10px] text-slate-500 mt-0.5">8 hours ago</p>
                            </li>
                            <li className="relative pl-6">
                                <div className="absolute left-[3px] top-1.5 w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_#10b981] ring-4 ring-card"></div>
                                <p className="text-xs text-emerald-400 font-medium">Re-indexed large event table</p>
                                <p className="text-[10px] text-slate-500 mt-0.5">1 day ago</p>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default InsightsPage;
