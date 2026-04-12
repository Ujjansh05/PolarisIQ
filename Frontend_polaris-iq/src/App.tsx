import { useState } from 'react';
import MainLayout from './components/layout/MainLayout';
import type { PageId } from './components/layout/Sidebar';
import HomeDashboard from './components/pages/HomeDashboard';
import QueryStudio from './components/pages/QueryStudio';
import DataWorkspace from './components/pages/DataWorkspace';
import InsightsPage from './components/pages/InsightsPage';
import PipelineMonitor from './components/pages/PipelineMonitor';
import LandingPage from './components/pages/LandingPage';

const LANDING_VISITED_KEY = 'polarisiq_landing_visited_v1';

function App() {
  const [currentPage, setCurrentPage] = useState<PageId>('home');
  const [showLanding, setShowLanding] = useState(() => !localStorage.getItem(LANDING_VISITED_KEY));

  const handleEnterApp = (page: PageId = 'home') => {
    setCurrentPage(page);
    setShowLanding(false);
    localStorage.setItem(LANDING_VISITED_KEY, '1');
  };

  if (showLanding) {
    return <LandingPage onEnter={handleEnterApp} />;
  }

  return (
    <MainLayout currentPage={currentPage} onNavigate={setCurrentPage}>
      {currentPage === 'home' && <HomeDashboard />}
      {currentPage === 'query' && <QueryStudio />}
      {currentPage === 'workspace' && <DataWorkspace />}
      {currentPage === 'insights' && <InsightsPage />}
      {currentPage === 'pipeline' && <PipelineMonitor />}
    </MainLayout>
  );
}

export default App;
