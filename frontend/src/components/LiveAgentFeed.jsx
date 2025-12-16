import React, { useEffect, useState, useRef } from 'react';
import { Terminal, Cpu, Database, Brain, CheckCircle2 } from 'lucide-react';

const generateLogs = (params) => [
    { type: 'sys', text: "Initializing Veritas Multi-Agent Swarm...", delay: 500 },
    { type: 'info', text: `Ingesting Plot Parameters: ${params?.plot_size || 0}sqm, Road ${params?.road_width || 0}m.`, delay: 1000 },
    { type: 'rag', text: "Accessing VectorDB (Chroma)... Searching 'DCPR 2034 FSI Rules'...", delay: 1800 },
    { type: 'rag', text: "Found 5 Relevant Regulation Chunks (Score: 0.89).", delay: 2800 },
    { type: 'llm', text: "LLM extracting specific constraints from Page 45, 87...", delay: 3800 },
    { type: 'rl', text: "RL Agent 'Policy_Pro' Activated.", delay: 4500 },
    { type: 'rl', text: `Observation State: [${params?.plot_size}.0, 1.0, ${params?.road_width}.0]`, delay: 5000 },
    { type: 'rl', text: "Policy Network Evaluating 5 Development Strategies...", delay: 6000 },
    { type: 'rl', text: ">>> OPTIMAL ACTION: HIGH DENSITY (Confidence 90%)", delay: 7000 },
    { type: 'sys', text: "Synthesizing Final Compliance Report...", delay: 8000 },
    { type: 'success', text: "Pipeline Execution Complete. Generating 3D Geometry.", delay: 9000 },
];

const LiveAgentFeed = ({ isRunning, params }) => {
    const [logs, setLogs] = useState([]);
    const scrollRef = useRef(null);

    // Auto-scroll to bottom
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [logs]);

    useEffect(() => {
        if (!isRunning) return;

        setLogs([]); // Clear logs on start
        const timeouts = [];
        const sequence = generateLogs(params);

        sequence.forEach((log) => {
            const t = setTimeout(() => {
                setLogs(prev => [...prev, log]);
            }, log.delay);
            timeouts.push(t);
        });

        return () => timeouts.forEach(clearTimeout);
    }, [isRunning, params]);

    const getIcon = (type) => {
        switch (type) {
            case 'rag': return <Database size={12} className="text-yellow-500" />;
            case 'llm': return <Cpu size={12} className="text-blue-400" />;
            case 'rl': return <Brain size={12} className="text-purple-400" />;
            case 'success': return <CheckCircle2 size={12} className="text-green-400" />;
            default: return <Terminal size={12} className="text-gray-500" />;
        }
    };

    const getColor = (type) => {
        switch (type) {
            case 'rag': return "text-yellow-200/80";
            case 'llm': return "text-blue-200/80";
            case 'rl': return "text-purple-300 font-bold";
            case 'success': return "text-green-400 font-bold drop-shadow-[0_0_8px_rgba(74,222,128,0.6)]";
            default: return "text-gray-400";
        }
    };

    // Special Highlighter for the "Optimal Action" log
    const getExtraStyle = (text) => {
        if (text.includes("OPTIMAL ACTION")) return "text-cyan-400 font-black tracking-wide drop-shadow-[0_0_10px_rgba(34,211,238,0.8)] text-sm py-1";
        return "";
    };

    return (
        <div className="bg-black/40 border-t border-white/10 p-4 h-64 overflow-hidden flex flex-col font-mono text-xs">
            <div className="flex items-center gap-2 mb-3 opacity-50 uppercase tracking-widest text-[10px] text-gray-500">
                <Terminal size={12} />
                <span>Live Agent Log</span>
            </div>

            <div ref={scrollRef} className="flex-1 overflow-y-auto space-y-2 scrollbar-hide">
                {logs.length === 0 && !isRunning && (
                    <div className="text-gray-600 italic">State: Idle. Waiting for case injection...</div>
                )}

                {logs.map((log, i) => (
                    <div key={i} className={`flex items-start gap-3 animate-fade-in ${getColor(log.type)} ${getExtraStyle(log.text)}`}>
                        <div className="mt-0.5 opacity-70">{getIcon(log.type)}</div>
                        <span>{log.text}</span>
                    </div>
                ))}

                {isRunning && (
                    <div className="flex items-center gap-2 text-gray-500 animate-pulse">
                        <div className="w-1 h-4 bg-indigo-500"></div>
                        <span>Processing...</span>
                    </div>
                )}
            </div>
        </div>
    );
};

export default LiveAgentFeed;
