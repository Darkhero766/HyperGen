"use client";
import { motion,useReducedMotion } from "framer-motion";
export default function Reveal({children,className=""}:{children:React.ReactNode;className?:string}){
 const reduce=useReducedMotion();
 return <motion.div className={className} initial={reduce?false:{opacity:0,y:26}} whileInView={{opacity:1,y:0}} viewport={{once:true,amount:.1}} transition={{duration:.65,ease:"easeOut"}}>{children}</motion.div>;
}
