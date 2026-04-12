"use client";

import { useEffect, useState } from "react";

interface RiskGaugeProps {
  score: number; // 0 to 1
  level: string;
}

export function RiskGauge({ score, level }: RiskGaugeProps) {
  const [progress, setProgress] = useState(0);
  const percentage = Math.round(score * 100);
  
  // Radius: 90, Circumference: 2 * PI * 90 ≈ 565.48
  const radius = 90;
  const strokeDasharray = 2 * Math.PI * radius;
  const strokeDashoffset = strokeDasharray - (strokeDasharray * progress) / 100;

  useEffect(() => {
    // Slower revealed state change
    const timer = setTimeout(() => {
      setProgress(percentage);
    }, 500); // 500ms delay before starting
    return () => clearTimeout(timer);
  }, [percentage]);

  const getColor = (p: number) => {
    if (p < 25) return "stroke-green-500";
    if (p < 50) return "stroke-yellow-400";
    if (p < 75) return "stroke-orange-500";
    return "stroke-red-600";
  };

  const getTextColor = (p: number) => {
    if (p < 25) return "text-green-600";
    if (p < 50) return "text-yellow-600";
    if (p < 75) return "text-orange-600";
    return "text-red-700";
  };

  const getBgColor = (p: number) => {
    if (p < 25) return "bg-green-50 text-green-700 border-green-200";
    if (p < 50) return "bg-yellow-50 text-yellow-700 border-yellow-200";
    if (p < 75) return "bg-orange-50 text-orange-700 border-orange-200";
    return "bg-red-50 text-red-700 border-red-200";
  };

  const ticks = Array.from({ length: 11 }, (_, i) => i * 10);

  return (
    <div className="flex flex-col items-center justify-center p-8 bg-white rounded-3xl shadow-xl border border-slate-100 animate-in zoom-in duration-700">
      <div className="relative w-64 h-64 flex items-center justify-center">
        <svg viewBox="0 0 200 200" className="w-full h-full transform -rotate-90 scale-110">
          <circle
            cx="100"
            cy="100"
            r={radius}
            fill="transparent"
            stroke="currentColor"
            strokeWidth="14"
            className="text-slate-100"
          />
          <circle
            cx="100"
            cy="100"
            r={radius}
            fill="transparent"
            stroke="currentColor"
            strokeWidth="16"
            strokeDasharray={strokeDasharray}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className={`transition-all duration-[3000ms] ease-in-out drop-shadow-md ${getColor(progress)}`}
          />
          {ticks.map((tick) => {
            const angle = (tick / 100) * 360;
            return (
              <line
                key={tick}
                x1="100"
                y1={100 - radius + 8}
                x2="100"
                y2={100 - radius - 8}
                stroke="currentColor"
                strokeWidth="2"
                className="text-slate-300"
                transform={`rotate(${angle}, 100, 100)`}
              />
            );
          })}
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center mt-2">
          <div className="flex items-baseline">
            <span className={`text-6xl font-black tracking-tighter transition-colors duration-1000 ${getTextColor(progress)}`}>
              {progress}
            </span>
            <span className="text-2xl font-bold text-slate-400 ml-1">%</span>
          </div>
          <span className="text-xs font-black uppercase text-slate-400 tracking-[0.2em] mt-1">
            Risk Score
          </span>
        </div>
      </div>
      <div className={`mt-8 px-8 py-3 rounded-2xl border-2 text-lg font-black shadow-lg transform hover:scale-105 transition-transform duration-300 cursor-default ${getBgColor(progress)}`}>
        {level.toUpperCase()} RISK
      </div>
    </div>
  );
}
