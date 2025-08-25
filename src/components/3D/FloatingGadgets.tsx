import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Box, Sphere, Torus, Text } from '@react-three/drei';
import * as THREE from 'three';

export const FloatingGadgets: React.FC = () => {
  const groupRef = useRef<THREE.Group>(null);
  useFrame((state) => {
    if (!groupRef.current) return;
    const t = state.clock.getElapsedTime();
    groupRef.current.rotation.y = t * 0.15;
    groupRef.current.children.forEach((c, i) => {
      c.position.y = Math.sin(t + i) * 0.2;
    });
  });
  const items = [
    { type: 'book', color: '#60A5FA', Component: Box, args: [0.8, 1, 0.12], position: [-2, 0.2, 0] },
    { type: 'tablet', color: '#A78BFA', Component: Box, args: [0.7, 0.45, 0.05], position: [2, -0.2, 0.5] },
    { type: 'laptop', color: '#34D399', Component: Box, args: [0.9, 0.55, 0.06], position: [0.5, 0.4, -1] },
    { type: 'ai', color: '#F472B6', Component: Sphere, args: [0.35, 24, 24], position: [0, 0, 0] },
    { type: 'ring', color: '#22D3EE', Component: Torus, args: [0.6, 0.06, 12, 36], position: [-0.8, -0.3, 1.2] },
  ];
  return (
    <group ref={groupRef}>
      {items.map((item, i) => {
        const Any = item.Component as any;
        return (
          <group key={i} position={item.position as [number, number, number]}>
            <Any args={item.args}>
              <meshStandardMaterial color={item.color} emissive={item.color} emissiveIntensity={0.35} />
            </Any>
            {item.type === 'book' && (
              <Text position={[0, 0, 0.08]} fontSize={0.17} color="#fff" anchorX="center">CS</Text>
            )}
          </group>
        );
      })}
    </group>
  );
};


