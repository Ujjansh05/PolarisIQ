import { useState, useEffect } from 'react';
import { Search, Sparkles, Wifi, WifiOff } from 'lucide-react';
import { fetchHealth } from '../../services/api';

const Topbar = () => {
    const [isOnline, setIsOnline] = useState(false);
    const [uptime, setUptime] = useState('');

    useEffect(() => {
        const checkHealth = () => {
            fetchHealth()
                .then(h => {
                    setIsOnline(true);
                    const s = h.uptime_seconds;
                    if (s < 60) setUptime(`${Math.round(s)}s`);
                    else if (s < 3600) setUptime(`${Math.round(s / 60)}m`);
                    else setUptime(`${Math.round(s / 3600)}h`);
                })
                .catch(() => setIsOnline(false));
        };

        checkHealth();
        const interval = setInterval(checkHealth, 10000);
        return () => clearInterval(interval);
    }, []);

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
                        placeholder="Ask PolarisIQ (switch to Query Studio)"
                    />
                    <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                        <div className="flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium text-slate-400 bg-white/5 border border-white/10 shadow-sm">
                            <Sparkles className="w-3 h-3 text-secondary" /> AI
                        </div>
                    </div>
                </div>
            </div>

            <div className="flex items-center gap-4 ml-6">
                {/* Backend Status */}
                <div className={`flex items-center gap-2 text-xs px-3 py-1.5 rounded-full border ${
                    isOnline
                        ? 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20'
                        : 'text-rose-400 bg-rose-400/10 border-rose-400/20'
                }`}>
                    {isOnline ? <Wifi size={12} /> : <WifiOff size={12} />}
                    <span className="font-medium">{isOnline ? 'Connected' : 'Offline'}</span>
                    {isOnline && uptime && (
                        <span className="text-emerald-400/60 ml-1">{uptime}</span>
                    )}
                </div>

                <div className="flex items-center gap-3 pl-4 border-l border-cardBorder">
                    <div className="text-right hidden sm:block">
                        <p className="text-sm font-medium text-slate-200 leading-none">Local User</p>
                        <p className="text-xs text-slate-500 mt-1">PolarisIQ Engine</p>
                    </div>
                    <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-primary to-secondary p-[2px] shadow-neon">
                        <div className="w-full h-full rounded-full border-2 border-background overflow-hidden bg-card flex items-center justify-center">
                            <span className="text-xs font-bold text-white">P</span>
                        </div>
                    </div>
                </div>
            </div>
        </header>
    );
};

export default Topbar;
