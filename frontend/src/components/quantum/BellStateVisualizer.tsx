import { useRef } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { Sphere, Line, Text, OrbitControls } from '@react-three/drei';
import * as THREE from 'three';

const TeleportationScene = ({ correlation }: { correlation: number }) => {
  const qubitARef = useRef<THREE.Mesh>(null);
  const qubitBRef = useRef<THREE.Mesh>(null);
  const classicalBitRef = useRef<THREE.Mesh>(null);
  const entanglementLineRef = useRef<any>(null);
  
  const baseColor = new THREE.Color("#DFFFBC");
  const measureColor = new THREE.Color("#FDE047");
  const targetColor = new THREE.Color("#60A5FA");
  const errorColor = new THREE.Color("#F87171");

  const { viewport } = useThree();
  // Ensure the 5-unit wide scene (-2.5 to 2.5) fits in the viewport safely
  const scale = Math.min(1, viewport.width / 6);

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime() % 10; // 10 second loop (slower)
    
    // Default positions
    if (qubitARef.current) {
      qubitARef.current.position.set(-2, Math.sin(clock.getElapsedTime() * 2) * 0.1, 0);
      qubitARef.current.rotation.y = clock.getElapsedTime() * 0.5;
    }
    if (qubitBRef.current) {
      qubitBRef.current.position.set(2, Math.sin(clock.getElapsedTime() * 2 + Math.PI) * 0.1, 0);
      qubitBRef.current.rotation.y = clock.getElapsedTime() * 0.5;
    }

    // Sequence Animation
    // 0-2s: Entanglement forms
    // 2-4s: Alice measures (A flashes)
    // 4-7s: Classical bits travel
    // 7-9s: Bob applies Pauli correction (B flashes)
    // 9-10s: Resolves to target state
    
    let aColor = baseColor.clone();
    let bColor = baseColor.clone();
    
    // Entanglement broken scenario
    if (correlation < 0.5) {
      bColor = errorColor.clone();
    }
    
    if (t > 2 && t <= 4) {
      // Alice measurement
      aColor.lerp(measureColor, (t - 2) / 2);
    } else if (t > 4) {
      aColor = new THREE.Color("#444444"); // Collapsed state
    }
    
    if (classicalBitRef.current) {
      if (t > 4 && t <= 7) {
        classicalBitRef.current.visible = true;
        const progress = (t - 4) / 3;
        // Travel from x=-2 to x=2
        classicalBitRef.current.position.set(-2 + (progress * 4), 0, 0);
      } else {
        classicalBitRef.current.visible = false;
      }
    }
    
    if (t > 7 && t <= 9 && correlation >= 0.5) {
      // Bob Pauli correction
      bColor.lerp(targetColor, (t - 7) / 2);
    } else if (t > 9 && correlation >= 0.5) {
      bColor = targetColor.clone();
    }
    
    if (qubitARef.current) {
       (qubitARef.current.material as THREE.MeshPhysicalMaterial).color = aColor;
       (qubitARef.current.material as THREE.MeshPhysicalMaterial).emissive = aColor;
    }
    if (qubitBRef.current) {
       (qubitBRef.current.material as THREE.MeshPhysicalMaterial).color = bColor;
       (qubitBRef.current.material as THREE.MeshPhysicalMaterial).emissive = bColor;
    }
    
  });

  const beamColor = correlation > 0.8 ? "#DFFFBC" : (correlation > 0.5 ? "#FDE047" : "#F87171");
  const eOpacity = correlation < 0.5 ? 0.1 : Math.max(0.1, correlation);

  return (
    <group scale={scale}>
      {/* Qubit A */}
      <group position={[-2, 0, 0]}>
        <Sphere ref={qubitARef} args={[0.5, 32, 32]}>
          <meshPhysicalMaterial transparent opacity={0.8} roughness={0.2} metalness={0.8} />
        </Sphere>
        <Text position={[0, -0.8, 0]} fontSize={0.2} color="white" anchorX="center" anchorY="middle">
          ALICE (Qubit A)
        </Text>
      </group>

      {/* Qubit B */}
      <group position={[2, 0, 0]}>
        <Sphere ref={qubitBRef} args={[0.5, 32, 32]}>
          <meshPhysicalMaterial transparent opacity={0.8} roughness={0.2} metalness={0.8} />
        </Sphere>
        <Text position={[0, -0.8, 0]} fontSize={0.2} color="white" anchorX="center" anchorY="middle">
          BOB (Qubit B)
        </Text>
      </group>
      
      {/* Classical bits traveling */}
      <Sphere ref={classicalBitRef} args={[0.1, 16, 16]} visible={false}>
        <meshBasicMaterial color="#FDE047" />
      </Sphere>
      <Text position={[0, 0.4, 0]} fontSize={0.15} color="#FDE047" visible={false}>
        Classical Bits
      </Text>

      {/* Entanglement Connection */}
      <Line 
        ref={entanglementLineRef}
        points={[[-2, 0, 0], [2, 0, 0]]} 
        color={beamColor} 
        lineWidth={5 * correlation} 
        transparent 
        opacity={eOpacity}
      />
      
      {correlation < 0.5 && (
        <Text position={[0, 0.5, 0]} fontSize={0.2} color="#F87171">
          ENTANGLEMENT DEGRADED
        </Text>
      )}
    </group>
  );
};

export const BellStateVisualizer = ({ correlation }: { correlation: number }) => {
  return (
    <div className="w-full h-[350px] relative rounded-lg overflow-hidden cursor-move">
      <Canvas camera={{ position: [0, 0, 7], fov: 45 }}>
        <ambientLight intensity={0.2} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        <TeleportationScene correlation={correlation} />
        <OrbitControls 
          enableZoom={false} 
          enablePan={false} 
          maxPolarAngle={Math.PI / 2 + 0.3} 
          minPolarAngle={Math.PI / 2 - 0.3} 
          minAzimuthAngle={-0.5} 
          maxAzimuthAngle={0.5} 
        />
      </Canvas>
      <div className="absolute top-2 right-2 flex gap-2">
        <span className="text-[10px] font-mono text-q-text-secondary bg-black/50 px-2 py-1 rounded backdrop-blur border border-white/10">INTERACTIVE 3D</span>
      </div>
    </div>
  );
};
