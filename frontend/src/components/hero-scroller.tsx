"use client";

import Image from "next/image";

const images = [
  { src: "/hero/heart-rate.png", alt: "Heart Rate Monitor" },
  { src: "/hero/global-network.png", alt: "Global Medical Network" },
  { src: "/hero/patients-india.png", alt: "Medical Context India" },
  { src: "/hero/hospital-main.png", alt: "Modern Hospital Architecture" },
  { src: "/hero/risk-score.png", alt: "Heart Risk Assessment" },
];

export function HeroScroller() {
  // We duplicate the array to create a seamless loop
  const scrollImages = [...images, ...images];

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {/* Container for the scrolling row */}
      <div className="flex w-[200%] h-full animate-infinite-scroll">
        {scrollImages.map((image, index) => (
          <div 
            key={index} 
            className="relative w-[10%] h-full shrink-0 px-2"
          >
            <div className="relative w-full h-full overflow-hidden rounded-[2rem] border border-white/10 shadow-2xl">
              <Image
                src={image.src}
                alt={image.alt}
                fill
                className="object-cover opacity-80"
                priority={index < 5}
              />
              {/* Individual image overlay for depth */}
              <div className="absolute inset-0 bg-blue-900/10 mix-blend-overlay" />
            </div>
          </div>
        ))}
      </div>

      {/* Global Hero Overlays */}
      <div className="absolute inset-0 bg-white/40 backdrop-blur-[2px]" />
      <div className="absolute inset-0 bg-gradient-to-b from-white via-white/20 to-white" />
    </div>
  );
}
