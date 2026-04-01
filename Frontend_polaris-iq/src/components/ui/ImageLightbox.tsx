import { useState, useRef, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, ZoomIn, ZoomOut, Maximize2, Download, RotateCcw } from 'lucide-react';

interface ImageLightboxProps {
    src: string;
    alt?: string;
    isOpen: boolean;
    onClose: () => void;
    layoutId?: string;
}

const ZOOM_STEP = 0.25;
const MIN_ZOOM = 0.25;
const MAX_ZOOM = 5;

const ImageLightbox = ({ src, alt = 'Visualization', isOpen, onClose, layoutId }: ImageLightboxProps) => {
    const [zoom, setZoom] = useState(1);
    const [position, setPosition] = useState({ x: 0, y: 0 });
    const [isDragging, setIsDragging] = useState(false);
    const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
    const containerRef = useRef<HTMLDivElement>(null);

    const resetView = useCallback(() => {
        setZoom(1);
        setPosition({ x: 0, y: 0 });
    }, []);

    useEffect(() => {
        if (isOpen) resetView();
    }, [isOpen, resetView]);

    useEffect(() => {
        if (!isOpen) return;

        const handleKey = (e: KeyboardEvent) => {
            switch (e.key) {
                case 'Escape':
                    onClose();
                    break;
                case '+':
                case '=':
                    setZoom(z => Math.min(z + ZOOM_STEP, MAX_ZOOM));
                    break;
                case '-':
                    setZoom(z => Math.max(z - ZOOM_STEP, MIN_ZOOM));
                    break;
                case '0':
                    resetView();
                    break;
            }
        };

        window.addEventListener('keydown', handleKey);
        return () => window.removeEventListener('keydown', handleKey);
    }, [isOpen, onClose, resetView]);

    const handleWheel = useCallback((e: React.WheelEvent) => {
        e.preventDefault();
        const delta = e.deltaY > 0 ? -ZOOM_STEP : ZOOM_STEP;
        setZoom(z => Math.min(Math.max(z + delta, MIN_ZOOM), MAX_ZOOM));
    }, []);

    const handleMouseDown = useCallback((e: React.MouseEvent) => {
        if (zoom <= 1) return;
        e.preventDefault();
        setIsDragging(true);
        setDragStart({ x: e.clientX - position.x, y: e.clientY - position.y });
    }, [zoom, position]);

    const handleMouseMove = useCallback((e: React.MouseEvent) => {
        if (!isDragging) return;
        setPosition({
            x: e.clientX - dragStart.x,
            y: e.clientY - dragStart.y,
        });
    }, [isDragging, dragStart]);

    const handleMouseUp = useCallback(() => {
        setIsDragging(false);
    }, []);

    const handleDownload = useCallback(() => {
        const a = document.createElement('a');
        a.href = src;
        a.download = src.split('/').pop() || 'visualization.png';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }, [src]);

    const zoomPercent = Math.round(zoom * 100);

    return (
        <AnimatePresence>
            {isOpen && (
                <motion.div
                    className="lightbox-overlay"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    onClick={(e) => {
                        if (e.target === e.currentTarget) onClose();
                    }}
                >
                    {/* Top toolbar */}
                    <motion.div
                        className="lightbox-toolbar"
                        initial={{ y: -40, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        exit={{ y: -40, opacity: 0 }}
                        transition={{ delay: 0.1, duration: 0.3 }}
                    >
                        <div className="lightbox-toolbar-group">
                            <button
                                onClick={() => setZoom(z => Math.max(z - ZOOM_STEP, MIN_ZOOM))}
                                className="lightbox-btn"
                                title="Zoom out (-)"
                            >
                                <ZoomOut size={16} />
                            </button>

                            <div className="lightbox-zoom-badge">
                                {zoomPercent}%
                            </div>

                            <button
                                onClick={() => setZoom(z => Math.min(z + ZOOM_STEP, MAX_ZOOM))}
                                className="lightbox-btn"
                                title="Zoom in (+)"
                            >
                                <ZoomIn size={16} />
                            </button>

                            <div className="lightbox-divider" />

                            <button
                                onClick={resetView}
                                className="lightbox-btn"
                                title="Reset view (0)"
                            >
                                <RotateCcw size={16} />
                            </button>

                            <button
                                onClick={() => { resetView(); setZoom(1); }}
                                className="lightbox-btn"
                                title="Fit to screen"
                            >
                                <Maximize2 size={16} />
                            </button>

                            <div className="lightbox-divider" />

                            <button
                                onClick={handleDownload}
                                className="lightbox-btn lightbox-btn-accent"
                                title="Download image"
                            >
                                <Download size={16} />
                                <span className="text-xs ml-1">Download</span>
                            </button>
                        </div>

                        <button
                            onClick={onClose}
                            className="lightbox-btn lightbox-btn-close"
                            title="Close (Esc)"
                        >
                            <X size={18} />
                        </button>
                    </motion.div>

                    {/* Image container */}
                    <div
                        ref={containerRef}
                        className="lightbox-image-container"
                        onWheel={handleWheel}
                        onMouseDown={handleMouseDown}
                        onMouseMove={handleMouseMove}
                        onMouseUp={handleMouseUp}
                        onMouseLeave={handleMouseUp}
                        style={{ cursor: zoom > 1 ? (isDragging ? 'grabbing' : 'grab') : 'default' }}
                    >
                        <motion.img
                            layoutId={layoutId}
                            src={src}
                            alt={alt}
                            className="lightbox-image"
                            style={{
                                transform: `translate(${position.x}px, ${position.y}px) scale(${zoom})`,
                            }}
                            initial={{ scale: 0.8, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.8, opacity: 0 }}
                            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
                            draggable={false}
                        />
                    </div>

                    {/* Bottom hint */}
                    <motion.div
                        className="lightbox-hint"
                        initial={{ y: 20, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        exit={{ y: 20, opacity: 0 }}
                        transition={{ delay: 0.2, duration: 0.3 }}
                    >
                        <span>Scroll to zoom</span>
                        <span className="lightbox-hint-dot" />
                        <span>Drag to pan</span>
                        <span className="lightbox-hint-dot" />
                        <span>Esc to close</span>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
};

export default ImageLightbox;
