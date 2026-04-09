import React from "react";
import { cn } from "@/lib/utils";

interface LogoProps {
  className?: string;
  iconClassName?: string;
  textClassName?: string;
  hideText?: boolean;
}

export function Logo({ className, iconClassName, textClassName, hideText = false }: LogoProps) {
  return (
    <div className={cn("flex items-center gap-2.5 group cursor-default", className)}>
      {/* Custom SVG Icon combining Heart + Pulse + Network Nodes */}
      <div className={cn(
        "relative flex items-center justify-center bg-blue-600 rounded-xl shadow-lg shadow-blue-500/20 group-hover:bg-blue-700 transition-colors p-2", 
        iconClassName
      )}>
        <svg 
          width="24" 
          height="24" 
          viewBox="0 0 24 24" 
          fill="none" 
          xmlns="http://www.w3.org/2000/svg"
          className="text-white"
        >
          {/* Solid White Heart */}
          <path 
            d="M12 21.35L10.55 20.03C5.4 15.36 2 12.28 2 8.5C2 5.42 4.42 3 7.5 3C9.24 3 10.91 3.81 12 5.09C13.09 3.81 14.76 3 16.5 3C19.58 3 22 5.42 22 8.5C22 12.28 18.6 15.36 13.45 20.04L12 21.35Z" 
            fill="currentColor" 
          />
          
          {/* Light Pulse Wave (Cut-out look) */}
          <path 
            d="M6 11.5H8.5L10 7L13 16L14.5 11.5H18" 
            stroke="#2563eb" 
            strokeWidth="1.5" 
            strokeLinecap="round" 
            strokeLinejoin="round" 
          />
        </svg>
      </div>

      {!hideText && (
        <span className={cn("text-xl font-bold tracking-tight text-slate-900 select-none", textClassName)}>
          Fed<span className="text-blue-600">Cure</span>
        </span>
      )}
    </div>
  );
}
