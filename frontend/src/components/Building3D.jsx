import React, { useRef, useMemo, useState, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Grid, Environment, ContactShadows, Stars } from '@react-three/drei';
import { EffectComposer, Bloom } from '@react-three/postprocessing';
import * as THREE from 'three';

const DataCloud = ({ count = 100, radius = 20, colors = ['#ffffff'] }) => {
    const points = useMemo(() => {
        const p = new Float32Array(count * 3);
        const c = new Float32Array(count * 3);
        const sizes = new Float32Array(count);

        for (let i = 0; i < count; i++) {
            const r = (Math.random() * radius) + radius / 2;
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.acos((Math.random() * 2) - 1);

            p[i * 3] = r * Math.sin(phi) * Math.cos(theta);
            p[i * 3 + 1] = (r * Math.sin(phi) * Math.sin(theta)) * 0.5 + 10; // Flattened disc, lifted up
            p[i * 3 + 2] = r * Math.cos(phi);

            const color = new THREE.Color(colors[Math.floor(Math.random() * colors.length)]);
            c[i * 3] = color.r;
            c[i * 3 + 1] = color.g;
            c[i * 3 + 2] = color.b;

            sizes[i] = Math.random() * 0.2;
        }
        return { p, c, sizes };
    }, [count, radius, colors]);

    return (
        <points>
            <bufferGeometry>
                <bufferAttribute attach="attributes-position" count={count} array={points.p} itemSize={3} />
                <bufferAttribute attach="attributes-color" count={count} array={points.c} itemSize={3} />
                <bufferAttribute attach="attributes-size" count={count} array={points.sizes} itemSize={1} />
            </bufferGeometry>
            <pointsMaterial size={0.3} vertexColors transparent opacity={0.6} sizeAttenuation depthWrite={false} blending={THREE.AdditiveBlending} />
        </points>
    );
};

const ProceduralBuilding = ({ width, depth, height, optimizationVal }) => {
    const meshRef = useRef();

    // Dynamic Height Animation: Start small, grow to final height
    // optimizationVal goes from 0 to 1
    const w = Number(width) || 10;
    const d = Number(depth) || 10;
    const targetH = Number(height) || 15;

    // Animate from 30% height to 100% height
    const currentH = targetH * (0.3 + (optimizationVal * 0.7));

    const floorCount = Math.max(1, Math.floor(currentH / 3));

    const geometry = useMemo(() => new THREE.BoxGeometry(w, currentH, d), [w, currentH, d]);
    const edges = useMemo(() => new THREE.EdgesGeometry(geometry), [geometry]);

    // Color shift: Gray -> Cyan -> Green/Gold based on completion
    const color = useMemo(() => {
        const c1 = new THREE.Color("#4b5563"); // Start Gray
        const c2 = new THREE.Color("#06b6d4"); // Mid Cyan
        const c3 = new THREE.Color("#10b981"); // End Emerald
        if (optimizationVal < 0.5) return c1.lerp(c2, optimizationVal * 2);
        return c2.lerp(c3, (optimizationVal - 0.5) * 2);
    }, [optimizationVal]);

    return (
        <group position={[0, currentH / 2, 0]}>
            {/* GLASSY MONOLITH */}
            <mesh geometry={geometry} castShadow receiveShadow>
                <meshPhysicalMaterial
                    color={color}
                    metalness={0.8}
                    roughness={0.1}
                    transmission={0.6}
                    thickness={2.0}
                    clearcoat={1.0}
                    envMapIntensity={2.5}
                />
            </mesh>

            {/* NEON BORDERS */}
            <lineSegments args={[edges, new THREE.LineBasicMaterial({ color: color.clone().multiplyScalar(4), linewidth: 2 })]} />

            {/* Glowing Floor Lines */}
            {Array.from({ length: floorCount }).map((_, i) => (
                <lineSegments
                    key={i}
                    position={[0, -currentH / 2 + (i + 1) * 3, 0]}
                    renderOrder={1}
                >
                    <edgesGeometry args={[new THREE.BoxGeometry(w + 0.1, 0.1, d + 0.1)]} />
                    <lineBasicMaterial color={color.clone().multiplyScalar(2)} toneMapped={false} />
                </lineSegments>
            ))}
        </group>
    );
};

