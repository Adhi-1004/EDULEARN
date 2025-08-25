import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Sphere, Ring } from '@react-three/drei';
import * as THREE from 'three';

export const AnimatedGlobe: React.FC = () => {
  const globeRef = useRef<THREE.Mesh>(null);
  const ringsRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (globeRef.current) {
      globeRef.current.rotation.y += 0.005;
    }
    if (ringsRef.current) {
      ringsRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.5) * 0.2;
      ringsRef.current.rotation.z = Math.cos(state.clock.elapsedTime * 0.3) * 0.1;
    }
  });

  return (
    <group>
      <Sphere ref={globeRef} args={[1, 32, 32]} castShadow receiveShadow>
        <meshStandardMaterial
          color="#3B82F6"
          transparent
          opacity={0.8}
          wireframe
        />
      </Sphere>
      
      <group ref={ringsRef}>
        <Ring args={[1.2, 1.3, 32]} rotation={[Math.PI / 2, 0, 0]}>
          <meshStandardMaterial color="#8B5CF6" transparent opacity={0.6} />
        </Ring>
        <Ring args={[1.4, 1.5, 32]} rotation={[0, Math.PI / 2, 0]}>
          <meshStandardMaterial color="#EC4899" transparent opacity={0.4} />
        </Ring>
      </group>
    </group>
  );
};
