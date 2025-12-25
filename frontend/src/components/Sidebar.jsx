import React, { useState, useEffect } from 'react';
import { Building2, MapPin, Ruler, Activity, Settings, Play, Hexagon } from 'lucide-react';
import LiveAgentFeed from './LiveAgentFeed';

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

    // Dynamic Location Options based on City
    const CITY_LOCATIONS = {
        'Mumbai': ['Island City', 'Suburbs', 'Extended Suburbs'],
        'Pune': ['Congested Area', 'Non-Congested Area', 'Developing Area'],
        'Nashik': ['Gaothan', 'Non-Gaothan', 'Town Planning Scheme'],
        'Delhi': ['Zone A (Walled City)', 'Zone B (Karol Bagh)', 'Zone C (Civil Lines)', 'Zone D (New Delhi)', 'General (Other Zones)']
    };

    const handleChange = (e) => {
        const { name, value } = e.target;

        // Special handling for City change to reset Location
        if (name === 'city') {
            const newLocations = CITY_LOCATIONS[value] || [];
            setParams(prev => ({
                ...prev,
                city: value,
                location: newLocations[0] || 'General' // Default to first proper location
            }));
        } else {
            setParams(prev => ({
                ...prev,
                [name]: parseFloat(value) || value
            }));
        }
    };

    const handleRun = () => {
        const payload = {
            project_id: "VERITAS-1",
            case_id: `case_${Date.now()}`,
            city: params.city,
            document: "io/DCPR_2034.pdf",
            parameters: { ...params }
        };
        onRun(payload);
    };

    return (
        <div className="w-80 h-screen flex flex-col relative z-20 glass-sidebar">
            {/* Branding Header */}
            <div className="p-8 pb-8 pt-10">
                <div className="flex items-center gap-3 mb-2">
                    <div className="relative w-8 h-8 flex items-center justify-center bg-gradient-to-br from-violet-600 to-indigo-600 rounded-lg shadow-lg shadow-purple-500/20">
                        <Hexagon size={18} className="text-white" strokeWidth={2.5} />
                    </div>
                    <h1 className="text-2xl font-bold text-white tracking-wider font-sans">VERITAS</h1>
                </div>
                <p className="text-[10px] text-purple-200/60 font-mono tracking-widest uppercase pl-11">AI Compliance Engine</p>
            </div>

            <div className="space-y-6 flex-1 overflow-y-auto px-6 py-4 custom-scrollbar">
                {/* Section: Basic Params */}
                <div className="space-y-4">
                    <h2 className="text-sm uppercase text-purple-300/80 font-bold tracking-widest mb-4">Site Parameters</h2>

                    <div className="space-y-1.5">
                        <label className="text-sm text-gray-300 font-medium ml-1">City Context</label>
                        <div className="relative">
                            <MapPin size={14} className="absolute left-3 top-3.5 text-gray-500" />
                            <select name="city" value={params.city} onChange={handleChange} className="glass-input w-full pl-9 py-2.5 text-sm appearance-none cursor-pointer hover:bg-white/10 transition-colors">
                                <option className="bg-[#1a103c]">Mumbai</option>
                                <option className="bg-[#1a103c]">Pune</option>
                                <option className="bg-[#1a103c]">Nashik</option>
                                <option className="bg-[#1a103c]">Delhi</option>
                            </select>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                        <div className="space-y-1.5">
                            <label className="text-sm text-gray-300 font-medium ml-1">Plot Area (m²)</label>
                            <input type="number" name="plot_size" value={params.plot_size} onChange={handleChange} className="glass-input w-full py-2.5 text-sm" />
                        </div>
                        <div className="space-y-1.5">
                            <label className="text-sm text-gray-300 font-medium ml-1">Road Width</label>
                            <input type="number" name="road_width" value={params.road_width} onChange={handleChange} className="glass-input w-full py-2.5 text-sm" />
                        </div>
                    </div>

                    <div className="space-y-1.5">
                        <label className="text-sm text-gray-300 font-medium ml-1">Zone Location</label>
                        <div className="relative">
                            <Activity size={14} className="absolute left-3 top-3.5 text-gray-500" />
                            <select name="location" value={params.location} onChange={handleChange} className="glass-input w-full pl-9 py-2.5 text-sm appearance-none hover:bg-white/10 transition-colors">
                                {CITY_LOCATIONS[params.city]?.map(loc => (
                                    <option key={loc} value={loc} className="bg-[#1a103c]">{loc}</option>
                                ))}
                            </select>
                        </div>
                    </div>
                </div>

                {/* Section: Detailed Params */}
                <div className="space-y-4 pt-4 border-t border-white/5">
                    <h2 className="text-sm uppercase text-purple-300/80 font-bold tracking-widest mb-4">Project Specs</h2>

                    <div className="space-y-1.5">
                        <label className="text-sm text-gray-300 font-medium ml-1">Zoning Type</label>
                        <select name="zoning" value={params.zoning} onChange={handleChange} className="glass-input w-full py-2.5 text-sm bg-transparent hover:bg-white/10 transition-colors">
                            <option className="bg-[#1a103c]">Residential (R-Zone)</option>
                            <option className="bg-[#1a103c]">Commercial (C-Zone)</option>
                            <option className="bg-[#1a103c]">Industrial (I-Zone)</option>
                        </select>
                    </div>

                    <div className="space-y-1.5">
                        <label className="text-sm text-gray-300 font-medium ml-1">Proposed Use</label>
                        <select name="proposed_use" value={params.proposed_use} onChange={handleChange} className="glass-input w-full py-2.5 text-sm bg-transparent hover:bg-white/10 transition-colors">
                            <option className="bg-[#1a103c]">Residential Building</option>
                            <option className="bg-[#1a103c]">Commercial Office</option>
                            <option className="bg-[#1a103c]">IT Park</option>
                            <option className="bg-[#1a103c]">Hospital</option>
                        </select>
                    </div>

                    <div className="space-y-1.5">
                        <label className="text-sm text-gray-300 font-medium ml-1 flex items-center gap-1.5"><Building2 size={14} /> Building Height (m)</label>
                        <input type="number" name="building_height" value={params.building_height} onChange={handleChange} className="glass-input w-full py-2.5 text-sm" />
                    </div>
                </div>

                {/* Section: Advanced */}
                <div className="space-y-4 pt-4 border-t border-white/5">
                    <button className="flex items-center gap-2 text-xs text-purple-400 hover:text-purple-300 transition-colors">
                        <Settings size={12} /> Advanced Configuration
                    </button>
                    <div className="space-y-3 text-white/50">
                        <div className="space-y-1">
                            <label className="text-xs ml-1 uppercase tracking-wider font-bold text-gray-400">ASR Rate</label>
                            <input type="number" name="asr_rate" value={params.asr_rate} onChange={handleChange} className="glass-input w-full py-2.5 px-3 text-sm" placeholder="0" />
                        </div>
                        <div className="space-y-1">
                            <label className="text-xs ml-1 uppercase tracking-wider font-bold text-gray-400">Deductions</label>
                            <input type="number" name="plot_deductions" value={params.plot_deductions} onChange={handleChange} className="glass-input w-full py-2.5 px-3 text-sm" placeholder="0" />
                        </div>
                    </div>
                </div>
            </div>

            <div className="bg-gradient-to-t from-[#0a0510] via-[#0a0510] to-transparent">
                <div className="px-6 pt-4 pb-2">
                    <button
                        onClick={handleRun}
                        disabled={isRunning}
                        className={`w-full py-3.5 px-6 rounded-xl font-semibold flex items-center justify-center gap-2 shadow-lg transition-all duration-300 ${isRunning
                            ? 'bg-gray-800 text-gray-500 cursor-not-allowed'
                            : 'gradient-btn text-white hover:scale-[1.02]'
                            }`}
                    >
                        {isRunning ? (
                            <div className="flex items-center gap-2">
                                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                <span>Processing...</span>
                            </div>
                        ) : (
                            <>
                                <span>Run Analysis</span>
                                <Play size={16} fill="currentColor" />
                            </>
                        )}
                    </button>
                </div>

                {/* HACKATHON WOW: Live Feed in Sidebar */}
                <div className="h-64 border-t border-white/5">
                    <LiveAgentFeed isRunning={isRunning} params={params} />
                </div>
            </div>
        </div>
    );
};

export default Sidebar;
