import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Sphere, Text } from '@react-three/drei';
import * as THREE from 'three';

/**
 * OrbitingSubjects
 * A learning-themed 3D scene with subject labels orbiting a glowing knowledge core.
 */
export const OrbitingSubjects: React.FC = () => {
  const groupRef = useRef<THREE.Group>(null);
  const subjects = [
    { label: 'Math', color: '#3B82F6', offset: 0 },
    { label: 'AI', color: '#8B5CF6', offset: Math.PI / 2 },
    { label: 'Physics', color: '#10B981', offset: Math.PI },
    { label: 'Code', color: '#F59E0B', offset: (3 * Math.PI) / 2 },
  ];

  useFrame((state) => {
    if (!groupRef.current) return;
    const t = state.clock.getElapsedTime();
    // gentle rotation of the whole system
    groupRef.current.rotation.y = t * 0.2;
    // per-child orbit animation
    groupRef.current.children.forEach((child, index) => {
      if (index === 0) return; // index 0 is the core sphere
      const info = subjects[index - 1];
      const r = 1.9;
      const speed = 0.6;
      const angle = t * speed + info.offset;
      child.position.x = Math.cos(angle) * r;
      child.position.z = Math.sin(angle) * r;
      child.position.y = Math.sin(t * 1.2 + index) * 0.2;
    });
  });

  return (
    <group ref={groupRef}>
      {/* Knowledge core */}
      <Sphere args={[0.7, 32, 32]} castShadow receiveShadow>
        <meshStandardMaterial color="#2563EB" emissive="#3B82F6" emissiveIntensity={0.6} />
      </Sphere>

      {subjects.map((s, i) => (
        <group key={s.label}>
          <Sphere args={[0.12, 16, 16]}>
            <meshStandardMaterial color={s.color} />
          </Sphere>
          <Text
            position={[0, 0.28, 0]}
            fontSize={0.25}
            color={s.color}
            anchorX="center"
            anchorY="middle"
          >
            {s.label}
          </Text>
        </group>
      ))}
    </group>
  );
};


