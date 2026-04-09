"use client";

import { useState } from "react";
import { loginHospital } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { KeyRound } from "lucide-react";

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
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      setError(err?.response?.data?.detail || err.message || "Invalid API Key. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-4rem)] items-center justify-center p-4">
      <Card className="w-full max-w-md shadow-lg">
        <CardHeader className="space-y-1 text-center">
          <div className="flex justify-center mb-4">
            <div className="p-3 bg-blue-100 rounded-full">
              <KeyRound className="h-6 w-6 text-blue-600" />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold">Hospital Login</CardTitle>
          <CardDescription>
            Enter your hospital&apos;s API key to access the dashboard.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="apiKey">API Key</Label>
              <Input 
                id="apiKey" 
                type="password"
                placeholder="Paste your API key here..." 
                required 
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
              />
            </div>
            
            {error && (
              <p className="text-sm font-medium text-red-500 text-center">{error}</p>
            )}

            <Button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 mt-4" disabled={loading || !apiKey}>
              {loading ? "Authenticating..." : "Login"}
            </Button>
          </form>
        </CardContent>
        <CardFooter className="flex justify-center border-t p-4 mt-2">
          <p className="text-sm text-slate-500">
            Have not joined yet?{" "}
            <Link href="/register" className="text-blue-600 hover:underline">
              Register hospital
            </Link>
          </p>
        </CardFooter>
      </Card>
    </div>
  );
}
