import { useState, useRef, useEffect } from 'react';
import { Send, Terminal, CheckCircle2, Circle, Clock, AlertCircle, Cpu, Sparkles } from 'lucide-react';
import { cn } from '../../lib/utils';
import { sendQuery } from '../../services/api';
import type { QueryResponse } from '../../types/api';

interface ChatMessage {
    role: 'user' | 'assistant' | 'error';
    content: string;
    metadata?: QueryResponse['metadata'];
}

const REASONING_STEPS = [
    'Understanding natural language query',
    'Mapping entities to hybrid OLAP schema',
    'Generating optimized execution plan',
    'Selecting best execution engine',
    'Executing query pipeline',
    'Generating explanation',
];

const QueryStudio = () => {
    const [prompt, setPrompt] = useState('');
    const [tableName, setTableName] = useState('test_table');
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [activeStep, setActiveStep] = useState(-1);
    const chatEndRef = useRef<HTMLDivElement>(null);
    const stepTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Clean up step timer on unmount
    useEffect(() => {
        return () => {
            if (stepTimerRef.current) clearInterval(stepTimerRef.current);
        };
    }, []);

    const startReasoningAnimation = () => {
        setActiveStep(0);
        let step = 0;
        stepTimerRef.current = setInterval(() => {
            step++;
            if (step < REASONING_STEPS.length) {
                setActiveStep(step);
            } else {
                if (stepTimerRef.current) clearInterval(stepTimerRef.current);
            }
        }, 800);
    };

    const stopReasoningAnimation = () => {
        if (stepTimerRef.current) clearInterval(stepTimerRef.current);
        setActiveStep(REASONING_STEPS.length); // all done
    };

    const handleSubmit = async () => {
        const trimmed = prompt.trim();
        if (!trimmed || isLoading) return;

        const userMsg: ChatMessage = { role: 'user', content: trimmed };
        setMessages(prev => [...prev, userMsg]);
        setPrompt('');
        setIsLoading(true);
        startReasoningAnimation();

        try {
            const response = await sendQuery(trimmed, tableName);
            stopReasoningAnimation();

            const assistantMsg: ChatMessage = {
                role: 'assistant',
                content: response.explanation,
                metadata: response.metadata,
            };
            setMessages(prev => [...prev, assistantMsg]);
        } catch (err) {
            stopReasoningAnimation();
            const errorMsg: ChatMessage = {
                role: 'error',
                content: err instanceof Error ? err.message : 'Failed to connect to PolarisIQ backend. Make sure the server is running on port 8000.',
            };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    return (
        <div className="h-full flex gap-6 animate-in fade-in duration-500">
            {/* Left Panel: Chat Interface */}
            <div className="w-1/3 flex flex-col gap-4">
                <div className="glass p-4 rounded-b-none border-b-0 flex-1 flex flex-col overflow-hidden">
                    <div className="flex-1 overflow-y-auto space-y-4 mb-4 scrollbar-hide">
                        {messages.length === 0 && (
                            <div className="flex flex-col items-center justify-center h-full text-center opacity-60">
                                <Sparkles size={32} className="text-primary mb-3" />
                                <p className="text-sm text-slate-400">Ask a question about your data</p>
                                <p className="text-xs text-slate-500 mt-1">e.g. "Show me average salary by education level"</p>
                            </div>
                        )}

                        {messages.map((msg, idx) => (
                            <div key={idx} className="flex gap-3">
                                {msg.role === 'user' ? (
                                    <>
                                        <div className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center shrink-0">
                                            <span className="text-xs font-bold text-slate-300">U</span>
                                        </div>
                                        <div className="bg-slate-800/50 p-3 rounded-2xl rounded-tl-none border border-slate-700/50 text-sm text-slate-300">
                                            {msg.content}
                                        </div>
                                    </>
                                ) : msg.role === 'error' ? (
                                    <>
                                        <div className="w-8 h-8 rounded-full bg-rose-500/20 flex items-center justify-center shrink-0">
                                            <AlertCircle size={14} className="text-rose-400" />
                                        </div>
                                        <div className="bg-rose-500/10 p-3 rounded-2xl rounded-tr-none border border-rose-500/20 text-sm text-rose-300">
                                            {msg.content}
                                        </div>
                                    </>
                                ) : (
                                    <>
                                        <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center shrink-0 shadow-[0_0_10px_rgba(99,102,241,0.3)]">
                                            <Terminal size={14} className="text-primary" />
                                        </div>
                                        <div className="space-y-2 flex-1 min-w-0">
                                            <div className="bg-primary/10 p-3 rounded-2xl rounded-tr-none border border-primary/20 text-sm text-slate-300 whitespace-pre-wrap break-words">
                                                {msg.content}
                                            </div>
                                            {msg.metadata && (
                                                <div className="flex gap-2 flex-wrap">
                                                    <span className="text-[10px] px-2 py-0.5 bg-primary/10 text-primary rounded-full border border-primary/20 font-medium">
                                                        Intent: {msg.metadata.intent}
                                                    </span>
                                                    <span className="text-[10px] px-2 py-0.5 bg-secondary/10 text-secondary rounded-full border border-secondary/20 font-medium">
                                                        Engine: {msg.metadata.engine_used}
                                                    </span>
                                                </div>
                                            )}
                                        </div>
                                    </>
                                )}
                            </div>
                        ))}

                        {isLoading && (
                            <div className="flex gap-3">
                                <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center shrink-0 shadow-[0_0_10px_rgba(99,102,241,0.3)]">
                                    <Terminal size={14} className="text-primary animate-pulse" />
                                </div>
                                <div className="bg-primary/10 p-3 rounded-2xl rounded-tr-none border border-primary/20 text-sm text-slate-400 flex items-center gap-2">
                                    <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                    <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                    <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                                </div>
                            </div>
                        )}

                        <div ref={chatEndRef} />
                    </div>
                </div>

                <div className="glass p-3 rounded-t-none relative">
                    <div className="absolute -top-3 left-6 text-[10px] font-bold tracking-wider text-primary uppercase bg-[#070810] px-2">Prompt</div>
                    <div className="flex gap-2 items-center mb-2">
                        <label className="text-[10px] text-slate-500 font-medium uppercase tracking-wider shrink-0">Table:</label>
                        <input
                            type="text"
                            value={tableName}
                            onChange={(e) => setTableName(e.target.value)}
                            className="bg-slate-800/60 border border-slate-700/50 rounded px-2 py-1 text-xs text-slate-300 w-32 focus:outline-none focus:border-primary transition-colors"
                        />
                    </div>
                    <div className="flex gap-2 relative">
                        <input
                            type="text"
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="Ask anything about your data..."
                            className="flex-1 bg-transparent border-none focus:ring-0 text-sm placeholder-slate-500 py-2 pl-2 text-white glow-focus"
                            disabled={isLoading}
                        />
                        <button
                            onClick={handleSubmit}
                            disabled={isLoading || !prompt.trim()}
                            className={cn(
                                "bg-primary text-white p-2 rounded-lg transition-all flex items-center justify-center shadow-neon",
                                isLoading || !prompt.trim()
                                    ? "opacity-50 cursor-not-allowed"
                                    : "hover:bg-primary/90"
                            )}
                        >
                            <Send size={16} />
                        </button>
                    </div>
                </div>
            </div>

            {/* Right Panel: AI Reasoning Engine */}
            <div className="flex-1 flex flex-col gap-4">
                <div className="glass p-6 flex flex-col flex-1 relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-4 opacity-5 pointer-events-none">
                        <Cpu size={120} />
                    </div>

                    <h3 className="text-sm font-bold text-slate-300 mb-6 flex items-center gap-2">
                        <div className={cn(
                            "w-2 h-2 rounded-full shadow-[0_0_8px_#6366f1]",
                            isLoading ? "bg-primary animate-pulse" : "bg-slate-600"
                        )}></div>
                        AI Reasoning Engine
                        {isLoading && (
                            <span className="text-[10px] text-primary font-medium ml-2 animate-pulse">Processing...</span>
                        )}
                    </h3>

                    <div className="flex-1 space-y-4">
                        {REASONING_STEPS.map((step, idx) => {
                            const isActive = activeStep === idx;
                            const isDone = activeStep > idx;
                            const isIdle = activeStep === -1;

                            return (
                                <div key={idx} className={cn(
                                    "flex items-start gap-4 p-3 rounded-lg border transition-all duration-500",
                                    isIdle ? "border-slate-800/30 text-slate-600" :
                                        isActive ? "bg-primary/5 border-primary/20 shadow-[0_0_15px_rgba(99,102,241,0.05)]" :
                                            isDone ? "bg-emerald-500/5 text-slate-400 border-emerald-500/10" :
                                                "border-transparent text-slate-600"
                                )}>
                                    <div className="mt-0.5 relative shrink-0">
                                        {isDone ? (
                                            <CheckCircle2 size={16} className="text-emerald-500 drop-shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                                        ) : isActive ? (
                                            <>
                                                <Circle size={16} className="text-primary animate-spin" style={{ animationDuration: '3s' }} />
                                                <div className="absolute inset-0 bg-primary/20 blur-md rounded-full"></div>
                                            </>
                                        ) : (
                                            <Circle size={16} className="text-slate-700" />
                                        )}
                                    </div>

                                    <div className="flex-1">
                                        <p className={cn(
                                            "text-sm font-medium",
                                            isIdle ? "text-slate-600" :
                                                isActive ? "text-primary" :
                                                    isDone ? "text-slate-300" :
                                                        "text-slate-600"
                                        )}>
                                            {step}
                                        </p>
                                    </div>

                                    <div className="text-xs font-mono flex items-center gap-1 opacity-60">
                                        {isActive && (
                                            <Clock size={12} className="text-primary animate-pulse" />
                                        )}
                                        {isDone ? '✓' : isActive ? '...' : ''}
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    {/* Connection status */}
                    <div className="mt-6 p-3 rounded-lg bg-[#0a0a14] border border-slate-800/50 flex items-center justify-between">
                        <div className="flex items-center gap-2 text-xs text-slate-500">
                            <div className={cn(
                                "w-1.5 h-1.5 rounded-full",
                                isLoading ? "bg-primary animate-pulse" : "bg-emerald-500"
                            )}></div>
                            PolarisIQ Backend
                        </div>
                        <span className="text-[10px] text-slate-600 font-mono">localhost:8000</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default QueryStudio;
