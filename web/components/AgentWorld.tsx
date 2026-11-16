"use client";
import { Canvas, useFrame } from "@react-three/fiber";
import { Float, Line, RoundedBox, Stars } from "@react-three/drei";
import { useMemo, useRef } from "react";
import * as THREE from "three";

/** Original procedural agent network. No external 3D assets or textures. */
const nodes: [number,number,number][] = [[-2.7,1.5,-.5],[1.45,1.65,-1.4],[-.75,-1.35,.9],[2.85,-1.1,-.7],[.35,.15,1.35]];
const links: [number,number][] = [[0,1],[0,2],[1,3],[2,3],[0,4],[1,4],[2,4],[3,4]];
function Core({index}:{index:number}){
 const active=index===4;
 return <Float speed={.8+index*.15} rotationIntensity={.07} floatIntensity={.17}>
  <group position={nodes[index]} rotation={[.38,.64,.1]}>
   <RoundedBox args={[active?1.85:1.35,active?1.85:1.35,active?1.85:1.35]} radius={.075} smoothness={3}>
    <meshPhysicalMaterial color={active?"#6d56ff":"#111321"} roughness={.22} metalness={.8} transparent opacity={active?.22:.12} depthWrite={false}/>
   </RoundedBox>
   <lineSegments><edgesGeometry args={[new THREE.BoxGeometry(active?1.86:1.36,active?1.86:1.36,active?1.86:1.36)]}/><lineBasicMaterial color={active?"#c2b6ff":"#777cba"} transparent opacity={active?.92:.58}/></lineSegments>
   <mesh rotation={[.4,.2,.1]}><octahedronGeometry args={[active?.64:.28,1]}/><meshPhysicalMaterial color={active?"#a999ff":"#a2b8e9"} emissive={active?"#6951ff":"#292e6a"} emissiveIntensity={active?1.1:.3} wireframe metalness={.8}/></mesh>
   {active&&<mesh><icosahedronGeometry args={[1.24,1]}/><meshBasicMaterial color="#8f7aff" wireframe transparent opacity={.16} depthWrite={false}/></mesh>}
  </group>
 </Float>;
}
function Network(){
 const group=useRef<THREE.Group>(null);
 const packets=useRef<(THREE.Mesh|null)[]>([]);
 const endpoints=useMemo(()=>links.map(([a,b])=>[new THREE.Vector3(...nodes[a]),new THREE.Vector3(...nodes[b])]),[]);
 useFrame(({clock,pointer},delta)=>{
  if(group.current){
   group.current.rotation.y=THREE.MathUtils.damp(group.current.rotation.y,pointer.x*.13,2,delta);
   group.current.rotation.x=THREE.MathUtils.damp(group.current.rotation.x,-pointer.y*.09,2,delta);
   group.current.position.y=Math.sin(clock.elapsedTime*.38)*.07;
  }
  packets.current.forEach((mesh,i)=>{if(!mesh)return;const [a,b]=endpoints[i];const t=(clock.elapsedTime*(.17+i*.009)+i*.21)%1;mesh.position.lerpVectors(a,b,t);const scale=.6+Math.sin(t*Math.PI)*.8;mesh.scale.setScalar(scale)});
 });
 return <group ref={group}>
  {nodes.map((_,i)=><Core index={i} key={i}/>)}
  {endpoints.map(([a,b],i)=><group key={i}>
   <Line points={[a,b]} color="#7f70df" transparent opacity={.28} lineWidth={1}/>
   <mesh ref={el=>{packets.current[i]=el}}><octahedronGeometry args={[.065,0]}/><meshBasicMaterial color="#c8bdff" toneMapped={false}/></mesh>
  </group>)}
  <mesh rotation={[Math.PI/2.6,0,.3]}><torusGeometry args={[3.4,.006,4,110]}/><meshBasicMaterial color="#6151aa" transparent opacity={.28}/></mesh>
  <mesh rotation={[Math.PI/2.25,.25,-.45]}><torusGeometry args={[4.2,.004,4,120]}/><meshBasicMaterial color="#6151aa" transparent opacity={.16}/></mesh>
 </group>;
}
export default function AgentWorld(){
 return <div aria-hidden="true" className="w-full h-full"><Canvas camera={{position:[0,0,10.5],fov:43}} dpr={[1,1.5]} gl={{antialias:false,alpha:true,powerPreference:"low-power"}}>
  <ambientLight intensity={.38}/><pointLight position={[3,4,6]} intensity={15} color="#8d79ff"/><pointLight position={[-4,-2,2]} intensity={5} color="#7294ff"/>
  <Stars radius={30} depth={12} count={140} factor={1.3} saturation={0} fade speed={.12}/>
  <Network/>
 </Canvas></div>;
}
