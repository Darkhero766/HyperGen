"use client";
import dynamic from "next/dynamic";
import { useEffect,useState } from "react";
const World=dynamic(()=>import("./AgentWorld"),{ssr:false});
export default function HeroScene(){
 const [enabled,setEnabled]=useState(false);
 useEffect(()=>{
  const motion=window.matchMedia("(prefers-reduced-motion: reduce)");
  const wide=window.matchMedia("(min-width: 900px)");
  const update=()=>setEnabled(wide.matches&&!motion.matches&&(navigator.hardwareConcurrency??4)>=4);
  update();wide.addEventListener("change",update);motion.addEventListener("change",update);
  return()=>{wide.removeEventListener("change",update);motion.removeEventListener("change",update)};
 },[]);
 return <div className="absolute inset-0 overflow-hidden pointer-events-none" aria-hidden="true">{enabled?<World/>:<div className="absolute right-[15%] top-[24%] w-64 h-64 rounded-[3rem] border border-violet/30 rotate-12 bg-violet/5 shadow-[0_0_140px_40px_rgba(133,106,255,.18)]"/>}</div>;
}
