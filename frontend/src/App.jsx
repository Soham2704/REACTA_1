import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import ReportView from './components/ReportView';
import FeedbackWidget from './components/FeedbackWidget';
import { runPipeline } from './api';

function App() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleRunPipeline = async (payload) => {
    setLoading(true);
    setReport(null); // Clear previous
    try {
      const result = await runPipeline(payload);
      setReport(result);
    } catch (error) {
      alert("Failed to run pipeline. Check console.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex bg-dark-bg min-h-screen text-gray-100 font-sans selection:bg-dark-accent selection:text-white">
      <Sidebar onRun={handleRunPipeline} isRunning={loading} />
      <main className="flex-1 relative">
        <ReportView data={report} isLoading={loading} />
        <FeedbackWidget reportData={report} />
      </main>

      {/* Background Decor */}
      <div className="fixed top-0 left-0 w-full h-full pointer-events-none z-[-1] opacity-30">
        <div className="absolute top-[-10%] right-[-5%] w-[500px] h-[500px] bg-indigo-600/20 rounded-full blur-[128px]"></div>
        <div className="absolute bottom-[-10%] left-[20%] w-[400px] h-[400px] bg-emerald-600/10 rounded-full blur-[128px]"></div>
      </div>
    </div>
  );
}

export default App;
