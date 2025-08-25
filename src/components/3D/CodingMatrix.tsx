import React, { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Sphere, Text } from '@react-three/drei';
import * as THREE from 'three';

export const CodingMatrix: React.FC = () => {
  const groupRef = useRef<THREE.Group>(null);
  const particles = useMemo(() => {
    const count = 200;
    const arr: { pos: THREE.Vector3; speed: number; char: string }[] = [];
    const chars = ['{', '}', '()', 'λ', 'Σ', '∑', 'π', '=>', '∫', 'i++'];
    for (let i = 0; i < count; i++) {
      arr.push({
        pos: new THREE.Vector3((Math.random() - 0.5) * 6, Math.random() * 6, (Math.random() - 0.5) * 4),
        speed: 0.2 + Math.random() * 0.6,
        char: chars[Math.floor(Math.random() * chars.length)],
      });
    }
    return arr;
  }, []);

  useFrame((state, delta) => {
    if (!groupRef.current) return;
    particles.forEach(p => {
      p.pos.y -= delta * p.speed;
      if (p.pos.y < -3) {
        p.pos.y = 3;
        p.pos.x = (Math.random() - 0.5) * 6;
        p.pos.z = (Math.random() - 0.5) * 4;
      }
    });
  });

  return (
    <group ref={groupRef}>
      {/* Central AI brain/laptop sphere */}
      <Sphere args={[0.6, 32, 32]} position={[0, 0, 0]}>
        <meshStandardMaterial color="#7C3AED" emissive="#7C3AED" emissiveIntensity={0.7} />
      </Sphere>
      {/* Falling code/equations */}
      {particles.map((p, i) => (
        <Text
          key={i}
          position={[p.pos.x, p.pos.y, p.pos.z]}
          fontSize={0.2}
          color="#60A5FA"
          rotation={[0, 0, Math.sin(i) * 0.3]}
        >
          {p.char}
        </Text>
      ))}
    </group>
  );
};


