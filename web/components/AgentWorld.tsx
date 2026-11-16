"use client";
import { Canvas, useFrame } from "@react-three/fiber";
import { Float, Line, RoundedBox } from "@react-three/drei";
import { useRef } from "react";
import * as THREE from "three";

const nodes: [number,number,number][] = [[-2,1,0],[1.6,1.4,-.5],[-.2,-1.2,.5],[2.7,-1.5,-1]];
function Network(){
 const group=useRef<THREE.Group>(null);
 const packets=useRef<THREE.Mesh[]>([]);
 const paths:[[number,number,number],[number,number,number]][]=[ [nodes[0],nodes[1]],[nodes[1],nodes[2]],[nodes[2],nodes[3]],[nodes[0],nodes[2]] ];
 useFrame(({clock,pointer})=>{
  if(group.current){group.current.rotation.y=THREE.MathUtils.lerp(group.current.rotation.y,pointer.x*.14,.025);group.current.rotation.x=THREE.MathUtils.lerp(group.current.rotation.x,-pointer.y*.1,.025)}
  packets.current.forEach((mesh,i)=>{if(!mesh)return;const [a,b]=paths[i];const t=(clock.elapsedTime*.23+i*.27)%1;mesh.position.set(...new THREE.Vector3(...a).lerp(new THREE.Vector3(...b),t).toArray())});
 });
 return <group ref={group}>
  {nodes.map((p,i)=><Float key={i} speed={1.2+i*.2} rotationIntensity={.12} floatIntensity={.3}><group position={p}>
   <RoundedBox args={[1.65,1.65,1.65]} radius={.12} smoothness={4}><meshPhysicalMaterial color={i===1?"#9d8cff":"#34375d"} metalness={.4} roughness={.25} transparent opacity={.16}/></RoundedBox>
   <lineSegments><edgesGeometry args={[new THREE.BoxGeometry(1.65,1.65,1.65)]}/><lineBasicMaterial color={i===1?"#b4a9ff":"#7e8cbd"} transparent opacity={.7}/></lineSegments>
   <mesh><icosahedronGeometry args={[.3,1]}/><meshBasicMaterial color={i===2?"#a6ffe2":"#b2a7ff"} wireframe/></mesh>
  </group></Float>)}
  {paths.map(([a,b],i)=><group key={i}><Line points={[a,b]} color="#9c93e5" transparent opacity={.32} lineWidth={1}/><mesh ref={el=>{if(el)packets.current[i]=el}}><octahedronGeometry args={[.095,0]}/><meshBasicMaterial color="#a6ffe2"/></mesh></group>)}
 </group>;
}
export default function AgentWorld(){
 return <div aria-hidden="true" className="w-full h-full"><Canvas camera={{position:[0,0,9],fov:44}} dpr={[1,1.5]} gl={{antialias:false,alpha:true}}><ambientLight intensity={1.4}/><pointLight position={[3,5,5]} intensity={18} color="#8d7aff"/><Network/></Canvas></div>;
}
