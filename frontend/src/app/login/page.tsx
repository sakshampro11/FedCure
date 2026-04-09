"use client";

import { useState } from "react";
import { loginHospital } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { KeyRound, Activity, ArrowLeft } from "lucide-react";
import Image from "next/image";

export default function LoginPage() {
  const [apiKey, setApiKey] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!apiKey) return;
    
    setLoading(true);
    setError("");
    
    try {
      const response = await loginHospital({ api_key: apiKey });
      if (response.access_token) {
        localStorage.setItem("fedcure_jwt", response.access_token);
        router.push("/dashboard");
      } else {
        throw new Error("Invalid response from server.");
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || err.message || "Invalid API Key. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col md:flex-row min-h-[calc(100vh-0rem)] w-full bg-white overflow-hidden">
      
      {/* Left side: Image and Branding */}
      <div className="hidden md:flex md:w-1/2 relative bg-slate-100 overflow-hidden">
        <Image 
          src="/hospital-auth.png" 
          alt="Modern Hospital Architecture" 
          fill
          className="object-cover"
          priority
        />
        <div className="absolute inset-0 bg-blue-600/10 mix-blend-multiply" />
        
        {/* Branding Overlay */}
        <div className="absolute top-12 left-12 z-10 flex items-center gap-2">
          <div className="bg-white/90 backdrop-blur p-2 rounded-xl shadow-lg border border-white/50">
            <Activity className="h-6 w-6 text-blue-600" />
          </div>
          <span className="text-2xl font-bold tracking-tight text-white drop-shadow-md">
            Fed<span className="text-blue-200">Cure</span>
          </span>
        </div>

        <div className="absolute bottom-12 left-12 z-10 max-w-md">
          <h2 className="text-4xl font-bold text-white mb-4 drop-shadow-md leading-tight">
            Advancing Medicine Through Collaboration.
          </h2>
          <p className="text-white/90 text-lg drop-shadow shadow-black/20">
            Securely access your hospital dashboard and contribute to global health intelligence.
          </p>
        </div>
      </div>

      {/* Right side: Login Form */}
      <div className="flex-1 flex flex-col justify-center items-center p-8 md:p-16 lg:p-24 bg-white relative">
        
        {/* Back to Home Link */}
        <div className="absolute top-8 left-8">
          <Link href="/" className="flex items-center gap-2 text-slate-500 hover:text-slate-900 transition-colors group">
            <ArrowLeft className="h-4 w-4 transition-transform group-hover:-translate-x-1" />
            <span className="text-sm font-medium">Back to Home</span>
          </Link>
        </div>

        <div className="w-full max-w-md space-y-10">
          <div className="space-y-3">
            <div className="bg-blue-50 w-14 h-14 rounded-2xl flex items-center justify-center mb-6">
              <KeyRound className="h-7 w-7 text-blue-600" />
            </div>
            <h1 className="text-4xl font-bold tracking-tight text-slate-900">Hospital Login</h1>
            <p className="text-slate-500 text-lg">
              Enter your hospital&apos;s API key to access the dashboard.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-8">
            <div className="space-y-3">
              <Label htmlFor="apiKey" className="text-slate-700 font-semibold tracking-wide uppercase text-xs">
                Private API Key
              </Label>
              <Input 
                id="apiKey" 
                type="password"
                placeholder="Paste your API key here..." 
                required 
                className="h-14 bg-slate-50/50 border-slate-200 focus:ring-blue-500/20 focus:border-blue-500 rounded-xl transition-all"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
              />
            </div>
            
            {error && (
              <p className="text-sm font-medium text-red-500 bg-red-50 p-4 rounded-xl border border-red-100 animate-in fade-in slide-in-from-top-1">
                {error}
              </p>
            )}

            <Button type="submit" className="w-full h-14 bg-blue-600 hover:bg-blue-700 text-white text-lg font-semibold rounded-xl shadow-xl shadow-blue-500/20 transition-all active:scale-[0.98]" disabled={loading || !apiKey}>
              {loading ? "Authenticating..." : "Login to Dashboard"}
              {!loading && <Activity className="ml-2 h-5 w-5" />}
            </Button>
          </form>

          <div className="pt-8 border-t border-slate-100 flex flex-col items-center gap-4">
            <p className="text-slate-500">
              New to the network?{" "}
              <Link href="/register" className="text-blue-600 font-bold hover:underline transition-all">
                Register Hospital
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

