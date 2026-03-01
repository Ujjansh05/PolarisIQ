import { Activity, CheckCircle2, Circle, ArrowRight, Save, UploadCloud, Cpu, Database } from 'lucide-react';

const PipelineNode = ({ title, status, icon: Icon, time }) => {
    const isDone = status === 'done';
    const isActive = status === 'active';

    return (
        <div className={`relative glass p-4 w-60 shrink-0 z-10 ${isActive ? 'shadow-neon border-primary/50' : ''}`}>
            <div className="flex justify-between items-start mb-3">
                <div className={`p-2 rounded-lg ${isActive ? 'bg-primary/20 text-primary' : 'bg-white/5 text-slate-400'}`}>
                    <Icon size={20} />
                </div>
                {isDone ? (
                    <CheckCircle2 size={18} className="text-emerald-400" />
                ) : isActive ? (
                    <div className="relative">
                        <Circle size={18} className="text-primary animate-spin" style={{ animationDuration: '3s' }} />
                        <div className="absolute inset-0 bg-primary/20 blur-md rounded-full animate-pulse"></div>
                    </div>
                ) : (
                    <Circle size={18} className="text-slate-600" />
                )}
            </div>
            <h3 className={`font-medium mb-1 ${isActive ? 'text-white' : 'text-slate-300'}`}>{title}</h3>
            <div className="flex justify-between items-center text-xs">
                <span className={`${isActive ? 'text-primary' : isDone ? 'text-emerald-400' : 'text-slate-500'}`}>
                    {isActive ? 'Processing...' : isDone ? 'Completed' : 'Pending'}
                </span>
                <span className="text-slate-500">{time}</span>
            </div>
        </div>
    );
};

const PipelineMonitor = () => {
    return (
        <div className="h-full flex flex-col gap-6 animate-in fade-in duration-500">
            <div>
                <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Pipeline Monitor</h1>
                <p className="text-slate-400">Visualizing real-time data ingestion and processing workflows.</p>
            </div>

            <div className="glass p-8 flex-1 flex flex-col justify-center relative overflow-hidden">
                {/* Background Grid Pattern */}
                <div className="absolute inset-0 border-white/[0.02] bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:40px_40px] pointer-events-none" />

                <h3 className="absolute top-6 left-6 text-sm font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                    <Activity size={16} className="text-primary" /> Active Job: Daily Analytics ETL
                </h3>

                <div className="relative max-w-5xl mx-auto w-full">
                    {/* Connecting Lines */}
                    <div className="absolute top-1/2 left-0 w-full h-1 -translate-y-1/2 bg-slate-800 z-0">
                        <div className="h-full w-[60%] bg-gradient-to-r from-emerald-500 to-primary relative shadow-[0_0_10px_#6366f1]">
                            <div className="absolute right-0 top-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full blur-sm opacity-50 animate-pulse"></div>
                        </div>
                    </div>

                    <div className="flex justify-between items-center relative z-10 gap-8 hide-scrollbar overflow-x-auto pb-4 pt-4">
                        <PipelineNode
                            title="Data Extraction"
                            status="done"
                            icon={UploadCloud}
                            time="12m 40s"
                        />

                        <ArrowRight className="text-emerald-400 shrink-0 mx-2" />

                        <PipelineNode
                            title="Schema Resolution"
                            status="done"
                            icon={Database}
                            time="4m 12s"
                        />

                        <ArrowRight className="text-emerald-400 shrink-0 mx-2" />

                        <PipelineNode
                            title="AI Structuring via LLM"
                            status="active"
                            icon={Cpu}
                            time="Running..."
                        />

                        <ArrowRight className="text-slate-600 shrink-0 mx-2" />

                        <PipelineNode
                            title="Load to OLAP"
                            status="pending"
                            icon={Save}
                            time="-"
                        />
                    </div>
                </div>

                <div className="absolute bottom-6 left-6 right-6 p-4 rounded-xl bg-[#0a0a14] border border-slate-800 flex items-center justify-between">
                    <div className="flex gap-4 font-mono text-xs">
                        <div className="flex items-center gap-2">
                            <span className="text-slate-500">Processed:</span>
                            <span className="text-primary font-bold">14.2 GB</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="text-slate-500">Rate:</span>
                            <span className="text-white">450 MB/s</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="text-slate-500">Errors:</span>
                            <span className="text-emerald-400 text-white">0</span>
                        </div>
                    </div>
                    <button className="text-xs bg-white/5 hover:bg-white/10 text-white px-3 py-1.5 rounded transition-colors border border-white/10">View Detailed Logs</button>
                </div>
            </div>
        </div>
    );
};

export default PipelineMonitor;
