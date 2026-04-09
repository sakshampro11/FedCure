"use client";

import { useState } from "react";
import { registerHospital } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { AlertCircle, CheckCircle2, Copy, Activity, ArrowLeft, ShieldCheck, Loader2 } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Image from "next/image";

export default function RegisterPage() {
  const [formData, setFormData] = useState({ name: "", location: "", admin_email: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [copied, setCopied] = useState(false);
  const router = useRouter();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    
    try {
      const response = await registerHospital(formData);
      if (response.api_key) {
        setApiKey(response.api_key);
      } else {
        throw new Error("API key not returned from server.");
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || err.message || "Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(apiKey);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex flex-col md:flex-row min-h-screen w-full bg-white overflow-hidden animate-in fade-in slide-in-from-bottom-8 duration-700">
      
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
            Join the Future of Medical AI.
          </h2>
          <p className="text-white/90 text-lg drop-shadow shadow-black/20">
            Securely register your institution and start training privacy-preserving models today.
          </p>
        </div>
      </div>

      {/* Right side: Register Form / Success State */}
      <div className="flex-1 flex flex-col justify-center items-center p-8 md:p-16 lg:p-24 bg-white relative">
        
        {/* Back to Home Link */}
        <div className="absolute top-8 left-8">
          <Link href="/" className="flex items-center gap-2 text-slate-500 hover:text-slate-900 transition-colors group">
            <ArrowLeft className="h-4 w-4 transition-transform group-hover:-translate-x-1" />
            <span className="text-sm font-medium">Back to Home</span>
          </Link>
        </div>

        <div className="w-full max-w-md space-y-10">
          
          {apiKey ? (
            /* Success State */
            <div className="space-y-8 animate-in fade-in zoom-in-95 duration-500">
              <div className="space-y-3">
                <div className="bg-green-50 w-16 h-16 rounded-3xl flex items-center justify-center mb-6 border border-green-100 shadow-sm shadow-green-200/50">
                  <CheckCircle2 className="h-8 w-8 text-green-600" />
                </div>
                <h1 className="text-4xl font-bold tracking-tight text-slate-900">Registration Successful</h1>
                <p className="text-slate-500 text-lg">
                  Your hospital has been registered on the FedCure network.
                </p>
              </div>

              <div className="bg-amber-50 border border-amber-200 text-amber-800 p-6 rounded-2xl space-y-3 text-sm flex items-start gap-4">
                <AlertCircle className="h-6 w-6 text-amber-600 mt-1 shrink-0" />
                <div>
                  <p className="font-bold text-amber-900 text-base">Save your API key securely</p>
                  <p className="text-amber-800/80 leading-relaxed">
                    We will not show it to you again. This key is required to log in and participate in federated training sessions.
                  </p>
                </div>
              </div>
              
              <div className="space-y-4">
                <Label className="text-slate-700 font-semibold tracking-wide uppercase text-xs">Your Private API Key</Label>
                <div className="flex gap-3">
                  <div className="flex-1 h-14 bg-slate-50 border border-slate-200 rounded-xl flex items-center px-4 font-mono text-sm text-slate-700 overflow-hidden">
                    {apiKey}
                  </div>
                  <Button variant="outline" className="h-14 w-14 rounded-xl border-slate-200 hover:bg-slate-50 transition-all shrink-0" onClick={copyToClipboard} title="Copy to clipboard">
                    {copied ? <CheckCircle2 className="h-5 w-5 text-green-600" /> : <Copy className="h-5 w-5" />}
                  </Button>
                </div>
              </div>

              <Button className="w-full h-14 bg-blue-600 hover:bg-blue-700 text-white text-lg font-semibold rounded-xl shadow-xl shadow-blue-500/20 transition-all" onClick={() => router.push("/login")}>
                Proceed to Login
                <Activity className="ml-2 h-5 w-5" />
              </Button>
            </div>
          ) : (
            /* Registration Form */
            <>
              <div className="space-y-3">
                <div className="bg-blue-50 w-14 h-14 rounded-2xl flex items-center justify-center mb-6">
                  <ShieldCheck className="h-7 w-7 text-blue-600" />
                </div>
                <h1 className="text-4xl font-bold tracking-tight text-slate-900">Register Hospital</h1>
                <p className="text-slate-500 text-lg">
                  Join the FedCure network to participate in federated learning.
                </p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="name" className="text-slate-700 font-semibold tracking-wide uppercase text-xs pl-1">Hospital Name</Label>
                    <Input 
                      id="name" 
                      name="name"
                      placeholder="Central City Hospital" 
                      required 
                      className="h-14 bg-slate-50/50 border-slate-200 focus:ring-blue-500/20 rounded-xl"
                      value={formData.name}
                      onChange={handleChange}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="location" className="text-slate-700 font-semibold tracking-wide uppercase text-xs pl-1">Location</Label>
                    <Input 
                      id="location" 
                      name="location"
                      placeholder="New York, NY" 
                      required 
                      className="h-14 bg-slate-50/50 border-slate-200 focus:ring-blue-500/20 rounded-xl"
                      value={formData.location}
                      onChange={handleChange}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="admin_email" className="text-slate-700 font-semibold tracking-wide uppercase text-xs pl-1">Admin Email Address</Label>
                    <Input 
                      id="admin_email" 
                      name="admin_email"
                      type="email" 
                      placeholder="admin@hospital.com" 
                      required 
                      className="h-14 bg-slate-50/50 border-slate-200 focus:ring-blue-500/20 rounded-xl"
                      value={formData.admin_email}
                      onChange={handleChange}
                    />
                  </div>
                </div>
                
                {error && (
                  <p className="text-sm font-medium text-red-500 bg-red-50 p-4 rounded-xl border border-red-100">
                    {error}
                  </p>
                )}

                <Button type="submit" className="w-full h-14 bg-blue-600 hover:bg-blue-700 text-white text-lg font-semibold rounded-xl shadow-xl shadow-blue-500/20 transition-all mt-4" disabled={loading}>
                  {loading ? <><Loader2 className="mr-2 h-5 w-5 animate-spin" /> Registering...</> : "Complete Registration"}
                  {!loading && <ArrowLeft className="ml-2 h-5 w-5 rotate-180" />}
                </Button>
              </form>

              <div className="pt-8 border-t border-slate-100 flex flex-col items-center gap-4">
                <p className="text-slate-500">
                  Already registered?{" "}
                  <Link href="/login" className="text-blue-600 font-bold hover:underline transition-all">
                    Login here
                  </Link>
                </p>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