const Building3D = ({ width, depth, height }) => {
    const w = Number(width) || 10;
    const d = Number(depth) || 10;
    const h = Number(height) || 15;

    // Start at 0 (Baseline) and wait for user trigger
    const [optimization, setOptimization] = useState(0);
    const [status, setStatus] = useState("Waiting for Authorization...");
    const [isPlaying, setIsPlaying] = useState(false);

    const startOptimization = () => {
        setIsPlaying(true);
        setStatus("Initializing Optimization Protocol...");

        let progress = 0;
        const interval = setInterval(() => {
            progress += 0.015; // Slower, more dramatic (approx 2s)
            if (progress >= 1) {
                progress = 1;
                clearInterval(interval);
                setStatus("Optimal Massing Achieved");
            } else if (progress < 0.3) {
                setStatus("Ingesting Constraints...");
            } else if (progress < 0.7) {
                setStatus("RL Agent Maximizing FSI...");
            } else {
                setStatus("Finalizing Structure...");
            }
            setOptimization(progress);
        }, 30);
    };

    const displayW = w.toFixed(1);
    const displayD = d.toFixed(1);
    const displayH = h.toFixed(1);
    const baseSize = Math.max(w, d, h) * 4;
    const camDist = Math.max(w, d, h) * 1.8;

    return (
        <div className="w-full relative group rounded-xl overflow-hidden border border-cyan-500/50 shadow-[0_0_40px_rgba(6,182,212,0.15)] bg-black/80 backdrop-blur-md transition-all duration-300 hover:shadow-[0_0_60px_rgba(6,182,212,0.25)] hover:border-cyan-400">

            {/* Status Header */}
            <div className="absolute top-0 left-0 right-0 z-10 flex justify-between items-start p-6 pointer-events-none">
                <div className="flex flex-col gap-1">
                    <h3 className="text-cyan-400 text-[10px] font-bold tracking-[0.25em] uppercase drop-shadow-[0_0_8px_rgba(6,182,212,0.8)]">Veritas Spatial Engine</h3>
                    <div className="flex items-center gap-2">
                        <div className={`w-1.5 h-1.5 rounded-full ${optimization === 1 ? 'bg-green-400 shadow-[0_0_10px_#4ade80]' : 'bg-cyan-400 animate-pulse shadow-[0_0_10px_#22d3ee]'}`} />
                        <span className="text-[9px] text-cyan-100/80 font-mono tracking-wider uppercase animate-pulse">
                            {status}
                        </span>
                    </div>
                </div>

                <div className="bg-black/40 backdrop-blur-md border border-cyan-500/30 px-4 py-2 rounded-lg text-right">
                    <div className="text-sm text-cyan-100 font-mono tracking-tight">
                        {displayW} × {displayD} × {(h * (0.3 + optimization * 0.7)).toFixed(1)}m
                    </div>
                </div>
            </div>

            {/* Dark Void Background */}
            <div className="h-[500px] w-full bg-gradient-to-b from-[#020617] via-[#0f172a] to-[#020617] cursor-move relative">

                {/* MANUAL TRIGGER OVERLAY */}
                {!isPlaying && (
                    <div className="absolute inset-0 z-20 flex items-center justify-center bg-black/40 backdrop-blur-sm">
                        <button
                            onClick={startOptimization}
                            className="group relative px-8 py-4 bg-cyan-950/80 border border-cyan-500/50 rounded-xl overflow-hidden shadow-[0_0_30px_rgba(6,182,212,0.3)] transition-all hover:scale-105 hover:border-cyan-400 hover:shadow-[0_0_50px_rgba(6,182,212,0.5)]"
                        >
                            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-cyan-400/10 to-transparent translate-x-[-100%] animate-[shimmer_2s_infinite]"></div>
                            <div className="flex flex-col items-center gap-2">
                                <span className="text-xs text-cyan-300 font-mono tracking-[0.2em] uppercase">AI Optimization Ready</span>
                                <span className="text-lg text-white font-bold tracking-widest drop-shadow-md group-hover:text-cyan-100">INITIALIZE AGENT</span>
                            </div>
                        </button>
                    </div>
                )}

                <Canvas shadows camera={{ position: [camDist, camDist, camDist], fov: 35 }} gl={{ preserveDrawingBuffer: true, antialias: false, toneMapping: THREE.ReinhardToneMapping, toneMappingExposure: 1.2 }}>

                    <ambientLight intensity={0.3} />
                    <directionalLight position={[10, 20, 10]} intensity={1.5} castShadow color="#ffffff" />
                    <spotLight position={[-20, 10, -5]} intensity={8} color="#06b6d4" angle={0.5} penumbra={1} />
                    <spotLight position={[20, 5, 5]} intensity={4} color="#10b981" angle={0.5} />

                    <Environment preset="city" />

                    {/* COSMIC AMBIENCE */}
                    <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
                    <DataCloud count={200} radius={baseSize / 1.5} colors={['#06b6d4', '#8b5cf6', '#10b981']} />

                    <group position={[0, -2, 0]}>
                        <ProceduralBuilding width={w} depth={d} height={h} optimizationVal={optimization} />

                        {/* Animated Grid */}
                        <Grid
                            position={[0, -0.04, 0]}
                            args={[baseSize, baseSize]}
                            cellSize={2}
                            cellThickness={1.0}
                            cellColor="#06b6d4"
                            sectionSize={10}
                            sectionThickness={1.5}
                            sectionColor={optimization === 1 ? "#10b981" : "#22d3ee"}
                            fadeDistance={baseSize / 1.2}
                        />

                        <ContactShadows position={[0, -0.05, 0]} opacity={0.8} scale={baseSize} blur={3} far={4} color="#000000" />
                    </group>

                    <OrbitControls
                        makeDefault
                        autoRotate={true} // Always rotate for cinematic feel
                        autoRotateSpeed={isPlaying ? 5.0 : 0.5} // Fast during AI, Slow during idle
                        maxPolarAngle={Math.PI / 2.1}
                        enableZoom={true}
                        enablePan={false}
                        target={[0, h / 3, 0]}
                    />

                    <EffectComposer disableNormalPass>
                        <Bloom luminanceThreshold={0.5} mipmapBlur intensity={1.8} radius={0.6} />
                    </EffectComposer>
                </Canvas>
            </div>

            {/* Replay Button (Bottom Right) */}
            {optimization === 1 && (
                <div className="absolute bottom-6 right-6 flex gap-4 animate-fade-in z-10 pointer-events-auto">
                    <button
                        onClick={() => { setOptimization(0); setIsPlaying(false); setStatus("Reset. Waiting..."); }}
                        className="text-[10px] text-cyan-300 bg-cyan-950/30 hover:bg-cyan-900/50 px-4 py-2 rounded uppercase tracking-[0.2em] border border-cyan-500/30 transition-colors shadow"
                    >
                        Reset Simulation
                    </button>
                </div>
            )}
        </div>
    );
};

export default Building3D;
