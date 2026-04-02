import { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Send, Terminal, CheckCircle2, Circle, Clock,
    AlertCircle, Sparkles, Wrench, ZoomIn, Database,
    ArrowRight, Cpu
} from 'lucide-react';
import { cn } from '../../lib/utils';
import { sendQuery, sendToolQuery, fetchTables } from '../../services/api';
import type { QueryResponse, TableInfo } from '../../types/api';
import ImageLightbox from '../ui/ImageLightbox';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import katex from 'katex';
import 'katex/dist/katex.min.css';

interface ChatMessage {
    id: string;
    role: 'user' | 'assistant' | 'error';
    content: string;
    imageUrl?: string;
    metadata?: QueryResponse['metadata'] | Record<string, unknown>;
    timestamp: number;
}

const REASONING_STEPS = [
    { label: 'Understanding natural language query', icon: '🧠' },
    { label: 'Mapping entities to hybrid OLAP schema', icon: '🗺️' },
    { label: 'Generating optimized execution plan', icon: '⚡' },
    { label: 'Selecting best execution engine', icon: '🔧' },
    { label: 'Executing query pipeline', icon: '🚀' },
    { label: 'Generating explanation', icon: '📊' },
];

const SUGGESTED_QUERIES = [
    'Show me the distribution of values',
    'What are the top 10 records by count?',
    'Generate a bar chart of the data',
    'Show correlations between numeric columns',
    'Summarize the dataset statistics',
];

let msgIdCounter = 0;
const nextMsgId = () => `msg-${++msgIdCounter}-${Date.now()}`;

