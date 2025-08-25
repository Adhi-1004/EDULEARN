import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Text, Tube } from '@react-three/drei';
import * as THREE from 'three';

export const LearningJourney: React.FC = () => {
  const curve = useRef(new THREE.CatmullRomCurve3([
    new THREE.Vector3(-2.5, -0.5, 1.5),
    new THREE.Vector3(-1.5, 0.2, 0.8),
    new THREE.Vector3(0, 0.4, 0),
    new THREE.Vector3(1.5, 0.1, -0.6),
    new THREE.Vector3(2.5, 0.5, -1.2)
  ]));
  const followRef = useRef<THREE.Group>(null);
  const tRef = useRef(0);

  useFrame((_, delta) => {
    tRef.current = (tRef.current + delta * 0.08) % 1;
    const pos = curve.current.getPointAt(tRef.current);
    const next = curve.current.getPointAt((tRef.current + 0.01) % 1);
    followRef.current?.position.copy(pos);
    followRef.current?.lookAt(next);
  });

  const labels = [
    { t: 0.02, text: 'Start Learning' },
    { t: 0.28, text: 'Assignments' },
    { t: 0.5, text: 'Projects' },
    { t: 0.75, text: 'Graduation' },
    { t: 0.95, text: 'Career Success' },
  ];

  return (
    <group>
      <Tube args={[curve.current, 100, 0.05, 8, false]}>
        <meshStandardMaterial color="#34D399" emissive="#34D399" emissiveIntensity={0.6} />
      </Tube>
      {labels.map((l, i) => {
        const p = curve.current.getPointAt(l.t);
        return (
          <Text key={i} position={[p.x, p.y + 0.3, p.z]} fontSize={0.18} color="#60A5FA" anchorX="center">
            {l.text}
          </Text>
        );
      })}
      <group ref={followRef}>
        <mesh>
          <sphereGeometry args={[0.12, 16, 16]} />
          <meshStandardMaterial color="#60A5FA" emissive="#60A5FA" emissiveIntensity={0.8} />
        </mesh>
      </group>
    </group>
  );
};


