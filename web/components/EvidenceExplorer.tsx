"use client";
import { useEffect, useState } from "react";

type ToolEvent = {tool:string;arguments:Record<string,unknown>;result:unknown};
type Run = {scenario_id:string;model:string;seed:number;run_id:string;verdict:string;expected:unknown;actual:unknown;security_checks:Record<string,boolean>;tool_trace:ToolEvent[]};
type Evidence = {status:string;note:string;runs:Run[]};
const pretty=(value:unknown)=>JSON.stringify(value,null,2);
export default function EvidenceExplorer(){
 const [data,setData]=useState<Evidence|null>(null);
 const [error,setError]=useState("");
 const [selected,setSelected]=useState(0);
 useEffect(()=>{let active=true;fetch("/data/evidence.json").then(r=>{if(!r.ok)throw new Error("Evidence unavailable");return r.json()}).then((d:Evidence)=>{if(active)setData(d)}).catch(()=>{if(active)setError("Recorded evidence could not be loaded.")});return()=>{active=false}},[]);
 const run=data?.runs[selected];
 return <section id="evidence" className="max-w-7xl mx-auto px-6 lg:px-10 py-20">
 <div className="flex flex-wrap justify-between items-end gap-5 mb-8"><div><p className="text-mint text-xs tracking-[.2em] uppercase mb-4">Recorded model behavior</p><h2 className="text-3xl md:text-5xl font-semibold tracking-tight">Explore real tool traces.</h2><p className="mt-4 text-white/50 max-w-2xl">Representative recorded NVIDIA API benchmark runs. Synthetic orders only; preliminary and not independently verified.</p></div><a className="text-sm underline text-white/70" href="https://github.com/Darkhero766/HyperGen/blob/feature/mission2-benchmark/results/results.json">Full 40-run evidence</a></div>
 <div className="glass rounded-3xl p-5 md:p-8">
 {error?<p role="alert" className="text-amber-200">{error}</p>:!run?<p className="text-white/60">Loading recorded evidence…</p>:<>
 <label htmlFor="scenario-evidence" className="block text-xs uppercase tracking-widest text-white/50 mb-3">Scenario</label>
 <select id="scenario-evidence" value={selected} onChange={e=>setSelected(Number(e.target.value))} className="w-full max-w-lg bg-[#17171d] text-white border border-white/20 rounded-xl p-3">{data!.runs.map((r,i)=><option key={r.run_id} value={i}>{r.scenario_id.replaceAll("_"," ")}</option>)}</select>
 <div className="mt-5 flex flex-wrap gap-3 text-sm"><span className="rounded-full border border-white/20 px-3 py-1">{run.verdict}</span><span className="text-white/50">Seed {run.seed} · {run.tool_trace.length} recorded tool calls</span></div>
 <div className="mt-7 space-y-4">{run.tool_trace.map((event,i)=><div key={i} className="border border-white/10 rounded-2xl p-4 md:p-6"><div className="text-mint text-sm font-mono mb-3">{i+1}. {event.tool}</div><div className="grid md:grid-cols-2 gap-4"><div><p className="text-xs text-white/50 mb-2">Arguments</p><pre className="text-xs text-white/80 whitespace-pre-wrap break-all">{pretty(event.arguments)}</pre></div><div><p className="text-xs text-white/50 mb-2">Tool result</p><pre className="text-xs text-white/80 whitespace-pre-wrap break-all">{pretty(event.result)}</pre></div></div></div>)}</div>
 <div className="mt-6 grid md:grid-cols-2 gap-4">{[["Expected state",run.expected],["Observed state",run.actual]].map(([label,value])=><div key={String(label)} className="border border-white/10 rounded-xl p-4"><p className="text-xs text-white/50 mb-3">{String(label)}</p><pre className="text-xs whitespace-pre-wrap break-all text-white/80">{pretty(value)}</pre></div>)}</div>
 <p className="text-xs text-white/40 mt-6">Run ID: {run.run_id} · These are recorded tool outcomes, not live calls. Passing synthetic cases does not establish production security.</p>
 </>}
 </div></section>;
}
