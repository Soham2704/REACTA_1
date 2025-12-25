import React, { useMemo } from 'react';
import { Viewer, Entity, CameraFlyTo } from 'resium';
import { Cartesian3, Color, Math as CesiumMath } from 'cesium';

// Default to Mumbai for context
// Position offset to ensure building bottom is on ground (approximate)
const LONGITUDE = 72.8777;
const LATITUDE = 19.0760;

const CesiumView = ({ width = 20, depth = 20, height = 50 }) => {

    // Calculate position: We lift the entity by half its height so it sits ON the ground, not IN it.
    const position = useMemo(() => {
        return Cartesian3.fromDegrees(LONGITUDE, LATITUDE, height / 2);
    }, [height]);

    // Angled Camera View
    const destination = useMemo(() => {
        return Cartesian3.fromDegrees(
            LONGITUDE,
            LATITUDE - 0.002, // Move camera slightly south
            300 // Height
        );
    }, []);

    const orientation = {
        heading: CesiumMath.toRadians(0), // Facing North
        pitch: CesiumMath.toRadians(-35), // Looking down at 35 degrees
        roll: 0
    };

    return (
        <div className="w-full h-full relative">
            <Viewer full homeButton={false} navigationHelpButton={false} sceneModePicker={false} baseLayerPicker={false} geocoder={false}>
                <CameraFlyTo
                    destination={destination}
                    orientation={orientation}
                    duration={3}
                />
                <Entity
                    name="Proposed Architecture"
                    position={position}
                    box={{
                        dimensions: new Cartesian3(width, depth, height),
                        material: Color.CYAN.withAlpha(0.7),
                        outline: true,
                        outlineColor: Color.WHITE,
                    }}
                    description={`
                        <h3>Proposed Development</h3>
                        <p>Height: ${height}m</p>
                        <p>Width: ${width}m</p>
                        <p>Depth: ${depth}m</p>
                    `}
                />
            </Viewer>

            {/* Overlay to ensure fit with the UI theme */}
            <div className="absolute inset-0 pointer-events-none border border-cyan-500/20 rounded-xl z-50"></div>
        </div>
    );
};

export default CesiumView;
