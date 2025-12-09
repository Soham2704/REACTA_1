import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { FileText, CheckCircle2, AlertTriangle, Download, Activity } from 'lucide-react';
import Building3D from './Building3D';

const ReportView = ({ data, isLoading }) => {
    if (isLoading) {
        return (
            <div className="flex-1 flex flex-col items-center justify-center p-12 text-gray-500 animate-pulse">
                <div className="w-16 h-16 border-4 border-dark-accent border-t-transparent rounded-full animate-spin mb-4"></div>
                <p className="text-lg font-medium">Analyzing Regulations...</p>
                <p className="text-sm">Consulting GPT-4 & ChromaDB</p>
            </div>
        );
    }

    if (!data) {
        return (
            <div className="flex-1 flex flex-col items-center justify-center p-12 text-gray-500">
                <FileText size={64} className="mb-4 opacity-20" />
                <p className="text-lg">Select parameters and run the pipeline to see the analysis.</p>
            </div>
        );
    }

    const { entitlements, rl_decision, inputs } = data;
    // Handle low confidence/inactive agent
    const rawConfidence = rl_decision?.confidence_score || 0;
    const confidence = Math.round(rawConfidence * 100);
    const showConfidence = confidence > 10; // Only show if meaningful

    return (
        <div className="flex-1 p-8 overflow-y-auto ml-80">
            <div className="max-w-4xl mx-auto space-y-8">

                {/* Header Card */}
                <div className="glass-panel p-6 rounded-2xl flex items-center justify-between bg-gradient-to-br from-white/5 to-transparent">
                    <div>
                        <h1 className="text-2xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                            AI Analysis Report
                        </h1>
                        <p className="text-sm text-gray-400 mt-1">Project: {data.project_id} | Case: {data.case_id}</p>
                    </div>

                    {showConfidence && (
                        <div className="flex items-center gap-4">
                            <div className="text-right">
                                <p className="text-[10px] uppercase font-bold text-gray-500 mb-1">AI Confidence</p>
                                <div className="flex items-center gap-2">
                                    <div className="w-24 h-2 bg-gray-700 rounded-full overflow-hidden">
                                        <div className="h-full bg-dark-success transition-all duration-1000" style={{ width: `${confidence}%` }}></div>
                                    </div>
                                    <span className="text-dark-success font-bold">{confidence}%</span>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Main Content (Analysis Text) */}
                <div className="glass-panel p-8 rounded-2xl min-h-[500px]">
                    <article className="prose prose-invert max-w-none prose-tables:border-collapse prose-th:bg-white/10 prose-th:p-3 prose-td:p-3 prose-td:border-b prose-td:border-white/10">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {entitlements?.analysis_summary || "No detailed analysis available."}
                        </ReactMarkdown>
                    </article>
                </div>

                {/* 3D Visualization Section */}
                <div className="glass-panel p-1 rounded-2xl overflow-hidden shadow-2xl border border-white/10">
                    <Building3D
                        key={`${data.calculated_geometry?.width || 0}-${data.calculated_geometry?.height || 0}-${data.calculated_geometry?.depth || 0}`}
                        width={data.calculated_geometry?.width || 20}
                        depth={data.calculated_geometry?.depth || 20}
                        height={data.calculated_geometry?.height || 50}
                    />
                </div>

                {/* Legacy Download (Optional) */}
                {data.geometry_file && (
                    <div className="glass-panel p-6 rounded-2xl flex items-center justify-between opacity-60 hover:opacity-100 transition-opacity">
                        <div className="flex items-center gap-4">
                            <div className="w-8 h-8 bg-indigo-500/10 rounded-lg flex items-center justify-center text-indigo-400">
                                <Download size={16} />
                            </div>
                            <span className="text-sm text-gray-400">Original STL File</span>
                        </div>
                        <a href={`http://localhost:8000${data.geometry_file}`} download className="text-xs text-indigo-300 hover:text-indigo-200 hover:underline">Download</a>
                    </div>
                )}

            </div>
        </div>
    );
};

export default ReportView;
