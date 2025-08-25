"use client"

import React, { Suspense, useMemo } from "react"
import { Canvas } from "@react-three/fiber"
import { OrbitControls, Environment, Float, Stars, Text, Grid, Line } from "@react-three/drei"
import * as THREE from "three"

type SceneType = "classroom" | "code-lab" | "atom" | "books"

export function Scene3D({
  type = "classroom",
  className = "w-full h-full",
}: {
  type?: SceneType
  className?: string
}) {
  return (
    <div className={className}>
      <Canvas camera={{ position: [6, 4, 8], fov: 50 }}>
        <color attach="background" args={["#0c0f19"]} />
        <Suspense fallback={null}>
          <Lights />
          <AuroraFog />
          {type === "classroom" && <ClassroomScene />}
          {type === "code-lab" && <CodeLabScene />}
          {type === "atom" && <AtomScene />}
          {type === "books" && <BooksScene />}

          <Environment preset="city" />
          <OrbitControls enablePan={false} maxDistance={20} minDistance={4} />
        </Suspense>
      </Canvas>
    </div>
  )
}

function Lights() {
  return (
    <>
      <ambientLight intensity={0.5} />
      <directionalLight position={[5, 10, 5]} intensity={1.2} color={new THREE.Color("#ffd1f7")} />
      <directionalLight position={[-6, 8, -3]} intensity={0.6} color={new THREE.Color("#b2ffe2")} />
      <pointLight position={[0, 3, 0]} intensity={0.5} color={"#ff7ab6"} />
    </>
  )
}

function AuroraFog() {
  return <fog attach="fog" args={["#0c0f19", 10, 40]} />
}

/* Scene: Classroom (stylized board + pencil + text) */
function ClassroomScene() {
  return (
    <>
      <Grid infiniteGrid sectionColor={"#2ee2b7"} cellColor={"#d946ef"} position={[0, -0.5, 0]} />
      <Float speed={1.2} rotationIntensity={0.6} floatIntensity={0.8}>
        {/* Board */}
        <mesh position={[0, 1.6, 0]}>
          <boxGeometry args={[4.5, 2.2, 0.1]} />
          <meshStandardMaterial color={"#101826"} metalness={0.2} roughness={0.7} />
        </mesh>
        {/* Board frame */}
        <mesh position={[0, 1.6, -0.06]}>
          <boxGeometry args={[4.7, 2.4, 0.02]} />
          <meshStandardMaterial color={"#1f2937"} />
        </mesh>
        {/* Chalk text */}
        <Text
          position={[0, 1.7, 0.08]}
          font="/fonts/Geist-Bold.ttf"
          color="#e9eaf6"
          anchorX="center"
          anchorY="middle"
          fontSize={0.42}
        >
          Learn • Build • Succeed
        </Text>
      </Float>

      {/* Pencil (cone + cylinder) */}
      <Float speed={2} rotationIntensity={1.2} floatIntensity={1.2}>
        <mesh position={[-1.6, 0.8, 0.4]} rotation={[0.2, 0.6, -0.2]}>
          <cylinderGeometry args={[0.06, 0.06, 1.2, 32]} />
          <meshStandardMaterial color={"#f59e0b"} />
        </mesh>
        <mesh position={[-1.6, 0.1, 0.4]} rotation={[0.2, 0.6, -0.2]}>
          <coneGeometry args={[0.06, 0.2, 32]} />
          <meshStandardMaterial color={"#facc15"} />
        </mesh>
      </Float>

      <Stars radius={80} depth={30} count={7000} factor={4} saturation={0} fade />
    </>
  )
}

/* Scene: Code Lab (floating symbols + torus + grid) */
function CodeLabScene() {
  return (
    <>
      <Grid infiniteGrid sectionColor={"#d946ef"} cellColor={"#2ee2b7"} position={[0, -0.5, 0]} />
      <Float speed={2} rotationIntensity={1} floatIntensity={1.3}>
        <Text position={[-1.2, 1.3, 0]} font="/fonts/Geist-Bold.ttf" color="#d946ef" fontSize={0.8}>
          {"<"}
        </Text>
        <Text position={[-0.4, 1.3, 0]} font="/fonts/Geist-Bold.ttf" color="#22c55e" fontSize={0.8}>
          {"/>"}
        </Text>
        <Text position={[0.9, 1.0, 0]} font="/fonts/Geist-Bold.ttf" color="#a78bfa" fontSize={0.6}>
          {"{ }"}
        </Text>
        <mesh position={[0, 0.8, 0]}>
          <torusKnotGeometry args={[0.6, 0.18, 200, 32, 2, 3]} />
          <meshStandardMaterial color={"#8b5cf6"} metalness={0.5} roughness={0.3} />
        </mesh>
      </Float>
      <Stars radius={80} depth={30} count={6000} factor={4} saturation={0} fade />
    </>
  )
}

