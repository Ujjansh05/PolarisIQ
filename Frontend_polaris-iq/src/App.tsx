import { useState } from 'react';
import MainLayout from './components/layout/MainLayout';
import type { PageId } from './components/layout/Sidebar';
import HomeDashboard from './components/pages/HomeDashboard';
import QueryStudio from './components/pages/QueryStudio';
import DataWorkspace from './components/pages/DataWorkspace';
import InsightsPage from './components/pages/InsightsPage';
import PipelineMonitor from './components/pages/PipelineMonitor';

function App() {
  const [currentPage, setCurrentPage] = useState<PageId>('home');

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
