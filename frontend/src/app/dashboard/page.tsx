"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getDashboardMetrics, predictHeartDisease } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { ShieldCheck, Activity, Users, Settings, Database, Server, RefreshCw } from "lucide-react";

export default function DashboardPage() {
  const router = useRouter();
  
  // Dashboard Metrics State
  const [metrics, setMetrics] = useState({
    current_round: 0,
    participating_hospitals: 0,
    epsilon: 0,
    latest_accuracy: 0,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    history: [] as any[]
  });
  
  // Prediction Form State
  const [predicting, setPredicting] = useState(false);
  const [predictionResult, setPredictionResult] = useState<{score: number, level: string} | null>(null);
  const [form, setForm] = useState({
    age: "",
    sex: "1", // 1: male, 0: female
    cp: "0",
    trestbps: "",
    chol: "",
    fbs: "0",
    restecg: "0",
    thalach: "",
    exang: "0",
    oldpeak: "",
    slope: "1",
    ca: "0",
    thal: "2"
  });

  const fetchMetrics = async () => {
    try {
      const data = await getDashboardMetrics();
      
      const rounds = data.rounds || [];
      const latestRound = rounds.length > 0 ? rounds[rounds.length - 1] : null;
      
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const history = rounds.map((r: any) => ({
        round: r.round_number,
        federatedModel: parseFloat((r.accuracy_federated * 100).toFixed(1)),
        centralizedBaseline: parseFloat((r.accuracy_baseline * 100).toFixed(1)),
      }));

      setMetrics({
        current_round: latestRound ? latestRound.round_number : 0,
        participating_hospitals: latestRound ? latestRound.num_hospitals : 0,
        epsilon: latestRound ? latestRound.epsilon : 0,
        latest_accuracy: latestRound ? latestRound.accuracy_federated : 0,
        history: history,
      });
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      if (err?.response?.status === 401) {
        localStorage.removeItem("fedcure_jwt");
        router.push("/login");
      }
      console.error("Failed to fetch metrics", err);
    }
  };

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 10000);
    return () => clearInterval(interval);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handlePredictChange = (name: string, value: string | null) => {
    if (value !== null) {
      setForm(prev => ({ ...prev, [name]: value }));
    }
  };

  const handlePredictSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setPredicting(true);
    setPredictionResult(null);
    try {
      // Convert values to numbers using standard mapping
      const submitData = {
        age: Number(form.age),
        sex: Number(form.sex),
        cp: Number(form.cp),
        trestbps: Number(form.trestbps),
        chol: Number(form.chol),
        fbs: Number(form.fbs),
        restecg: Number(form.restecg),
        thalach: Number(form.thalach),
        exang: Number(form.exang),
        oldpeak: Number(form.oldpeak),
        slope: Number(form.slope),
        ca: Number(form.ca),
        thal: Number(form.thal)
      };
      
      const res = await predictHeartDisease(submitData);
      setPredictionResult({
        score: res.risk_score,
        level: res.risk_level
      });
    } catch (err) {
      console.error("Prediction failed", err);
      alert("Prediction failed. Ensure model is trained.");
    } finally {
      setPredicting(false);
    }
  };

  const logout = () => {
    localStorage.removeItem("fedcure_jwt");
    router.push("/");
  };

  return (
    <div className="container mx-auto p-4 md:p-8 space-y-8 animate-in fade-in duration-500">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">Hospital Dashboard</h1>
          <p className="text-slate-500">Connected to the FedCure Privacy-Preserving Network</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={fetchMetrics}>
            <RefreshCw className="h-4 w-4 mr-2" /> Refresh Status
          </Button>
          <Button variant="ghost" size="sm" onClick={logout}>
            Disconnect
          </Button>
        </div>
      </div>

      {/* A. Training Status Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Training Round</CardTitle>
            <Settings className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.current_round}</div>
            <p className="text-xs text-muted-foreground mt-1">Active continuous learning</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Participating Hospitals</CardTitle>
            <Users className="h-4 w-4 text-indigo-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.participating_hospitals}</div>
            <p className="text-xs text-muted-foreground mt-1">Global federated network</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Privacy Guarantee (ε)</CardTitle>
            <ShieldCheck className={`h-4 w-4 ${metrics.epsilon <= 1.0 ? 'text-green-600' : 'text-amber-500'}`} />
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold">{metrics.epsilon.toFixed(2)}</span>
              {metrics.epsilon > 0 && metrics.epsilon <= 1.0 && (
                <Badge className="bg-green-100 text-green-800 hover:bg-green-100 border-none">High</Badge>
              )}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Differential privacy budget used</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Model Accuracy</CardTitle>
            <Activity className="h-4 w-4 text-teal-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(metrics.latest_accuracy * 100).toFixed(1)}%</div>
            <p className="text-xs text-muted-foreground mt-1">Avg on validation subset</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-8 grid-cols-1 lg:grid-cols-3">
        
        {/* B. Accuracy Chart */}
        <Card className="col-span-1 lg:col-span-2">
          <CardHeader>
            <CardTitle>Training Accuracy Timeline</CardTitle>
            <CardDescription>
              Comparing the Federated Model against Centralized Baseline. Live update every 10s.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[350px] w-full">
              {metrics.history.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={metrics.history} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" opacity={0.5} />
                    <XAxis dataKey="round" label={{ value: 'Round', position: 'insideBottomRight', offset: -5 }} />
                    <YAxis domain={[0, 100]} label={{ value: 'Accuracy %', angle: -90, position: 'insideLeft' }} />
                    <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                    <Legend verticalAlign="top" height={36}/>
                    <Line type="monotone" name="Federated Model" dataKey="federatedModel" stroke="#2563eb" strokeWidth={3} dot={{r: 4}} activeDot={{ r: 6 }} />
                    <Line type="monotone" name="Centralized Baseline" dataKey="centralizedBaseline" stroke="#94a3b8" strokeDasharray="5 5" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex h-full items-center justify-center text-slate-400">
                  Waiting for first training round to complete...
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* D. Privacy Guarantee Explanation */}
        <Card className="bg-slate-900 text-slate-50 border-none shadow-xl relative overflow-hidden">
          <div className="absolute -right-4 -top-4 opacity-10">
            <Server className="w-32 h-32" />
          </div>
          <CardHeader>
            <CardTitle className="text-blue-400 flex items-center gap-2">
              <ShieldCheck className="w-5 h-5" /> Our Privacy Promise
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm/relaxed text-slate-300">
              Your patient data <strong className="text-white">never leaves your hospital</strong>. 
            </p>
            <div className="p-4 bg-slate-800 rounded-lg space-y-3">
              <div className="flex items-start gap-3 text-sm">
                <Database className="w-4 h-4 text-emerald-400 mt-1 shrink-0" />
                <p className="text-slate-300">Raw patient data remains securely behind your institutional firewall.</p>
              </div>
              <div className="flex items-start gap-3 text-sm">
                <Activity className="w-4 h-4 text-blue-400 mt-1 shrink-0" />
                <p className="text-slate-300">Only encrypted model weight gradients are shared with the aggregator.</p>
              </div>
            </div>
            <div className="text-xs text-slate-400 mt-4 border-t border-slate-800 pt-4">
              <strong>ε (Epsilon)</strong> represents the Differential Privacy budget. A smaller value means higher privacy protection against data inference attacks by adding mathematically calibrated noise.
            </div>
          </CardContent>
        </Card>
      </div>

      {/* C. Heart Disease Prediction Tool */}
      <Card>
        <CardHeader>
          <CardTitle>Clinical Inference Tool</CardTitle>
          <CardDescription>
            Predict heart disease risk utilizing the aggregated federated model.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handlePredictSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
              
              <div className="space-y-2">
                <Label>Age</Label>
                <Input type="number" required placeholder="e.g. 54" value={form.age} onChange={(e) => handlePredictChange("age", e.target.value)} />
              </div>
              
              <div className="space-y-2">
                <Label>Sex</Label>
                <Select value={form.sex} onValueChange={(v) => handlePredictChange("sex", v)}>
                  <SelectTrigger><SelectValue placeholder="Select sex" /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">Male</SelectItem>
                    <SelectItem value="0">Female</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Chest Pain Type</Label>
                <Select value={form.cp} onValueChange={(v) => handlePredictChange("cp", v)}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="0">Typical Angina (0)</SelectItem>
                    <SelectItem value="1">Atypical Angina (1)</SelectItem>
                    <SelectItem value="2">Non-anginal Pain (2)</SelectItem>
                    <SelectItem value="3">Asymptomatic (3)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Resting BP (mm Hg)</Label>
                <Input type="number" required placeholder="e.g. 130" value={form.trestbps} onChange={(e) => handlePredictChange("trestbps", e.target.value)} />
              </div>

              <div className="space-y-2">
                <Label>Cholesterol (mg/dl)</Label>
                <Input type="number" required placeholder="e.g. 240" value={form.chol} onChange={(e) => handlePredictChange("chol", e.target.value)} />
              </div>

              <div className="space-y-2">
                <Label>Fasting Blood Sugar {'>'} 120</Label>
                <Select value={form.fbs} onValueChange={(v) => handlePredictChange("fbs", v)}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">Yes (True)</SelectItem>
                    <SelectItem value="0">No (False)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Resting ECG</Label>
                <Select value={form.restecg} onValueChange={(v) => handlePredictChange("restecg", v)}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="0">Normal (0)</SelectItem>
                    <SelectItem value="1">ST-T Wave Abnormality (1)</SelectItem>
                    <SelectItem value="2">LV Hypertrophy (2)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Max Heart Rate</Label>
                <Input type="number" required placeholder="e.g. 150" value={form.thalach} onChange={(e) => handlePredictChange("thalach", e.target.value)} />
              </div>

              <div className="space-y-2">
                <Label>Exercise Induced Angina</Label>
                <Select value={form.exang} onValueChange={(v) => handlePredictChange("exang", v)}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">Yes</SelectItem>
                    <SelectItem value="0">No</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>ST Depression</Label>
                <Input type="number" step="0.1" required placeholder="e.g. 1.2" value={form.oldpeak} onChange={(e) => handlePredictChange("oldpeak", e.target.value)} />
              </div>

              <div className="space-y-2">
                <Label>ST Slope</Label>
                <Select value={form.slope} onValueChange={(v) => handlePredictChange("slope", v)}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="0">Upsloping (0)</SelectItem>
                    <SelectItem value="1">Flat (1)</SelectItem>
                    <SelectItem value="2">Downsloping (2)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Major Vessels (0-3)</Label>
                <Select value={form.ca} onValueChange={(v) => handlePredictChange("ca", v)}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="0">0</SelectItem>
                    <SelectItem value="1">1</SelectItem>
                    <SelectItem value="2">2</SelectItem>
                    <SelectItem value="3">3</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Thalassemia</Label>
                <Select value={form.thal} onValueChange={(v) => handlePredictChange("thal", v)}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">Normal (1)</SelectItem>
                    <SelectItem value="2">Fixed Defect (2)</SelectItem>
                    <SelectItem value="3">Reversable Defect (3)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

            </div>

            <div className="flex flex-col md:flex-row gap-6 mt-6 items-end">
              <Button type="submit" size="lg" className="bg-blue-600 hover:bg-blue-700 w-full md:w-64" disabled={predicting}>
                {predicting ? "Running Inference..." : "Predict Risk"}
              </Button>

              {predictionResult && (
                <div className="flex-1 w-full bg-slate-50 border rounded-lg p-4 flex items-center justify-between">
                  <div>
                    <p className="text-sm text-slate-500 font-medium">Model Inference Result</p>
                    <p className="text-3xl font-bold mt-1">
                      Risk Score: {(predictionResult.score * 100).toFixed(1)}%
                    </p>
                  </div>
                  <Badge 
                    className={`text-lg px-4 py-2 ${
                      predictionResult.level === 'High' ? 'bg-red-100 text-red-800 hover:bg-red-200' :
                      predictionResult.level === 'Moderate' ? 'bg-amber-100 text-amber-800 hover:bg-amber-200' :
                      'bg-green-100 text-green-800 hover:bg-green-200'
                    }`}
                  >
                    {predictionResult.level} Risk
                  </Badge>
                </div>
              )}
            </div>
            
          </form>
        </CardContent>
      </Card>

      {/* E. Local Node Installation Guide */}
      <Card className="bg-slate-900 text-slate-50 border-none shadow-xl relative overflow-hidden">
        <div className="absolute -right-4 -top-4 opacity-10">
          <Server className="w-32 h-32" />
        </div>
        <CardHeader>
          <CardTitle className="text-blue-400 flex items-center gap-2">
            <Server className="h-5 w-5" />
            Participate in Training (Local Node Setup)
          </CardTitle>
          <CardDescription className="text-slate-400">
            Execute the following command on your hospital&apos;s localized, firewalled servers where private patient data resides. 
            This script downloads the current global model, trains locally, adds differential privacy noise, and securely submits the weight gradients.
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-2 space-y-4">
           <div className="bg-slate-800/50 p-4 rounded-md overflow-x-auto border border-slate-700">
             <pre className="text-sm text-blue-300 font-mono">
{`# 1. Configure your Hospital credentials
export API_KEY="<your-api-key>"
export HOSPITAL_ID="<your-hospital-id>"
export SERVER_URL="http://localhost:8000" # Update to your server's IP if remote

# 2. Run the federated learning client using Docker
docker build -t fedcure-client ./client
docker run --net=host \\
           --env API_KEY=$API_KEY \\
           --env HOSPITAL_ID=$HOSPITAL_ID \\
           --env SERVER_URL=$SERVER_URL \\
           fedcure-client`}
             </pre>
           </div>
           <div className="text-xs text-slate-400 mt-4 border-t border-slate-800 pt-4">
             Ensure <code className="bg-slate-800 px-1 py-0.5 rounded text-slate-300">heart_disease_data.csv</code> is placed inside the client directory. You can customize <code className="bg-slate-800 px-1 py-0.5 rounded text-slate-300">NUM_ROUNDS</code> and <code className="bg-slate-800 px-1 py-0.5 rounded text-slate-300">EPOCHS_PER_ROUND</code> via environment variables to alter the training loop.
             <p className="mt-2 text-blue-400/80">Recommended: 5-10 rounds with 3-5 local epochs per round for optimal convergence.</p>
           </div>
        </CardContent>
      </Card>

    </div>
  );
}
