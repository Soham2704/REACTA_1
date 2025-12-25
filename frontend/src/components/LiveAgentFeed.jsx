import React, { useEffect, useState, useRef } from 'react';
import { Terminal, Cpu, Database, Brain, CheckCircle2 } from 'lucide-react';

const WEBSOCKET_URL = "ws://localhost:8000/ws/logs";

const LiveAgentFeed = ({ isRunning, params }) => {
    const [logs, setLogs] = useState([]);
    const scrollRef = useRef(null);

    // Auto-scroll to bottom
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [logs]);

    const [status, setStatus] = useState('Disconnected');

    useEffect(() => {
        // Always keep the socket open to receive broadcasts
        const ws = new WebSocket(WEBSOCKET_URL);

        ws.onopen = () => {
            setStatus('Connected');
            setLogs(prev => [...prev, { type: 'sys', text: ">> Connected to Veritas Core System", delay: 0 }]);
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                // Only show relevant logs
                setLogs(prev => [...prev, data]);
            } catch (err) {
                console.error("Log parse error", err);
            }
        };

        ws.onclose = () => setStatus('Disconnected');
        ws.onerror = (err) => {
            setStatus('Error');
            console.error("WS Error", err);
        };

        return () => ws.close();
    }, []);

    // Clear logs only when a NEW run starts, but keep the connection
    useEffect(() => {
        if (isRunning) {
            setLogs([{ type: 'sys', text: ">> Initialization Sequence Started...", delay: 0 }]);
        }
    }, [isRunning]);

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
            <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2 opacity-50 uppercase tracking-widest text-[10px] text-gray-500">
                    <Terminal size={12} />
                    <span>Live Agent Log</span>
                </div>
                <div className="flex items-center gap-1.5">
                    <div className={`w-1.5 h-1.5 rounded-full ${status === 'Connected' ? 'bg-green-500 shadow-[0_0_5px_rgba(34,197,94,0.6)]' : 'bg-red-500'}`}></div>
                    <span className="text-[9px] uppercase tracking-wider text-gray-600 font-mono">{status}</span>
                </div>
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