const QueryStudio = () => {
    const [prompt, setPrompt] = useState('');
    const [tableName, setTableName] = useState('');
    const [tables, setTables] = useState<TableInfo[]>([]);
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [activeStep, setActiveStep] = useState(-1);
    const [toolMode, setToolMode] = useState(false);
    const [lightboxSrc, setLightboxSrc] = useState<string | null>(null);
    const [lightboxId, setLightboxId] = useState<string | undefined>();
    const chatEndRef = useRef<HTMLDivElement>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const stepTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

    useEffect(() => {
        fetchTables()
            .then(res => {
                setTables(res.tables);
                if (res.tables.length > 0 && !tableName) {
                    setTableName(res.tables[0].name);
                }
            })
            .catch(() => {});
    }, []);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    useEffect(() => {
        return () => {
            if (stepTimerRef.current) clearInterval(stepTimerRef.current);
        };
    }, []);

    // Auto-resize textarea
    const adjustTextarea = useCallback(() => {
        const ta = textareaRef.current;
        if (!ta) return;
        ta.style.height = 'auto';
        ta.style.height = Math.min(ta.scrollHeight, 160) + 'px';
    }, []);

    useEffect(() => {
        adjustTextarea();
    }, [prompt, adjustTextarea]);

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
        setActiveStep(REASONING_STEPS.length);
        setTimeout(() => setActiveStep(-1), 1500);
    };

    const handleSubmit = async () => {
        const trimmed = prompt.trim();
        if (!trimmed || isLoading || !tableName) return;

        const userMsg: ChatMessage = {
            id: nextMsgId(),
            role: 'user',
            content: `${toolMode ? '[TOOL] ' : ''}${trimmed}`,
            timestamp: Date.now(),
        };
        setMessages(prev => [...prev, userMsg]);
        setPrompt('');
        setIsLoading(true);
        startReasoningAnimation();

        try {
            let assistantMsg: ChatMessage;

            if (toolMode) {
                const response = await sendToolQuery(trimmed, tableName);
                stopReasoningAnimation();
                assistantMsg = {
                    id: nextMsgId(),
                    role: 'assistant',
                    content: typeof response.tool_result === 'string' ? response.tool_result : JSON.stringify(response.tool_result),
                    imageUrl: response.image_url ? `/api${response.image_url}` : undefined,
                    metadata: response.metadata,
                    timestamp: Date.now(),
                };
            } else {
                const response = await sendQuery(trimmed, tableName);
                stopReasoningAnimation();
                assistantMsg = {
                    id: nextMsgId(),
                    role: 'assistant',
                    content: response.explanation,
                    imageUrl: response.image_url ? `/api${response.image_url}` : undefined,
                    metadata: response.metadata,
                    timestamp: Date.now(),
                };
            }

            setMessages(prev => [...prev, assistantMsg]);
        } catch (err) {
            stopReasoningAnimation();
            const errorMsg: ChatMessage = {
                id: nextMsgId(),
                role: 'error',
                content: err instanceof Error ? err.message : 'Failed to connect to PolarisIQ backend.',
                timestamp: Date.now(),
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

    const openLightbox = (src: string, layoutId: string) => {
        setLightboxSrc(src);
        setLightboxId(layoutId);
    };

    const handleSuggestedQuery = (q: string) => {
        setPrompt(q);
        textareaRef.current?.focus();
    };

    // Message animation variants
    const messageVariants = {
        hidden: { opacity: 0, y: 20, scale: 0.97 },
        visible: { opacity: 1, y: 0, scale: 1 },
        exit: { opacity: 0, y: -10 },
    };

    const metadataVariants = {
        hidden: { opacity: 0, scale: 0.8 },
        visible: (i: number) => ({
            opacity: 1,
            scale: 1,
            transition: { delay: 0.3 + i * 0.08, type: 'spring', stiffness: 500, damping: 30 },
        }),
    };

    return (
        <div className="h-full flex flex-col animate-in fade-in duration-500">
            {/* Inline Reasoning Progress Bar */}
            <AnimatePresence>
                {activeStep >= 0 && activeStep < REASONING_STEPS.length && (
                    <motion.div
                        className="mb-4"
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.35 }}
                    >
                        <div className="glass p-3 relative overflow-hidden">
                            {/* Shimmer effect */}
                            <div className="reasoning-shimmer" />

                            <div className="flex items-center gap-3 mb-2">
                                <Cpu size={14} className="text-primary animate-pulse" />
                                <span className="text-xs font-bold text-slate-300 tracking-wider uppercase">
                                    AI Reasoning Pipeline
                                </span>
                                {toolMode && (
                                    <span className="text-[9px] text-amber-400 font-semibold flex items-center gap-1 ml-1">
                                        <Wrench size={9} /> Tool Mode
                                    </span>
                                )}
                                <span className="text-[10px] text-primary font-mono ml-auto animate-pulse">
                                    Processing...
                                </span>
                            </div>

                            <div className="flex gap-1 items-center">
                                {REASONING_STEPS.map((step, idx) => {
                                    const isActive = activeStep === idx;
                                    const isDone = activeStep > idx;

                                    return (
                                        <div key={idx} className="flex items-center gap-1 flex-1">
                                            <div className="flex-1 relative">
                                                <div className={cn(
                                                    "h-1.5 rounded-full transition-all duration-500",
                                                    isDone ? "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.4)]" :
                                                        isActive ? "bg-primary shadow-[0_0_8px_rgba(99,102,241,0.4)] animate-pulse" :
                                                            "bg-slate-800"
                                                )} />
                                                {isActive && (
                                                    <motion.div
                                                        className="absolute -top-8 left-1/2 -translate-x-1/2 whitespace-nowrap text-[10px] font-medium text-primary bg-primary/10 border border-primary/20 px-2 py-0.5 rounded-md"
                                                        initial={{ opacity: 0, y: 5 }}
                                                        animate={{ opacity: 1, y: 0 }}
                                                        exit={{ opacity: 0 }}
                                                    >
                                                        {step.icon} {step.label}
                                                    </motion.div>
                                                )}
                                            </div>
                                            {idx < REASONING_STEPS.length - 1 && (
                                                <ArrowRight size={8} className={cn(
                                                    "shrink-0 transition-colors duration-300",
                                                    isDone ? "text-emerald-500" : "text-slate-700"
                                                )} />
                                            )}
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* All-done flash */}
            <AnimatePresence>
                {activeStep === REASONING_STEPS.length && (
                    <motion.div
                        className="mb-4"
                        initial={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.5, delay: 0.5 }}
                    >
                        <div className="glass p-3 border-emerald-500/20">
                            <div className="flex items-center gap-2">
                                <CheckCircle2 size={14} className="text-emerald-500" />
                                <span className="text-xs font-bold text-emerald-400 tracking-wider uppercase">
                                    Pipeline Complete
                                </span>
                                <div className="flex gap-0.5 ml-auto">
                                    {REASONING_STEPS.map((_, idx) => (
                                        <div key={idx} className="w-3 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_6px_rgba(16,185,129,0.4)]" />
                                    ))}
                                </div>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Chat Area — Full Width */}
            <div className="flex-1 flex flex-col overflow-hidden glass">
                <div className="flex-1 overflow-y-auto p-6 space-y-5 scrollbar-hide">
                    {/* Empty state */}
                    {messages.length === 0 && (
                        <motion.div
                            className="flex flex-col items-center justify-center h-full text-center"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.2 }}
                        >
                            <div className="relative mb-6">
                                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center border border-primary/10">
                                    <Sparkles size={28} className="text-primary" />
                                </div>
                                <div className="absolute -inset-4 bg-primary/5 rounded-3xl blur-xl -z-10" />
                            </div>
                            <h3 className="text-lg font-bold text-slate-200 mb-2">Ask PolarisIQ Anything</h3>
                            <p className="text-sm text-slate-500 max-w-md mb-8">
                                Query your data using natural language. PolarisIQ generates optimized execution plans, selects the right engine, and explains results.
                            </p>

                            {/* Suggestion pills */}
                            <div className="flex flex-wrap gap-2 justify-center max-w-lg">
                                {SUGGESTED_QUERIES.map((q, i) => (
                                    <motion.button
                                        key={i}
                                        className="suggestion-pill"
                                        onClick={() => handleSuggestedQuery(q)}
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ delay: 0.3 + i * 0.06 }}
                                        whileHover={{ scale: 1.04, y: -1 }}
                                        whileTap={{ scale: 0.97 }}
                                    >
                                        <ArrowRight size={10} className="text-primary/60" />
                                        {q}
                                    </motion.button>
                                ))}
                            </div>
                        </motion.div>
                    )}

                    {/* Messages */}
                    <AnimatePresence initial={false}>
                        {messages.map((msg) => (
                            <motion.div
                                key={msg.id}
                                variants={messageVariants}
                                initial="hidden"
                                animate="visible"
                                exit="exit"
                                transition={{ type: 'spring', damping: 25, stiffness: 300 }}
                                layout
                            >
                                <div className={cn(
                                    "flex gap-3",
                                    msg.role === 'user' ? "justify-end" : "justify-start"
                                )}>
                                    {/* Avatar — left for assistant/error */}
                                    {msg.role !== 'user' && (
                                        <div className={cn(
                                            "w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1",
                                            msg.role === 'error'
                                                ? "bg-rose-500/20"
                                                : "bg-primary/20 shadow-[0_0_10px_rgba(99,102,241,0.3)]"
                                        )}>
                                            {msg.role === 'error'
                                                ? <AlertCircle size={14} className="text-rose-400" />
                                                : <Terminal size={14} className="text-primary" />
                                            }
                                        </div>
                                    )}

                                    {/* Message content */}
                                    <div className={cn(
                                        "max-w-[75%] space-y-2",
                                        msg.role === 'user' ? "items-end" : "items-start"
                                    )}>
                                        {/* Text bubble */}
                                        <div className={cn(
                                            "p-4 rounded-2xl text-sm leading-relaxed",
                                            msg.role === 'user'
                                                ? "bg-primary/15 border border-primary/25 rounded-br-md text-slate-200"
                                                : msg.role === 'error'
                                                    ? "bg-rose-500/10 border border-rose-500/20 rounded-tl-none text-rose-300"
                                                    : "bg-slate-800/40 border border-slate-700/30 rounded-tl-none text-slate-300 whitespace-pre-wrap break-words prose prose-invert prose-sm max-w-none prose-p:leading-relaxed prose-pre:bg-slate-900/50"
                                        )}>
                                            {msg.role === 'assistant' ? (
                                                <ReactMarkdown
                                                    remarkPlugins={[remarkMath]}
                                                    rehypePlugins={[rehypeKatex]}
                                                    components={{
                                                        code(props: any) {
                                                            const { node, className, children, ...rest } = props;
                                                            const str = String(children).replace(/\n$/, '');
                                                            // Detect if the code block is actually LaTeX math wrapped in backticks
                                                            const isMath = str.includes('\\text{') || str.includes('\\frac') || str.includes('\\beta') || str.includes('\\times') || str.includes('\\cdot') || str.includes('^') || className?.includes('language-latex') || className?.includes('language-math');
                                                            
                                                            if (isMath) {
                                                                try {
                                                                    const isBlock = String(children).includes('\\n') || className;
                                                                    return (
                                                                        <span 
                                                                            dangerouslySetInnerHTML={{ 
                                                                                __html: katex.renderToString(str, { throwOnError: false, displayMode: !!isBlock }) 
                                                                            }} 
                                                                        />
                                                                    );
                                                                } catch (e) {
                                                                    // Fallback to normal code if KaTeX fails completely
                                                                }
                                                            }
                                                            return <code className={className} {...rest}>{children}</code>;
                                                        }
                                                    }}
                                                >
                                                    {msg.content}
                                                </ReactMarkdown>
                                            ) : (
                                                msg.content
                                            )}
                                        </div>

                                        {/* Image thumbnail */}
                                        {msg.imageUrl && (
                                            <motion.div
                                                className="chat-image-wrapper group"
                                                whileHover={{ scale: 1.02 }}
                                                whileTap={{ scale: 0.98 }}
                                                onClick={() => openLightbox(msg.imageUrl!, `img-${msg.id}`)}
                                            >
                                                <motion.img
                                                    layoutId={`img-${msg.id}`}
                                                    src={msg.imageUrl}
                                                    alt="Generated visualization"
                                                    className="chat-image"
                                                    loading="lazy"
                                                />
                                                {/* Hover overlay */}
                                                <div className="chat-image-overlay">
                                                    <div className="chat-image-zoom-badge">
                                                        <ZoomIn size={16} />
                                                        <span>Click to enlarge</span>
                                                    </div>
                                                </div>
                                            </motion.div>
                                        )}

                                        {/* Metadata pills */}
                                        {msg.metadata && (
                                            <div className="flex gap-2 flex-wrap pt-1">
                                                {Object.entries(msg.metadata).map(([key, val], i) => (
                                                    <motion.span
                                                        key={key}
                                                        className="metadata-pill"
                                                        custom={i}
                                                        variants={metadataVariants}
                                                        initial="hidden"
                                                        animate="visible"
                                                    >
                                                        {key}: {String(val)}
                                                    </motion.span>
                                                ))}
                                            </div>
                                        )}
                                    </div>

                                    {/* Avatar — right for user */}
                                    {msg.role === 'user' && (
                                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center shrink-0 mt-1 shadow-neon">
                                            <span className="text-xs font-bold text-white">U</span>
                                        </div>
                                    )}
                                </div>
                            </motion.div>
                        ))}
                    </AnimatePresence>

                    {/* Typing indicator */}
                    <AnimatePresence>
                        {isLoading && (
                            <motion.div
                                className="flex gap-3"
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0 }}
                            >
                                <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center shrink-0 shadow-[0_0_10px_rgba(99,102,241,0.3)]">
                                    <Terminal size={14} className="text-primary animate-pulse" />
                                </div>
                                <div className="bg-slate-800/40 border border-slate-700/30 p-4 rounded-2xl rounded-tl-none flex items-center gap-2">
                                    <div className="typing-dot" style={{ animationDelay: '0ms' }} />
                                    <div className="typing-dot" style={{ animationDelay: '150ms' }} />
                                    <div className="typing-dot" style={{ animationDelay: '300ms' }} />
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    <div ref={chatEndRef} />
                </div>

                {/* Input Area */}
                <div className="border-t border-slate-800/50 p-4 relative">
                    {/* Table selector + Tool mode toggle */}
                    <div className="flex gap-2 items-center mb-3">
                        <div className="flex items-center gap-2 text-[10px] text-slate-500 font-semibold uppercase tracking-wider">
                            <Database size={12} className="text-primary/60" />
                            Table:
                        </div>
                        <select
                            value={tableName}
                            onChange={e => setTableName(e.target.value)}
                            className="bg-slate-800/60 border border-slate-700/50 rounded-lg px-3 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-primary/50 transition-all"
                        >
                            {tables.length === 0 && <option value="">No tables</option>}
                            {tables.map(t => (
                                <option key={t.name} value={t.name}>{t.name} ({t.rows.toLocaleString()} rows)</option>
                            ))}
                        </select>

                        <button
                            onClick={() => setToolMode(!toolMode)}
                            className={cn(
                                "ml-auto flex items-center gap-1.5 text-[10px] font-semibold px-3 py-1.5 rounded-lg border transition-all duration-300",
                                toolMode
                                    ? "bg-amber-500/10 text-amber-400 border-amber-500/20 shadow-[0_0_10px_rgba(245,158,11,0.1)]"
                                    : "bg-white/5 text-slate-500 border-white/10 hover:text-slate-300 hover:bg-white/8"
                            )}
                            title="Toggle tool mode for visualizations"
                        >
                            <Wrench size={11} />
                            {toolMode ? 'Tool Mode ON' : 'Tool Mode'}
                        </button>
                    </div>

                    {/* Input + send */}
                    <div className="chat-input-wrapper">
                        <textarea
                            ref={textareaRef}
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder={toolMode ? "Describe a visualization to generate..." : "Ask anything about your data..."}
                            className="chat-textarea"
                            disabled={isLoading}
                            rows={1}
                        />
                        <button
                            onClick={handleSubmit}
                            disabled={isLoading || !prompt.trim() || !tableName}
                            className={cn(
                                "chat-send-btn",
                                isLoading || !prompt.trim() || !tableName
                                    ? "opacity-40 cursor-not-allowed"
                                    : "hover:shadow-neon-strong hover:scale-105"
                            )}
                        >
                            <Send size={16} />
                        </button>
                    </div>

                    <div className="flex items-center justify-between mt-2">
                        <p className="text-[10px] text-slate-600">
                            Press <kbd className="kbd-hint">Enter</kbd> to send, <kbd className="kbd-hint">Shift+Enter</kbd> for new line
                        </p>
                        <div className="flex items-center gap-1.5 text-[10px] text-slate-600">
                            <div className={cn(
                                "w-1.5 h-1.5 rounded-full",
                                isLoading ? "bg-primary animate-pulse" : "bg-emerald-500"
                            )} />
                            PolarisIQ
                            <span className="font-mono text-slate-700 ml-1">localhost:8000</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Lightbox */}
            <ImageLightbox
                src={lightboxSrc || ''}
                isOpen={!!lightboxSrc}
                onClose={() => setLightboxSrc(null)}
                layoutId={lightboxId}
            />
        </div>
    );
};

export default QueryStudio;
