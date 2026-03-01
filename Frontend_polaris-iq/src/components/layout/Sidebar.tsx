import { Activity, Database, LayoutDashboard, MessageSquare, Settings, Zap } from 'lucide-react';
import { cn } from '../../lib/utils'; // We'll create a simple utli if shadcn failed to generate it

export type PageId = 'home' | 'query' | 'workspace' | 'insights' | 'pipeline';

interface SidebarProps {
    currentPage: PageId;
    onNavigate: (page: PageId) => void;
}

const navItems = [
    { id: 'home', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'query', label: 'AI Query Studio', icon: MessageSquare },
    { id: 'workspace', label: 'Data Workspace', icon: Database },
    { id: 'insights', label: 'Insights', icon: Zap },
    { id: 'pipeline', label: 'Pipeline Monitor', icon: Activity },
];

const Sidebar = ({ currentPage, onNavigate }: SidebarProps) => {
    return (
        <aside className="w-64 glass border-r-0 border-y-0 rounded-none rounded-r-2xl flex-shrink-0 flex flex-col h-full overflow-hidden transition-all duration-300">
            <div className="p-6 flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center shadow-neon">
                    <div className="w-3 h-3 bg-white rounded-full"></div>
                </div>
                <h1 className="text-xl font-bold tracking-tight text-white flex items-center">
                    Polaris<span className="text-primary font-black">IQ</span>
                </h1>
            </div>

            <nav className="flex-1 px-4 py-8 space-y-2">
                {navItems.map((item) => {
                    const isActive = currentPage === item.id;
                    const Icon = item.icon;

                    return (
                        <button
                            key={item.id}
                            onClick={() => onNavigate(item.id as PageId)}
                            className={cn(
                                "w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-300 group relative",
                                isActive
                                    ? "text-white bg-primary/10 shadow-[inset_0_0_20px_rgba(99,102,241,0.1)]"
                                    : "text-slate-400 hover:text-white hover:bg-white/5"
                            )}
                        >
                            {isActive && (
                                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-primary rounded-r-md shadow-[0_0_10px_#6366f1]"></div>
                            )}
                            <Icon
                                size={20}
                                className={cn(
                                    "transition-colors duration-300",
                                    isActive ? "text-primary drop-shadow-[0_0_8px_rgba(99,102,241,0.8)]" : "group-hover:text-primary/70"
                                )}
                            />
                            <span className="font-medium text-sm">{item.label}</span>
                        </button>
                    )
                })}
            </nav>

            <div className="p-4 mt-auto">
                <button className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-all">
                    <Settings size={20} />
                    <span className="font-medium text-sm">Settings</span>
                </button>
            </div>
        </aside>
    );
};

export default Sidebar;
