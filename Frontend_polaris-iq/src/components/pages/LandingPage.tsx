import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
    ArrowRight,
    BarChart3,
    BrainCircuit,
    CheckCircle2,
    Database,
    Play,
    Shield,
    Sparkles,
    Wand2,
} from 'lucide-react';
import { fetchHealth } from '../../services/api';
import type { PageId } from '../layout/Sidebar';

interface LandingPageProps {
    onEnter: (page?: PageId) => void;
}

const featureCards = [
    {
        icon: BrainCircuit,
        title: 'Ask In Plain English',
        description: 'Turn natural language questions into robust analytics workflows without writing SQL.',
    },
    {
        icon: BarChart3,
        title: 'Explainable Results',
        description: 'Get generated insights, model outputs, and visualizations with clear execution metadata.',
    },
    {
        icon: Shield,
        title: 'Runs Locally',
        description: 'Your DuckDB data stays on your machine while PolarisIQ performs fast multi-engine analysis.',
    },
];

const quickSteps = [
    'Ingest a CSV, Excel, JSON, or Parquet file',
    'Pick a table and ask a question in Query Studio',
    'Review insights, charts, and model-driven explanations',
];

const LandingPage = ({ onEnter }: LandingPageProps) => {
    const [backendOnline, setBackendOnline] = useState(false);

    useEffect(() => {
        fetchHealth()
            .then(() => setBackendOnline(true))
            .catch(() => setBackendOnline(false));
    }, []);

    return (
        <div className="min-h-screen bg-[#05070f] text-slate-100 relative overflow-hidden">
            <div className="pointer-events-none absolute inset-0">
                <div className="absolute -top-40 -left-20 h-[420px] w-[420px] rounded-full bg-cyan-500/10 blur-3xl" />
                <div className="absolute top-1/4 -right-20 h-[420px] w-[420px] rounded-full bg-primary/20 blur-3xl" />
                <div className="absolute -bottom-40 left-1/4 h-[360px] w-[360px] rounded-full bg-emerald-500/10 blur-3xl" />
            </div>

            <div className="relative z-10 max-w-7xl mx-auto px-6 md:px-10">
                <header className="h-20 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-primary flex items-center justify-center shadow-[0_0_22px_rgba(34,211,238,0.25)]">
                            <Sparkles size={18} className="text-white" />
                        </div>
                        <div>
                            <p className="text-lg font-semibold tracking-tight">PolarisIQ</p>
                            <p className="text-xs text-slate-400">AI Analytics Workspace</p>
                        </div>
                    </div>

                    <div className="flex items-center gap-3">
                        <span className={`text-xs px-3 py-1.5 rounded-full border ${
                            backendOnline
                                ? 'text-emerald-300 bg-emerald-500/10 border-emerald-500/30'
                                : 'text-amber-300 bg-amber-500/10 border-amber-500/30'
                        }`}>
                            {backendOnline ? 'Backend Connected' : 'Backend Offline'}
                        </span>
                        <button
                            onClick={() => onEnter('home')}
                            className="px-4 py-2 rounded-lg border border-white/15 text-sm text-slate-200 hover:bg-white/5 transition-colors"
                        >
                            Enter App
                        </button>
                    </div>
                </header>

                <main className="pt-10 pb-16 md:pt-14 md:pb-20">
                    <div className="grid lg:grid-cols-2 gap-10 items-center">
                        <div>
                            <motion.div
                                initial={{ opacity: 0, y: 16 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.45 }}
                                className="inline-flex items-center gap-2 mb-5 px-3 py-1.5 rounded-full border border-cyan-400/30 bg-cyan-400/10 text-cyan-200 text-xs"
                            >
                                <Wand2 size={12} />
                                Local-first analytics with AI guidance
                            </motion.div>

                            <motion.h1
                                initial={{ opacity: 0, y: 18 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.5, delay: 0.05 }}
                                className="text-4xl md:text-5xl lg:text-6xl font-black tracking-tight leading-[1.05]"
                            >
                                Ask your data
                                <span className="block text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 via-emerald-300 to-primary">
                                    and get explainable answers
                                </span>
                            </motion.h1>

                            <motion.p
                                initial={{ opacity: 0, y: 18 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.5, delay: 0.1 }}
                                className="mt-5 text-slate-300 max-w-xl"
                            >
                                PolarisIQ combines DuckDB, sklearn, and visualization tooling into one guided interface for
                                data exploration, correlation analysis, feature insights, and predictive workflows.
                            </motion.p>

                            <motion.div
                                initial={{ opacity: 0, y: 18 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.5, delay: 0.15 }}
                                className="mt-8 flex flex-wrap gap-3"
                            >
                                <button
                                    onClick={() => onEnter('query')}
                                    className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-primary text-white font-semibold hover:brightness-110 transition-all shadow-[0_10px_30px_rgba(34,211,238,0.22)]"
                                >
                                    <Play size={16} />
                                    Open Query Studio
                                </button>

                                <button
                                    onClick={() => onEnter('workspace')}
                                    className="inline-flex items-center gap-2 px-5 py-3 rounded-xl border border-white/15 text-slate-200 hover:bg-white/5 transition-colors"
                                >
                                    Browse Data Workspace
                                    <ArrowRight size={15} />
                                </button>
                            </motion.div>
                        </div>

                        <motion.div
                            initial={{ opacity: 0, y: 16 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.55, delay: 0.12 }}
                            className="rounded-2xl border border-white/10 bg-slate-950/60 backdrop-blur-xl p-6 shadow-[0_18px_50px_rgba(0,0,0,0.4)]"
                        >
                            <div className="flex items-center justify-between mb-5">
                                <div className="flex items-center gap-2 text-sm text-slate-300">
                                    <Database size={16} className="text-cyan-300" />
                                    Live Analysis Snapshot
                                </div>
                                <span className="text-[11px] text-emerald-300 px-2 py-1 rounded border border-emerald-500/30 bg-emerald-500/10">
                                    Ready
                                </span>
                            </div>

                            <div className="space-y-3">
                                {quickSteps.map((step, idx) => (
                                    <div key={idx} className="flex items-start gap-3 p-3 rounded-lg bg-white/5 border border-white/10">
                                        <CheckCircle2 size={16} className="text-cyan-300 mt-0.5" />
                                        <p className="text-sm text-slate-200">{step}</p>
                                    </div>
                                ))}
                            </div>

                            <div className="mt-5 p-3 rounded-lg bg-gradient-to-r from-cyan-500/10 to-primary/10 border border-cyan-500/20">
                                <p className="text-xs text-cyan-100 font-medium">Suggested starter prompt</p>
                                <p className="text-sm text-slate-200 mt-1">
                                    "Run logistic regression using time_on_site and avg_session_time to predict purchase."
                                </p>
                            </div>
                        </motion.div>
                    </div>

                    <section className="mt-14 grid md:grid-cols-3 gap-4">
                        {featureCards.map((feature, idx) => {
                            const Icon = feature.icon;
                            return (
                                <motion.div
                                    key={feature.title}
                                    initial={{ opacity: 0, y: 14 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ duration: 0.45, delay: 0.2 + idx * 0.08 }}
                                    className="rounded-2xl border border-white/10 bg-slate-900/55 p-5"
                                >
                                    <div className="w-10 h-10 rounded-lg bg-cyan-500/10 border border-cyan-500/25 flex items-center justify-center mb-4">
                                        <Icon size={18} className="text-cyan-300" />
                                    </div>
                                    <h3 className="text-base font-semibold text-white">{feature.title}</h3>
                                    <p className="text-sm text-slate-400 mt-2">{feature.description}</p>
                                </motion.div>
                            );
                        })}
                    </section>
                </main>
            </div>
        </div>
    );
};

export default LandingPage;
