import { Bell, Search, Sparkles } from 'lucide-react';

const Topbar = () => {
    return (
        <header className="h-16 flex items-center justify-between px-8 bg-background/50 backdrop-blur-md border-b border-cardBorder sticky top-0 z-10 w-full">
            <div className="flex-1 max-w-xl">
                <div className="relative group">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <Search className="h-4 w-4 text-slate-400 group-focus-within:text-primary transition-colors" />
                    </div>
                    <input
                        type="text"
                        className="block w-full pl-10 pr-3 py-2 border border-cardBorder rounded-lg leading-5 bg-card/50 text-slate-300 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary focus:bg-card transition-all sm:text-sm glow-focus"
                        placeholder="Ask PolarisIQ (e.g. 'Show anomaly detection for Q3')"
                    />
                    <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                        <div className="flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium text-slate-400 bg-white/5 border border-white/10 shadow-sm">
                            <Sparkles className="w-3 h-3 text-secondary" /> AI
                        </div>
                    </div>
                </div>
            </div>

            <div className="flex items-center gap-4 ml-6">
                <button className="relative p-2 text-slate-400 hover:text-white transition-colors">
                    <Bell className="w-5 h-5" />
                    <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-rose-500 rounded-full shadow-[0_0_8px_#f43f5e]"></span>
                </button>

                <div className="flex items-center gap-3 pl-4 border-l border-cardBorder">
                    <div className="text-right hidden sm:block">
                        <p className="text-sm font-medium text-slate-200 leading-none">Alex Mercer</p>
                        <p className="text-xs text-slate-500 mt-1">Lead Data Scientist</p>
                    </div>
                    <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-primary to-secondary p-[2px] shadow-neon">
                        <div className="w-full h-full rounded-full border-2 border-background overflow-hidden bg-card flex items-center justify-center">
                            <span className="text-xs font-bold text-white">AM</span>
                        </div>
                    </div>
                </div>
            </div>
        </header>
    );
};

export default Topbar;
