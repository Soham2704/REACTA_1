import React, { useState, useEffect } from 'react';
import { Building2, MapPin, Ruler, Activity, Settings, Play } from 'lucide-react';

const Sidebar = ({ onRun, isRunning }) => {
    const [params, setParams] = useState({
        city: 'Mumbai',
        plot_size: 2000,
        road_width: 20.0,
        location: 'Island City',
        zoning: 'Residential (R-Zone)',
        proposed_use: 'Residential Building',
        building_height: 15.0,
        asr_rate: 0,
        plot_deductions: 0
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setParams(prev => ({
            ...prev,
            [name]: parseFloat(value) || value // Basic parsing, improve for strings
        }));
    };

    const handleRun = () => {
        // Construct payload structure expected by backend
        const payload = {
            project_id: "react_web_prj_01",
            case_id: `case_${Date.now()}`,
            city: params.city,
            document: "io/DCPR_2034.pdf", // Default for now
            parameters: {
                ...params
            }
        };
        onRun(payload);
    };

    return (
        <div className="w-80 h-screen glass-panel flex flex-col p-6 overflow-y-auto fixed left-0 top-0 z-20">
            <div className="flex items-center gap-3 mb-8">
                <Activity className="text-dark-accent w-6 h-6" />
                <h1 className="text-xl font-bold tracking-tight">Compliance AI</h1>
            </div>

            <div className="space-y-6 flex-1">
                {/* Section: Basic Params */}
                <div className="space-y-4">
                    <h2 className="text-xs uppercase text-gray-500 font-semibold tracking-wider">Site Parameters</h2>

                    <div className="space-y-1">
                        <label className="text-xs text-gray-400">City</label>
                        <select name="city" value={params.city} onChange={handleChange} className="glass-input w-full bg-dark-card">
                            <option>Mumbai</option>
                            <option>Pune</option>
                            <option>Nashik</option>
                        </select>
                    </div>

                    <div className="space-y-1">
                        <label className="text-xs text-gray-400 flex items-center gap-1"><Ruler size={12} /> Plot Size (sq.m)</label>
                        <input type="number" name="plot_size" value={params.plot_size} onChange={handleChange} className="glass-input w-full" />
                    </div>

                    <div className="space-y-1">
                        <label className="text-xs text-gray-400 flex items-center gap-1"><Building2 size={12} /> Road Width (m)</label>
                        <input type="number" name="road_width" value={params.road_width} onChange={handleChange} className="glass-input w-full" />
                    </div>

                    <div className="space-y-1">
                        <label className="text-xs text-gray-400 flex items-center gap-1"><MapPin size={12} /> Location Type</label>
                        <select name="location" value={params.location} onChange={handleChange} className="glass-input w-full bg-dark-card">
                            <option>Island City</option>
                            <option>Suburbs</option>
                            <option>Extended Suburbs</option>
                        </select>
                    </div>
                </div>

                {/* Section: Detailed Params */}
                <div className="space-y-4 pt-4 border-t border-white/5">
                    <h2 className="text-xs uppercase text-gray-500 font-semibold tracking-wider">Detailed Specs</h2>

                    <div className="space-y-1">
                        <label className="text-xs text-gray-400">Zoning</label>
                        <select name="zoning" value={params.zoning} onChange={handleChange} className="glass-input w-full bg-dark-card">
                            <option>Residential (R-Zone)</option>
                            <option>Commercial (C-Zone)</option>
                            <option>Industrial (I-Zone)</option>
                        </select>
                    </div>

                    <div className="space-y-1">
                        <label className="text-xs text-gray-400">Proposed Use</label>
                        <select name="proposed_use" value={params.proposed_use} onChange={handleChange} className="glass-input w-full bg-dark-card">
                            <option>Residential Building</option>
                            <option>Commercial Office</option>
                            <option>IT Park</option>
                            <option>Hospital</option>
                        </select>
                    </div>

                    <div className="space-y-1">
                        <label className="text-xs text-gray-400">Building Height (m)</label>
                        <input type="number" name="building_height" value={params.building_height} onChange={handleChange} className="glass-input w-full" />
                    </div>
                </div>

                {/* Section: Advanced */}
                <div className="space-y-4 pt-4 border-t border-white/5">
                    <h2 className="text-xs uppercase text-gray-500 font-semibold tracking-wider flex items-center gap-2"><Settings size={12} /> Advanced</h2>
                    <div className="grid grid-cols-2 gap-2">
                        <div className="space-y-1">
                            <label className="text-[10px] text-gray-400">ASR (₹/sq.m)</label>
                            <input type="number" name="asr_rate" value={params.asr_rate} onChange={handleChange} className="glass-input w-full text-xs" />
                        </div>
                        <div className="space-y-1">
                            <label className="text-[10px] text-gray-400">Deductions (sq.m)</label>
                            <input type="number" name="plot_deductions" value={params.plot_deductions} onChange={handleChange} className="glass-input w-full text-xs" />
                        </div>
                    </div>
                </div>
            </div>

            <div className="pt-6">
                <button
                    onClick={handleRun}
                    disabled={isRunning}
                    className={`w-full glass-button flex items-center justify-center gap-2 ${isRunning ? 'bg-gray-600 cursor-not-allowed' : 'bg-dark-accent hover:bg-indigo-600 shadow-lg shadow-indigo-500/20'}`}
                >
                    {isRunning ? <span className="animate-pulse">Analyzing...</span> : <><Play size={16} fill="currentColor" /> Run Pipeline</>}
                </button>
            </div>
        </div>
    );
};

export default Sidebar;
