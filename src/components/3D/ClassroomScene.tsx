import React, { useMemo, useRef } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { Html, Text, Sphere, Box, Plane } from '@react-three/drei';
import * as THREE from 'three';

export const ClassroomScene: React.FC = () => {
  const groupRef = useRef<THREE.Group>(null);
  const { camera } = useThree();
  const timeRef = useRef(0);

  const studentPositions = useMemo(() => {
    const rows = 2;
    const cols = 3;
    const spacingX = 1.6;
    const spacingZ = 1.3;
    const startX = -((cols - 1) * spacingX) / 2;
    const startZ = 0.5;
    const list: Array<[number, number, number]> = [];
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        list.push([startX + c * spacingX, -0.2, startZ + r * spacingZ]);
      }
    }
    return list;
  }, []);

  useFrame((_, delta) => {
    timeRef.current += delta;
    if (groupRef.current) {
      groupRef.current.rotation.y = Math.sin(timeRef.current * 0.2) * 0.1;
    }
    const t = timeRef.current;
    camera.position.x = Math.sin(t * 0.15) * 0.6;
    camera.position.z = 5 + Math.cos(t * 0.1) * 0.3;
    camera.lookAt(0, 0, 0);
  });

  return (
    <group ref={groupRef}>
      {/* Floor */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.6, 0]} receiveShadow>
        <planeGeometry args={[10, 10]} />
        <meshStandardMaterial color="#1f2937" roughness={0.9} metalness={0.05} />
      </mesh>

      {/* AI Hologram Teacher */}
      <group position={[0, 0, -1.2]}>
        <Sphere args={[0.5, 32, 32]}>
          <meshStandardMaterial color="#60A5FA" emissive="#60A5FA" emissiveIntensity={0.7} transparent opacity={0.7} />
        </Sphere>
        <Text position={[0, 0.9, 0]} fontSize={0.22} color="#93C5FD" anchorX="center" anchorY="middle">AI Mentor</Text>
        <mesh rotation={[Math.PI / 2, 0, 0]} position={[0, -0.55, 0]}>
          <ringGeometry args={[0.45, 0.6, 64]} />
          <meshStandardMaterial color="#818CF8" emissive="#818CF8" emissiveIntensity={0.4} transparent opacity={0.4} />
        </mesh>
      </group>

      {/* Student desks with glowing laptops */}
      {studentPositions.map((pos, i) => (
        <group key={i} position={pos as [number, number, number]}>
          <Box args={[1.1, 0.1, 0.6]} position={[0, -0.15, 0]} castShadow receiveShadow>
            <meshStandardMaterial color="#374151" />
          </Box>
          <Box args={[0.6, 0.03, 0.4]} position={[0, 0, -0.05]}>
            <meshStandardMaterial color="#111827" />
          </Box>
          <Plane args={[0.6, 0.35]} position={[0, 0.2, -0.28]} rotation={[-0.6, 0, 0]}>
            <meshStandardMaterial color="#22D3EE" emissive="#22D3EE" emissiveIntensity={0.8} />
          </Plane>
          <Sphere args={[0.12, 16, 16]} position={[0, 0.15, 0.15]}>
            <meshStandardMaterial color="#10B981" />
          </Sphere>
        </group>
      ))}

      {/* Hotspots */}
      <Html position={[-1.6, 0.6, -0.2]} center>
        <a href="#features" className="px-2 py-1 rounded-md text-xs bg-white/80 backdrop-blur text-slate-700 shadow">Assignments</a>
      </Html>
      <Html position={[0, 0.7, -0.2]} center>
        <a href="#features" className="px-2 py-1 rounded-md text-xs bg-white/80 backdrop-blur text-slate-700 shadow">Coding</a>
      </Html>
      <Html position={[1.6, 0.6, -0.2]} center>
        <a href="#features" className="px-2 py-1 rounded-md text-xs bg-white/80 backdrop-blur text-slate-700 shadow">AI Tutor</a>
      </Html>
    </group>
  );
};


