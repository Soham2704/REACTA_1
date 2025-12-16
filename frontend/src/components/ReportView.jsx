import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import { FileText, CheckCircle2, AlertTriangle, Download, Activity } from 'lucide-react';
import Building3D from './Building3D';

const ReportView = ({ data, isLoading }) => {
    if (isLoading) {
        return (
            <div className="flex-1 flex flex-col items-center justify-center p-12 text-gray-500 animate-pulse h-screen">
                <div className="relative w-24 h-24 mb-6">
                    <div className="absolute inset-0 border-4 border-indigo-500/20 rounded-full animate-ping"></div>
                    <div className="absolute inset-0 border-4 border-t-indigo-500 rounded-full animate-spin"></div>
                </div>
                <p className="text-xl font-medium text-indigo-300">Analyzing Regulations...</p>
                <p className="text-sm text-gray-400 mt-2">Consulting GPT-4 & ChromaDB Neural Engine</p>
            </div>
        );
    }

    if (!data) {
        return (
            <div className="flex-1 flex flex-col items-center justify-center p-12 text-gray-500 h-screen">
                <div className="w-20 h-20 bg-white/5 rounded-2xl flex items-center justify-center mb-6 backdrop-blur-sm border border-white/10">
                    <FileText size={40} className="text-gray-600" />
                </div>
                <p className="text-xl font-light text-gray-300">Ready to Analyze</p>
                <p className="text-sm text-gray-500 mt-2">Select parameters and run the investigation pipeline.</p>
            </div>
        );
    }

    const { entitlements, rl_decision, inputs } = data;
    const rawConfidence = rl_decision?.confidence_score || 0;
    const confidence = Math.round(rawConfidence * 100);
    const showConfidence = confidence > 10;

    return (
        <div className="flex-1 p-12 overflow-y-auto min-h-screen text-gray-200 font-sans relative z-10 selection:bg-indigo-500/30">

            <div className="max-w-4xl mx-auto space-y-24">

                {/* Minimalist Header */}
                <div className="flex items-end justify-between border-b border-white/10 pb-8 mt-12 text-center md:text-left">
                    <div>
                        <p className="text-[10px] uppercase tracking-[0.4em] text-gray-500 mb-4 font-mono">Veritas Intelligence Output</p>
                        <h1 className="text-7xl font-normal text-white tracking-tighter">
                            {data.project_id}
                        </h1>
                        <div className="flex items-center gap-4 mt-2 text-gray-500 font-light">
                            <span>{data.city}</span>
                            <span className="text-white/10">|</span>
                            <span className="font-mono text-xs uppercase tracking-widest">{data.case_id}</span>
                        </div>
                    </div>

                    {showConfidence && (
                        <div className="text-right hidden md:block border-l border-white/10 pl-8">
                            <p className="text-[10px] uppercase tracking-[0.2em] text-gray-500 mb-1 font-mono">AI Confidence</p>
                            <div className="flex items-baseline justify-end gap-2">
                                <span className="text-5xl font-light text-white tracking-tighter">{confidence}%</span>
                                <span className="text-xs text-green-400 font-mono uppercase tracking-wider">High Fidelity</span>
                            </div>
                        </div>
                    )}
                </div>

                {/* --- COMPARATIVE VALUE DASHBOARD (HACKATHON WOW FEATURE) --- */}
                {data.comparative_analysis && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-fade-in-up">
                        {/* Baseline Card */}
                        <div className="md:col-span-1 p-6 rounded-xl border border-white/5 bg-white/5 backdrop-blur-sm grayscale opacity-70">
                            <div className="flex items-center gap-2 mb-4 text-gray-400">
                                <Activity size={16} />
                                <span className="text-xs uppercase tracking-widest font-mono">Baseline (Traditional)</span>
                            </div>
                            <div className="space-y-1">
                                <p className="text-2xl font-light text-white">₹{data.comparative_analysis.baseline.estimated_profit?.toLocaleString()}</p>
                                <p className="text-xs text-gray-500 font-mono">
                                    FSI {data.comparative_analysis.baseline.fsi} • {data.comparative_analysis.baseline.bua?.toLocaleString()} sq.m
                                </p>
                            </div>
                        </div>

                        {/* Optimized Card */}
                        <div className="md:col-span-2 p-6 rounded-xl border border-indigo-500/30 bg-gradient-to-br from-indigo-900/20 to-purple-900/20 backdrop-blur-md relative overflow-hidden group">
                            <div className="absolute top-0 right-0 p-4 opacity-50">
                                <span className="text-[10px] uppercase tracking-widest text-indigo-300 font-mono border border-indigo-500/30 px-2 py-1 rounded">AI Optimized</span>
                            </div>

                            <div className="grid grid-cols-2 gap-8 relative z-10">
                                <div>
                                    <div className="flex items-center gap-2 mb-4 text-indigo-300">
                                        <Activity size={16} />
                                        <span className="text-xs uppercase tracking-widest font-mono">Veritas Strategy</span>
                                    </div>
                                    <div className="space-y-1">
                                        <p className="text-4xl font-normal text-white tracking-tight">₹{data.comparative_analysis.optimized.estimated_profit?.toLocaleString()}</p>
                                        <p className="text-sm text-indigo-200/60 font-mono">
                                            FSI {data.comparative_analysis.optimized.fsi} • {data.comparative_analysis.optimized.bua?.toLocaleString()} sq.m
                                        </p>
                                    </div>
                                </div>

                                <div className="border-l border-white/10 pl-8 flex flex-col justify-center">
                                    <p className="text-xs uppercase tracking-widest text-green-400 mb-2 font-mono">Value Unlocked</p>
                                    <p className="text-3xl font-light text-green-400">+ ₹{data.comparative_analysis.value_add?.toLocaleString()}</p>
                                    <p className="text-xs text-gray-400 mt-1">
                                        {data.comparative_analysis.roi_increase_percent}% Increase in Profitability
                                    </p>
                                </div>
                            </div>

                            {/* Subtle Glow Effect */}
                            <div className="absolute -bottom-20 -right-20 w-64 h-64 bg-indigo-500/20 rounded-full blur-[80px] group-hover:bg-indigo-500/30 transition-all duration-700"></div>
                        </div>
                    </div>
                )}
                <article className="prose prose-invert prose-xl max-w-none 
                    prose-headings:font-normal prose-headings:tracking-wide prose-headings:text-white 
                    prose-p:text-gray-400 prose-p:font-light prose-p:leading-loose
                    prose-strong:text-white prose-strong:font-medium
                    prose-li:text-gray-400
                    prose-code:text-gray-300 prose-code:bg-white/5 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:before:content-none prose-code:after:content-none
                ">
                    <ReactMarkdown
                        remarkPlugins={[remarkGfm, remarkMath]}
                        rehypePlugins={[rehypeKatex]}
                        components={{
                            // Custom "Veritas" minimalist tables
                            table: ({ node, ...props }) => <div className="my-12 overflow-hidden"><table className="w-full text-left text-base border-t border-b border-white/10" {...props} /></div>,
                            thead: ({ node, ...props }) => <thead className="uppercase text-[10px] tracking-[0.2em] text-gray-500 font-medium font-mono" {...props} />,
                            th: ({ node, ...props }) => <th className="py-6 pr-8 font-normal" {...props} />,
                            td: ({ node, ...props }) => <td className="py-6 pr-8 border-t border-white/5 text-gray-300 font-light" {...props} />,
                            // "Cinematic" Quotes
                            blockquote: ({ node, ...props }) => (
                                <div className="border-l-2 border-white pl-8 py-2 my-12 italic text-2xl text-gray-300 font-light leading-relaxed">
                                    {props.children}
                                </div>
                            ),
                            h1: ({ node, ...props }) => <h1 className="text-4xl font-normal text-white mb-8 mt-16 tracking-wide border-b border-white/10 pb-4" {...props} />,
                            h2: ({ node, ...props }) => <h2 className="text-3xl font-light text-white mb-6 mt-12 tracking-wide" {...props} />,
                            h3: ({ node, ...props }) => <h3 className="text-xl font-normal text-white/80 mb-4 mt-8 uppercase tracking-[0.2em] text-xs font-mono" {...props} />,
                        }}
                    >
                        {entitlements?.analysis_summary || "No detailed analysis available."}
                    </ReactMarkdown>
                </article>

                {/* Cinematic 3D Footer */}
                <div className="pt-12 border-t border-white/5">
                    <div className="flex justify-between items-end mb-8">
                        <h2 className="text-xl font-light text-white tracking-[0.2em] uppercase">Spatial Visualization</h2>
                        {data.geometry_file && (
                            <a href={`http://localhost:8000${data.geometry_file}`} download className="text-[10px] uppercase tracking-widest text-gray-500 hover:text-white transition-colors cursor-pointer border border-white/10 px-4 py-2 hover:bg-white/5">
                                Download Geometry
                            </a>
                        )}
                    </div>

                    <div className="w-full h-[600px] border border-white/5 bg-[#050505] relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-4 z-10 text-right opacity-50 group-hover:opacity-100 transition-opacity">
                            <p className="font-mono text-[10px] text-white/50 tracking-widest">INTERACTIVE PREVIEW</p>
                        </div>
                        <Building3D
                            key={`${data.calculated_geometry?.width || 0}-${data.calculated_geometry?.height || 0}-${data.calculated_geometry?.depth || 0}`}
                            width={data.calculated_geometry?.width || 20}
                            depth={data.calculated_geometry?.depth || 20}
                            height={data.calculated_geometry?.height || 50}
                        />
                    </div>
                </div>

            </div>
        </div>
    );
};

export default ReportView;
