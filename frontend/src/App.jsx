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
    // Replaced bg-dark-bg with transparent to let global gradient show
    <div className="flex min-h-screen text-gray-100 font-sans selection:bg-purple-500 selection:text-white overflow-hidden">
      <Sidebar onRun={handleRunPipeline} isRunning={loading} />
      <main className="flex-1 relative z-10 flex flex-col h-screen overflow-hidden">
        {/* Top padding to account for layout spacing if needed */}
        <div className="flex-1 overflow-y-auto w-full">
          <ReportView data={report} isLoading={loading} />
          <FeedbackWidget reportData={report} />
        </div>
      </main>

      {/* Cosmic Background Ambience (ExamAi/Space Style) */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-[-20%] right-[-10%] w-[800px] h-[800px] bg-purple-900/20 rounded-full blur-[120px] mix-blend-screen animate-pulse-slow"></div>
        <div className="absolute bottom-[-20%] left-[-10%] w-[600px] h-[600px] bg-indigo-900/20 rounded-full blur-[100px] mix-blend-screen"></div>

        {/* Subtle Stars/Noise */}
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 brightness-150 contrast-150"></div>
      </div>
    </div>
  );
}

export default App;
