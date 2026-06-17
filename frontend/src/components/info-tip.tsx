"use client";

import { Info } from "lucide-react";

interface InfoTipProps {
  text: string;
}

export function InfoTip({ text }: InfoTipProps) {
  return (
    <span className="relative group inline-flex items-center ml-1.5 cursor-help">
      <Info className="h-3.5 w-3.5 text-slate-400 group-hover:text-blue-500 transition-colors" />
      <span className="pointer-events-none absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-56 rounded-lg bg-slate-900 px-3 py-2 text-xs leading-relaxed text-slate-200 shadow-xl opacity-0 scale-95 group-hover:opacity-100 group-hover:scale-100 transition-all duration-200 z-50">
        {text}
        <span className="absolute top-full left-1/2 -translate-x-1/2 -mt-px border-4 border-transparent border-t-slate-900" />
      </span>
    </span>
  );
}
