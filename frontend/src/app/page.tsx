import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Activity, Network, LockKeyhole } from "lucide-react";

export default function Home() {
  return (
    <div className="flex flex-col items-center">
      {/* Hero Section */}
      <section className="w-full py-24 md:py-32 bg-white text-center">
        <div className="container px-4 md:px-6 mx-auto">
          <div className="flex flex-col items-center space-y-4 text-center">
            <div className="space-y-2">
              <h1 className="text-4xl font-bold tracking-tighter sm:text-5xl md:text-6xl text-slate-900">
                Fed<span className="text-blue-600">Cure</span>
              </h1>
              <p className="mx-auto max-w-[700px] text-lg md:text-xl text-slate-600 mt-4">
                Privacy-Preserving Federated Learning for Heart Disease Prediction
              </p>
            </div>
            <p className="mx-auto max-w-[800px] text-slate-500 md:text-lg/relaxed lg:text-base/relaxed xl:text-lg/relaxed py-4">
              Collaborate on training highly accurate machine learning models without sharing sensitive patient data. 
              Our federated learning system ensures data never leaves your hospital&apos;s isolated infrastructure.
            </p>
            <div className="space-x-4 mt-8 flex flex-col sm:flex-row gap-4 sm:gap-0 justify-center">
              <Link href="/register">
                <Button size="lg" className="w-full sm:w-auto h-12 px-8 text-base bg-blue-600 hover:bg-blue-700">
                  Register Hospital
                </Button>
              </Link>
              <Link href="/login">
                <Button size="lg" variant="outline" className="w-full sm:w-auto h-12 px-8 text-base border-blue-200 text-blue-700 hover:bg-blue-50">
                  Login to Dashboard
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="w-full py-16 md:py-24 bg-slate-50">
        <div className="container px-4 md:px-6 mx-auto">
          <div className="grid gap-12 sm:grid-cols-2 lg:grid-cols-3 items-start justify-center">
            <div className="flex flex-col items-center space-y-4 text-center">
              <div className="p-4 bg-blue-100 rounded-full">
                <LockKeyhole className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-bold">Data Privacy Guaranteed</h3>
              <p className="text-slate-500">
                Patient records are never uploaded. Only encrypted model weight updates are transmitted securely to the central aggregator.
              </p>
            </div>
            <div className="flex flex-col items-center space-y-4 text-center">
              <div className="p-4 bg-teal-100 rounded-full">
                <Network className="h-8 w-8 text-teal-600" />
              </div>
              <h3 className="text-xl font-bold">Federated Infrastructure</h3>
              <p className="text-slate-500">
                Tap into a global network of medical institutions continuously improving a shared diagnostic model collaboratively.
              </p>
            </div>
            <div className="flex flex-col items-center space-y-4 text-center sm:col-span-2 lg:col-span-1">
              <div className="p-4 bg-indigo-100 rounded-full">
                <Activity className="h-8 w-8 text-indigo-600" />
              </div>
              <h3 className="text-xl font-bold">High Accuracy Predictions</h3>
              <p className="text-slate-500">
                Access a continuously trained generalized model capable of rendering accurate and immediate heart disease risk assessments.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
