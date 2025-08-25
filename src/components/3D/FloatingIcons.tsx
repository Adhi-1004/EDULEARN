import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Box, Cylinder, Octahedron } from '@react-three/drei';
import * as THREE from 'three';

export const FloatingIcons: React.FC = () => {
  const groupRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.children.forEach((child, index) => {
        child.position.y = Math.sin(state.clock.elapsedTime + index) * 0.3;
        child.rotation.y += 0.01 * (index + 1);
        child.rotation.x += 0.005 * (index + 1);
      });
    }
  });

  const shapes = [
    { Component: Box, args: [0.5, 0.5, 0.5], position: [-3, 2, 0], color: '#F59E0B' },
    { Component: Cylinder, args: [0.3, 0.3, 0.6, 8], position: [3, 1, -1], color: '#EF4444' },
    { Component: Octahedron, args: [0.4], position: [-2, -1, 2], color: '#10B981' },
    { Component: Box, args: [0.4, 0.4, 0.4], position: [2, -2, 1], color: '#8B5CF6' },
  ];

  return (
    <group ref={groupRef}>
      {shapes.map((shape, index) => {
        const { Component, args, position, color } = shape;
        return (
          <Component
            key={index}
            args={args as any}
            position={position as [number, number, number]}
            castShadow
            receiveShadow
          >
            <meshStandardMaterial color={color} />
          </Component>
        );
      })}
    </group>
  );
};