/* Scene: Atom (nucleus + electron orbits) */
function AtomScene() {
  const orbit = useMemo(() => new THREE.EllipseCurve(0, 0, 1.8, 1.1, 0, 2 * Math.PI, false, 0), [])
  const points = orbit.getSpacedPoints(100).map((p) => new THREE.Vector3(p.x, 0, p.y))

  return (
    <>
      <Grid infiniteGrid sectionColor={"#22c55e"} cellColor={"#d946ef"} position={[0, -0.5, 0]} />
      <Float speed={1.5} rotationIntensity={0.8} floatIntensity={1}>
        {/* Nucleus */}
        <mesh position={[0, 1.2, 0]}>
          <sphereGeometry args={[0.45, 32, 32]} />
          <meshStandardMaterial color={"#d946ef"} metalness={0.5} roughness={0.2} />
        </mesh>

        {/* Orbits */}
        <Line points={points} color="#22c55e" lineWidth={2} />
        <Line points={points.map((p) => new THREE.Vector3(p.x, p.z * 0.3, p.y))} color="#a78bfa" lineWidth={2} />
        <Line
          points={points.map((p) => new THREE.Vector3(p.x * 0.7, p.z * 0.7, p.y * 0.7))}
          color="#f59e0b"
          lineWidth={2}
        />

        {/* Electrons */}
        <Electron radius={1.8} speed={1.2} color="#22c55e" height={0} />
        <Electron radius={1.8} speed={1.6} color="#a78bfa" height={0.3} />
        <Electron radius={1.25} speed={2.0} color="#f59e0b" height={-0.25} />
      </Float>
      <Stars radius={80} depth={30} count={5000} factor={4} saturation={0} fade />
    </>
  )
}

function Electron({ radius, speed, color, height }: { radius: number; speed: number; color: string; height: number }) {
  // Simple animation via shaderless rotation using three's built-in time uniform
  const ref = React.useRef<THREE.Mesh>(null)
  useFrame((state) => {
    const t = state.clock.getElapsedTime() * speed
    const x = Math.cos(t) * radius
    const z = Math.sin(t) * radius * 0.6
    if (ref.current) {
      ref.current.position.set(x, 1.2 + height, z)
    }
  })
  return (
    <mesh ref={ref}>
      <sphereGeometry args={[0.08, 16, 16]} />
      <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.6} />
    </mesh>
  )
}

// Need useFrame
import { useFrame } from "@react-three/fiber"

/* Scene: Books (stacked books + labels) */
function BooksScene() {
  const books = [
    { color: "#f59e0b", label: "Math", pos: [-1.4, 0.4, 0.2], rot: [0.1, 0.3, 0.06] },
    { color: "#22c55e", label: "Biology", pos: [-0.3, 0.7, -0.1], rot: [0.06, -0.3, -0.03] },
    { color: "#a78bfa", label: "CS", pos: [0.9, 1.0, 0.1], rot: [-0.08, 0.2, 0.05] },
  ]
  return (
    <>
      <Grid infiniteGrid sectionColor={"#a78bfa"} cellColor={"#22c55e"} position={[0, -0.5, 0]} />
      <Float speed={1.2} rotationIntensity={0.8} floatIntensity={0.9}>
        {books.map((b, i) => (
          <group key={i} position={[b.pos[0], b.pos[1] + 0.7, b.pos[2]]} rotation={[b.rot[0], b.rot[1], b.rot[2]]}>
            <mesh>
              <boxGeometry args={[1.6, 0.25, 1]} />
              <meshStandardMaterial color={b.color} metalness={0.2} roughness={0.6} />
            </mesh>
            <Text
              position={[0, 0.001, 0.55]}
              rotation={[-Math.PI / 2, 0, 0]}
              font="/fonts/Geist-Bold.ttf"
              fontSize={0.18}
              color="#0b0f1a"
              anchorX="center"
              anchorY="middle"
            >
              {b.label}
            </Text>
          </group>
        ))}
      </Float>
      <Stars radius={80} depth={30} count={6000} factor={4} saturation={0} fade />
    </>
  )
}
