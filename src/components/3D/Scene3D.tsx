import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera } from '@react-three/drei';
import { FloatingIcons } from './FloatingIcons';
import { OrbitingSubjects } from './OrbitingSubjects';
import { ClassroomScene } from './ClassroomScene';
import { CodingMatrix } from './CodingMatrix';
import { LearningJourney } from './LearningJourney';
import { FloatingGadgets } from './FloatingGadgets';
import { LaptopShowcase } from './LaptopShowcase';

interface Scene3DProps {
  type: 'books' | 'icons' | 'subjects' | 'network' | 'classroom' | 'matrix' | 'journey' | 'gadgets' | 'laptops';
  className?: string;
}

export const Scene3D: React.FC<Scene3DProps> = ({ type, className }) => {
  const renderScene = () => {
    switch (type) {
      case 'books':
        return <FloatingGadgets />;
      case 'subjects':
        return <OrbitingSubjects />;
      case 'icons':
        return <FloatingIcons />;
      case 'network':
        return <OrbitingSubjects />;
      case 'classroom':
        return <ClassroomScene />;
      case 'matrix':
        return <CodingMatrix />;
      case 'journey':
        return <LearningJourney />;
      case 'gadgets':
        return <FloatingGadgets />;
      case 'laptops':
        return <LaptopShowcase />;
      default:
        return <LaptopShowcase />;
    }
  };

  return (
    <div className={className}>
      <Canvas shadows>
        <PerspectiveCamera makeDefault position={[0, 0, 5]} />
        <ambientLight intensity={0.5} />
        <directionalLight
          position={[10, 10, 5]}
          intensity={1}
          castShadow
          shadow-mapSize-width={2048}
          shadow-mapSize-height={2048}
        />
        <pointLight position={[-10, -10, -10]} intensity={0.3} />
        
        <Suspense fallback={null}>
          {renderScene()}
        </Suspense>
        
        <OrbitControls
          enableZoom={false}
          enablePan={false}
          autoRotate
          autoRotateSpeed={0.5}
        />
      </Canvas>
    </div>
  );
};
