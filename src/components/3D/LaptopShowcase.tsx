import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Box, Plane, Text } from '@react-three/drei';
import * as THREE from 'three';

type LaptopProps = {
  position: [number, number, number];
  label: string;
  color?: string;
};

function Laptop({ position, label, color = '#22D3EE' }: LaptopProps) {
  return (
    <group position={position}>
      {/* Desk/base shadow catcher */}
      <Box args={[1.2, 0.08, 0.8]} position={[0, -0.18, 0]} receiveShadow>
        <meshStandardMaterial color="#1f2937" />
      </Box>

      {/* Laptop base */}
      <Box args={[0.9, 0.04, 0.6]} position={[0, 0, 0]} castShadow>
        <meshStandardMaterial color="#0b1324" />
      </Box>

      {/* Screen */}
      <Plane args={[0.9, 0.55]} position={[0, 0.36, -0.28]} rotation={[-0.58, 0, 0]}>
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.65} />
      </Plane>

      {/* Screen label */}
      <Text
        position={[0, 0.36, -0.26]}
        rotation={[-0.58, 0, 0]}
        fontSize={0.18}
        color="#ffffff"
        anchorX="center"
        anchorY="middle"
        outlineWidth={0.005}
        outlineColor="#0b1324"
      >
        {label}
      </Text>
    </group>
  );
}

export const LaptopShowcase: React.FC = () => {
  const groupRef = useRef<THREE.Group>(null);
  useFrame((state) => {
    if (!groupRef.current) return;
    const t = state.clock.getElapsedTime();
    groupRef.current.rotation.y = Math.sin(t * 0.2) * 0.06;
  });

  return (
    <group ref={groupRef}>
      {/* Subtle ground */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.22, 0]} receiveShadow>
        <planeGeometry args={[10, 6]} />
        <meshStandardMaterial color="#0b1324" roughness={0.95} metalness={0.05} />
      </mesh>

      <Laptop position={[-1.6, 0, 0.4]} label="learn" color="#60A5FA" />
      <Laptop position={[0, 0, -0.1]} label="code" color="#A78BFA" />
      <Laptop position={[1.6, 0, 0.4]} label="succeed" color="#34D399" />
    </group>
  );
};


