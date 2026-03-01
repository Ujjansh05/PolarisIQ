import type { ReactNode } from 'react';
import Sidebar, { type PageId } from './Sidebar';
import Topbar from './Topbar';
import ParticleBackground from '../ui/ParticleBackground';

interface MainLayoutProps {
    children: ReactNode;
    currentPage: PageId;
    onNavigate: (page: PageId) => void;
}

const MainLayout = ({ children, currentPage, onNavigate }: MainLayoutProps) => {
    return (
        <div className="flex h-screen w-full bg-background overflow-hidden text-slate-100 relative">
            <ParticleBackground />

            <Sidebar currentPage={currentPage} onNavigate={onNavigate} />

            <div className="flex-1 flex flex-col h-full overflow-hidden relative z-0">
                <Topbar />

                <main className="flex-1 overflow-y-auto overflow-x-hidden p-6 scrollbar-hide">
                    <div className="max-w-7xl mx-auto w-full h-full">
                        {children}
                    </div>
                </main>
            </div>
        </div>
    );
};

export default MainLayout;
