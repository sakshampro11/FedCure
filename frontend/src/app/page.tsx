import Link from "next/link";
import { Button } from "@/components/ui/button";
import { 
  Activity, 
  Network, 
  LockKeyhole,
  BrainCircuit,
  Database,
  ArrowRight,
  ShieldCheck,
  Server
} from "lucide-react";

import { HeroScroller } from "@/components/hero-scroller";

import { Logo } from "@/components/logo";

export default function Home() {
  return (
    <div className="flex flex-col items-center bg-white min-h-screen text-slate-900 selection:bg-blue-100 w-full">
      
      {/* Navigation Bar - Liquid Glass Pill (Light Version) */}
      <header className="fixed top-6 left-1/2 -translate-x-1/2 z-50 w-[95%] max-w-5xl rounded-2xl border border-slate-200/60 bg-white/70 backdrop-blur-xl backdrop-saturate-150 shadow-[0_8px_32px_0_rgba(31,38,135,0.07)]">
        <div className="px-4 md:px-6 h-16 flex items-center justify-between">
          <Link href="/">
            <Logo />
          </Link>
          
          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-600">
            <Link href="#features" className="hover:text-blue-600 transition-colors">Features</Link>
            <Link href="#how-it-works" className="hover:text-blue-600 transition-colors">How it Works</Link>
          </nav>

          <div className="flex items-center gap-4">
            <Link href="/login" className="text-sm font-medium text-slate-600 hover:text-blue-600 transition-colors hidden sm:block">
              Log in
            </Link>
            <Link href="/register">
              <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white shadow-lg shadow-blue-500/20 border-0 rounded-lg h-9 px-4 hover:-translate-y-0.5 transition-transform">
                Get Started
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative w-full py-40 md:py-64 overflow-hidden">
        
        {/* Background Scroller Layer */}
        <div className="absolute inset-0 z-0">
          <HeroScroller />
        </div>

        <div className="container px-4 md:px-6 mx-auto relative z-10">
          <div className="flex flex-col items-center space-y-8 text-center">
            
            {/* Badge */}
            <div className="inline-flex items-center rounded-full border border-blue-200 bg-white/80 px-3 py-1 text-sm font-medium text-blue-700 backdrop-blur-sm shadow-sm ring-1 ring-blue-600/10 animate-in fade-in zoom-in duration-700">
              <span className="flex h-2 w-2 rounded-full bg-blue-600 mr-2 animate-pulse"></span>
              Federated Learning Core v1.0
            </div>

            <div className="space-y-4 max-w-4xl animate-in fade-in slide-in-from-bottom-4 duration-1000">
              <h1 className="text-6xl font-extrabold tracking-tight sm:text-7xl md:text-8xl lg:text-9xl text-slate-900 drop-shadow-sm">
                Fed<span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">Cure</span>
              </h1>
              <p className="mx-auto max-w-[850px] text-xl md:text-2xl lg:text-3xl text-slate-700 mt-6 leading-relaxed font-medium">
                The Decentralized Network for Heart Health.
              </p>
              <p className="mx-auto max-w-[750px] text-slate-600 text-lg md:text-xl leading-relaxed">
                Connect your institution and contribute to global medical breakthroughs without ever exposing private patient data.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-6 pt-8 w-full justify-center max-w-md mx-auto sm:max-w-none animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-300">
              <Link href="/register">
                <Button size="lg" className="w-full sm:w-auto h-16 px-10 text-lg bg-blue-600 hover:bg-blue-700 text-white shadow-2xl shadow-blue-500/40 transition-all duration-300 hover:-translate-y-1 border-0 rounded-2xl">
                  Register Hospital
                  <ArrowRight className="ml-2 h-6 w-6" />
                </Button>
              </Link>
              <Link href="/login">
                <Button size="lg" className="w-full sm:w-auto h-16 px-10 text-lg bg-slate-950 hover:bg-slate-800 text-white shadow-2xl shadow-slate-900/20 transition-all duration-300 hover:-translate-y-1 border-0 rounded-2xl">
                  Login to Dashboard
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Bento Box Features Section */}
      <section id="features" className="w-full py-24 relative z-10 border-t border-slate-100 bg-slate-50/30 scroll-mt-16">
        <div className="container px-4 md:px-6 mx-auto">
          <div className="mb-16 text-center max-w-3xl mx-auto">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4 text-slate-900">Next-Generation Healthcare AI</h2>
            <p className="text-slate-500 text-lg">Harness the collective intelligence of global hospitals while satisfying strict HIPAA and GDPR compliance.</p>
          </div>

          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 max-w-6xl mx-auto">
            
            {/* Main Feature - Large Card */}
            <div className="lg:col-span-2 group relative overflow-hidden rounded-3xl border border-slate-200/60 bg-white p-8 transition-all duration-500 hover:-translate-y-1 shadow-sm hover:shadow-xl hover:shadow-blue-500/5">
              <div className="absolute right-0 top-0 -mr-16 -mt-16 h-64 w-64 rounded-full bg-blue-50/50 blur-3xl transition-all duration-500 group-hover:bg-blue-100/50"></div>
              <div className="relative z-10 flex flex-col h-full justify-between gap-12">
                <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50 text-blue-600 border border-blue-100 shadow-sm">
                  <LockKeyhole className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold mb-3 text-slate-900">Zero-Trust Data Privacy</h3>
                  <p className="text-slate-500 text-lg leading-relaxed">
                    Patient records are never uploaded or shared. Only differentially private, encrypted model weight gradients are transmitted to the central aggregator, ensuring mathematical guarantees on patient anonymity.
                  </p>
                </div>
              </div>
            </div>

            {/* Feature 2 - Small Card */}
            <div className="group relative overflow-hidden rounded-3xl border border-slate-200/60 bg-white p-8 transition-all duration-500 hover:-translate-y-1 shadow-sm hover:shadow-xl hover:shadow-indigo-500/5">
              <div className="relative z-10 flex flex-col h-full gap-6">
                <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600 border border-indigo-100 shadow-sm">
                  <Activity className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="text-xl font-bold mb-2 text-slate-900">High Accuracy</h3>
                  <p className="text-slate-500">
                    Access a continuously trained generalized model capable of rendering accurate and immediate risk assessments.
                  </p>
                </div>
              </div>
            </div>

            {/* Feature 3 - Small Card */}
            <div className="group relative overflow-hidden rounded-3xl border border-slate-200/60 bg-white p-8 transition-all duration-500 hover:-translate-y-1 shadow-sm hover:shadow-xl hover:shadow-teal-500/5">
              <div className="relative z-10 flex flex-col h-full gap-6">
                <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-teal-50 text-teal-600 border border-teal-100 shadow-sm">
                  <Network className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="text-xl font-bold mb-2 text-slate-900">Federated Network</h3>
                  <p className="text-slate-500">
                    Tap into a global network of medical institutions continuously improving a shared diagnostic model.
                  </p>
                </div>
              </div>
            </div>

            {/* Feature 4 - Medium Card */}
            <div className="sm:col-span-2 relative overflow-hidden rounded-3xl border border-slate-200/60 bg-white p-8 transition-all duration-500 hover:-translate-y-1 shadow-sm hover:shadow-xl hover:shadow-purple-500/5">
              <div className="absolute right-0 bottom-0 max-w-sm translate-x-12 translate-y-12 opacity-[0.03] pointer-events-none grayscale">
                <BrainCircuit className="w-full h-full text-purple-600" />
              </div>
              <div className="relative z-10 flex flex-col md:flex-row gap-8 items-center">
                <div className="flex-1">
                  <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-purple-50 text-purple-600 border border-purple-100 shadow-sm mb-6">
                    <ShieldCheck className="h-6 w-6" />
                  </div>
                  <h3 className="text-2xl font-bold mb-3 text-slate-900">Differential Privacy Built-in</h3>
                  <p className="text-slate-500">
                    Our local training loops automatically inject calibrated Gaussian noise into weight updates before transmission, thwarting model inversion and membership inference attacks.
                  </p>
                </div>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="w-full py-24 relative z-10 scroll-mt-16">
        <div className="container px-4 md:px-6 mx-auto">
          <div className="mb-20 text-center max-w-3xl mx-auto">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4 text-slate-900">How FedCure Works</h2>
            <p className="text-slate-500 text-lg">A seamless, automated pipeline bridging local data and global intelligence.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-12 relative max-w-6xl mx-auto">
            {/* Connecting line for desktop */}
            <div className="hidden md:block absolute top-[45px] left-[10%] right-[10%] h-[1px] bg-slate-200"></div>
            
            {[
              {
                icon: <Database className="h-6 w-6" />,
                title: "1. Local Data",
                desc: "Hospitals retain their strictly private patient datasets locally.",
                borderColor: "group-hover:border-blue-200",
                bgColor: "bg-blue-50",
                textColor: "text-blue-600",
                shadow: "hover:shadow-blue-500/10"
              },
              {
                icon: <BrainCircuit className="h-6 w-6" />,
                title: "2. Local Training",
                desc: "The global model is downloaded and trained locally for a few epochs.",
                borderColor: "group-hover:border-indigo-200",
                bgColor: "bg-indigo-50",
                textColor: "text-indigo-600",
                shadow: "hover:shadow-indigo-500/10"
              },
              {
                icon: <ShieldCheck className="h-6 w-6" />,
                title: "3. Encrypted Sync",
                desc: "Differentially private gradients are securely sent to the cloud.",
                borderColor: "group-hover:border-purple-200",
                bgColor: "bg-purple-50",
                textColor: "text-purple-600",
                shadow: "hover:shadow-purple-500/10"
              },
              {
                icon: <Server className="h-6 w-6" />,
                title: "4. Aggregation",
                desc: "The server averages updates (FedAvg) and distributes the improved model.",
                borderColor: "group-hover:border-teal-200",
                bgColor: "bg-teal-50",
                textColor: "text-teal-600",
                shadow: "hover:shadow-teal-500/10"
              }
            ].map((step, i) => (
              <div key={i} className="relative z-10 flex flex-col items-center text-center group">
                <div className={`w-24 h-24 rounded-3xl flex items-center justify-center mb-8 bg-white border border-slate-100 shadow-sm transition-all duration-300 group-hover:-translate-y-2 group-hover:scale-105 ${step.shadow} overflow-hidden relative`}>
                  <div className={`absolute inset-0 ${step.bgColor} opacity-0 group-hover:opacity-100 transition-all duration-300`}></div>
                  <div className={`${step.textColor} relative z-10 transition-colors duration-300`}>
                    {step.icon}
                  </div>
                </div>
                <h3 className="text-xl font-bold mb-3 text-slate-900">{step.title}</h3>
                <p className="text-slate-500 text-sm leading-relaxed max-w-[200px]">
                  {step.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer CTA */}
      <section className="w-full py-24 relative z-10 border-t border-slate-100 bg-slate-50/20">
        <div className="container px-4 text-center">
          <h2 className="text-3xl font-bold mb-6 text-slate-900">Ready to join the network?</h2>
          <p className="text-slate-500 mb-10 max-w-2xl mx-auto">Start contributing to the global medical AI model today with just a few CLI commands.</p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/register">
              <Button size="lg" className="h-14 px-10 bg-slate-900 text-white hover:bg-slate-800 hover:scale-105 transition-all duration-300 rounded-2xl font-semibold shadow-xl">
                Get Started Now
              </Button>
            </Link>
            <Link href="/login">
              <Button size="lg" className="h-14 px-10 bg-slate-800 text-white hover:bg-slate-700 hover:scale-105 transition-all duration-300 rounded-2xl font-semibold shadow-lg">
                Explore Demo
              </Button>
            </Link>
          </div>
        </div>
      </section>

    </div>
  );
}
