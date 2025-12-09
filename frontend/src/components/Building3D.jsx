
import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Stage, Grid, Environment, ContactShadows, Text } from '@react-three/drei';
import * as THREE from 'three';

const ProceduralBuilding = ({ width, depth, height }) => {
    const meshRef = useRef();

    // Ensure valid dimensions
    const w = Math.max(1, width || 10);
    const d = Math.max(1, depth || 10);
    const h = Math.max(1, height || 10);

    // Floor heights (standard ~3m per floor)
    const floorCount = Math.floor(h / 3);

    // Create geometry with segmentations for windows
    const geometry = useMemo(() => new THREE.BoxGeometry(w, h, d), [w, h, d]);

    // Create a simple window shader material or use standard material with texture hints
    // For now, we use a nice physical material
    const material = new THREE.MeshPhysicalMaterial({
        color: '#e0e0e0',
        metalness: 0.1,
        roughness: 0.2,
        transmission: 0,
        clearcoat: 0.5,
        clearcoatRoughness: 0.1,
    });

    // Edges for "blueprint" look overlay
    const edges = useMemo(() => new THREE.EdgesGeometry(geometry), [geometry]);

    return (
        <group position={[0, h / 2, 0]}>
            {/* Main Mass */}
            <mesh ref={meshRef} geometry={geometry} material={material} castShadow receiveShadow />

            {/* Edges */}
            <lineSegments args={[edges, new THREE.LineBasicMaterial({ color: '#4f46e5', linewidth: 2 })]} />

            {/* Floor indicators */}
            {Array.from({ length: floorCount }).map((_, i) => (
                <lineSegments
                    key={i}
                    position={[0, -h / 2 + (i + 1) * 3, 0]}
                >
                    <edgesGeometry args={[new THREE.BoxGeometry(w + 0.1, 0.05, d + 0.1)]} />
                    <lineBasicMaterial color="#4f46e5" transparent opacity={0.3} />
                </lineSegments>
            ))}
        </group>
    );
};

const Building3D = ({ width, depth, height }) => {
    return (
        <div className="w-full h-96 bg-gradient-to-br from-gray-900 to-slate-800 rounded-2xl overflow-hidden relative">
            <div className="absolute top-4 left-4 z-10 pointer-events-none">
                <h3 className="text-white font-bold text-lg drop-shadow-md">3D Visualization</h3>
                <p className="text-gray-300 text-xs drop-shadow-md">Interactive View • {width}m x {depth}m x {height}m</p>
            </div>

            <Canvas shadows camera={{ position: [width * 2, height * 1.5, depth * 2], fov: 45 }}>
                <color attach="background" args={['#111827']} />

                {/* Lighting Environment */}
                <ambientLight intensity={0.5} />
                <spotLight position={[50, 50, 50]} angle={0.5} penumbra={1} intensity={1000} castShadow />
                <Environment preset="city" />

                <group>
                    <ProceduralBuilding width={width} depth={depth} height={height} />

                    {/* Floor Plane */}
                    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.01, 0]} receiveShadow>
                        <planeGeometry args={[100, 100]} />
                        <meshStandardMaterial color="#1f2937" metalness={0.8} roughness={0.2} />
                    </mesh>

                    {/* Grid */}
                    <Grid
                        position={[0, 0.01, 0]}
                        args={[100, 100]}
                        cellSize={1}
                        cellThickness={0.5}
                        cellColor="#6b7280"
                        sectionSize={5}
                        sectionThickness={1}
                        sectionColor="#4f46e5"
                        fadeDistance={50}
                        infiniteGrid
                    />

                    {/* Shadow Catcher */}
                    <ContactShadows position={[0, 0, 0]} opacity={0.5} scale={50} blur={2.5} far={4} />
                </group>

                <OrbitControls makeDefault autoRotate autoRotateSpeed={0.5} maxPolarAngle={Math.PI / 2} />
            </Canvas>
        </div>
    );
};

export default Building3D;
