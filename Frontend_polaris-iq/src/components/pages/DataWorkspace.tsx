import { useState, useEffect, useCallback } from 'react';
import { Database, Search, HardDrive, Table2, Upload, X, FileUp, Hash, Calendar, Type, AlignLeft } from 'lucide-react';
import { fetchTables, fetchSchema, fetchPreview, ingestFile } from '../../services/api';
import type { TableInfo, ColumnInfo, PreviewResponse } from '../../types/api';

const TYPE_ICONS: Record<string, React.ElementType> = {
    INTEGER: Hash, BIGINT: Hash, DOUBLE: Hash, DECIMAL: Hash, FLOAT: Hash,
    TIMESTAMP: Calendar, DATE: Calendar, TIME: Calendar,
    VARCHAR: Type, TEXT: Type, BOOLEAN: Type,
};

const DataWorkspace = () => {
    const [tables, setTables] = useState<TableInfo[]>([]);
    const [selectedTable, setSelectedTable] = useState<string | null>(null);
    const [columns, setColumns] = useState<ColumnInfo[]>([]);
    const [rowCount, setRowCount] = useState(0);
    const [preview, setPreview] = useState<PreviewResponse | null>(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [uploadMessage, setUploadMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
    const [dragOver, setDragOver] = useState(false);

    const loadTables = useCallback(async () => {
        setLoading(true);
        try {
            const res = await fetchTables();
            setTables(res.tables);
            if (res.tables.length > 0 && !selectedTable) {
                setSelectedTable(res.tables[0].name);
            }
        } catch {
            setTables([]);
        } finally {
            setLoading(false);
        }
    }, [selectedTable]);

    useEffect(() => { loadTables(); }, []);

    useEffect(() => {
        if (!selectedTable) return;
        fetchSchema(selectedTable)
            .then(res => {
                setColumns(res.columns);
                setRowCount(res.row_count);
            })
            .catch(() => { setColumns([]); setRowCount(0); });
    }, [selectedTable]);

    const handlePreview = async () => {
        if (!selectedTable) return;
        try {
            const res = await fetchPreview(selectedTable, 100);
            setPreview(res);
        } catch {
            setPreview(null);
        }
    };

    const handleFileUpload = async (file: File) => {
        setUploading(true);
        setUploadMessage(null);
        try {
            const res = await ingestFile(file);
            setUploadMessage({ type: 'success', text: `Ingested "${res.table_name}" — ${res.rows.toLocaleString()} rows, ${res.columns} columns` });
            await loadTables();
            setSelectedTable(res.table_name);
        } catch (err) {
            setUploadMessage({ type: 'error', text: err instanceof Error ? err.message : 'Upload failed' });
        } finally {
            setUploading(false);
        }
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setDragOver(false);
        const file = e.dataTransfer.files[0];
        if (file) handleFileUpload(file);
    };

    const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) handleFileUpload(file);
        e.target.value = '';
    };

    const filteredTables = tables.filter(t =>
        t.name.toLowerCase().includes(searchQuery.toLowerCase())
    );

    const getIcon = (type: string) => TYPE_ICONS[type] || AlignLeft;

    return (
        <div className="h-full flex flex-col gap-6 animate-in fade-in duration-500">
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Data Workspace</h1>
                    <p className="text-slate-400">Explore, profile, and manage your datasets.</p>
                </div>
                <div className="flex gap-3">
                    <div className="relative group">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                        <input
                            type="text"
                            placeholder="Search tables..."
                            value={searchQuery}
                            onChange={e => setSearchQuery(e.target.value)}
                            className="pl-9 pr-4 py-2 bg-card/50 border border-cardBorder rounded-lg text-sm text-slate-200 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary w-64 transition-all"
                        />
                    </div>
                    <label className="flex items-center gap-2 px-4 py-2 bg-primary/10 border border-primary/20 text-primary rounded-lg text-sm font-medium cursor-pointer hover:bg-primary/20 transition-colors">
                        <Upload size={16} />
                        Upload File
                        <input type="file" className="hidden" accept=".csv,.tsv,.parquet,.json,.ndjson,.xlsx,.xls" onChange={handleFileInput} />
                    </label>
                </div>
            </div>

            {/* Upload message */}
            {uploadMessage && (
                <div className={`flex items-center justify-between p-3 rounded-lg border text-sm ${
                    uploadMessage.type === 'success'
                        ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                        : 'bg-rose-500/10 border-rose-500/20 text-rose-400'
                }`}>
                    <span>{uploadMessage.text}</span>
                    <button onClick={() => setUploadMessage(null)} className="hover:opacity-70"><X size={14} /></button>
                </div>
            )}

            <div className="flex gap-6 flex-1 min-h-0">
                {/* Left: Table List + Drop Zone */}
                <div className="w-1/3 flex flex-col gap-4">
                    <div className="glass flex flex-col overflow-hidden flex-1">
                        <div className="p-4 border-b border-cardBorder bg-white/5 font-medium flex gap-2 items-center text-slate-200">
                            <Database size={16} className="text-primary" />
                            Tables ({tables.length})
                        </div>
                        <div className="flex-1 overflow-y-auto p-3 space-y-2 scrollbar-hide">
                            {loading ? (
                                <div className="text-center text-slate-500 text-sm py-8">Loading...</div>
                            ) : filteredTables.length === 0 ? (
                                <div className="text-center text-slate-500 text-sm py-8">
                                    {tables.length === 0 ? 'No tables. Upload a file to get started.' : 'No matching tables.'}
                                </div>
                            ) : (
                                filteredTables.map(t => (
                                    <div
                                        key={t.name}
                                        onClick={() => { setSelectedTable(t.name); setPreview(null); }}
                                        className={`p-3 rounded-lg border cursor-pointer transition-all ${
                                            selectedTable === t.name
                                                ? 'border-primary/50 bg-primary/10 shadow-[inset_0_0_20px_rgba(99,102,241,0.05)]'
                                                : 'border-cardBorder bg-card/30 hover:bg-card/80 hover:border-slate-600'
                                        }`}
                                    >
                                        <h3 className={`font-medium mb-1 ${selectedTable === t.name ? 'text-primary' : 'text-slate-300'}`}>
                                            {t.name}
                                        </h3>
                                        <div className="flex gap-4 text-xs text-slate-400">
                                            <span className="flex items-center gap-1"><Table2 size={12} /> {t.rows.toLocaleString()} rows</span>
                                            <span className="flex items-center gap-1"><HardDrive size={12} /> {t.columns} cols</span>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>

                    {/* Drop Zone */}
                    <div
                        onDragOver={e => { e.preventDefault(); setDragOver(true); }}
                        onDragLeave={() => setDragOver(false)}
                        onDrop={handleDrop}
                        className={`glass p-6 text-center transition-all ${
                            dragOver ? 'border-primary bg-primary/10' : ''
                        } ${uploading ? 'opacity-50 pointer-events-none' : ''}`}
                    >
                        <FileUp size={24} className={`mx-auto mb-2 ${dragOver ? 'text-primary' : 'text-slate-500'}`} />
                        <p className="text-sm text-slate-400">
                            {uploading ? 'Uploading...' : 'Drop a file here to ingest'}
                        </p>
                        <p className="text-xs text-slate-600 mt-1">CSV, Parquet, JSON, Excel</p>
                    </div>
                </div>

                {/* Right: Schema + Preview */}
                <div className="flex-1 flex flex-col gap-4">
                    {selectedTable ? (
                        <>
                            <div className="glass p-6 flex flex-col">
                                <div className="flex justify-between items-start pb-6 border-b border-cardBorder">
                                    <div>
                                        <div className="flex items-center gap-3 mb-1">
                                            <h2 className="text-xl font-bold text-white">{selectedTable}</h2>
                                            <span className="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider text-emerald-400 bg-emerald-400/10 border border-emerald-400/20">
                                                {rowCount.toLocaleString()} rows
                                            </span>
                                        </div>
                                        <p className="text-sm text-slate-400">{columns.length} columns</p>
                                    </div>
                                    <button
                                        onClick={handlePreview}
                                        className="text-primary hover:text-primary-light text-sm font-medium transition-colors"
                                    >
                                        Preview Data
                                    </button>
                                </div>

                                <div className="pt-6">
                                    <h3 className="text-sm font-bold text-slate-300 mb-4 uppercase tracking-wider">Schema & Statistics</h3>
                                    <div className="w-full overflow-x-auto rounded-lg border border-cardBorder">
                                        <table className="w-full text-left text-sm whitespace-nowrap">
                                            <thead className="bg-white/5 text-slate-400 font-medium">
                                                <tr>
                                                    <th className="px-4 py-3">Column Name</th>
                                                    <th className="px-4 py-3">Type</th>
                                                    <th className="px-4 py-3 text-right">Null %</th>
                                                </tr>
                                            </thead>
                                            <tbody className="divide-y divide-cardBorder bg-card/30">
                                                {columns.map(col => {
                                                    const Icon = getIcon(col.type);
                                                    return (
                                                        <tr key={col.name} className="hover:bg-white/5 transition-colors">
                                                            <td className="px-4 py-3 font-medium text-slate-200 flex items-center gap-2">
                                                                <Icon size={14} className="text-slate-500" />
                                                                {col.name}
                                                            </td>
                                                            <td className="px-4 py-3">
                                                                <span className="text-[10px] px-1.5 py-0.5 bg-slate-800 text-slate-300 rounded font-mono border border-slate-700">
                                                                    {col.type}
                                                                </span>
                                                            </td>
                                                            <td className="px-4 py-3 text-right text-slate-400">
                                                                {col.null_percent !== undefined ? `${col.null_percent}%` : '—'}
                                                            </td>
                                                        </tr>
                                                    );
                                                })}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>

                            {/* Data Preview */}
                            {preview ? (
                                <div className="glass p-6 flex-1 overflow-auto">
                                    <div className="flex justify-between items-center mb-4">
                                        <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider">
                                            Data Preview ({preview.total} rows)
                                        </h3>
                                        <button onClick={() => setPreview(null)} className="text-slate-400 hover:text-white">
                                            <X size={16} />
                                        </button>
                                    </div>
                                    <div className="overflow-x-auto rounded-lg border border-cardBorder">
                                        <table className="w-full text-left text-xs whitespace-nowrap">
                                            <thead className="bg-white/5 text-slate-400 font-medium sticky top-0">
                                                <tr>
                                                    {preview.columns.map(col => (
                                                        <th key={col} className="px-3 py-2">{col}</th>
                                                    ))}
                                                </tr>
                                            </thead>
                                            <tbody className="divide-y divide-cardBorder">
                                                {preview.rows.map((row, i) => (
                                                    <tr key={i} className="hover:bg-white/5 transition-colors">
                                                        {preview.columns.map(col => (
                                                            <td key={col} className="px-3 py-2 text-slate-300 max-w-[200px] truncate">
                                                                {String(row[col] ?? '')}
                                                            </td>
                                                        ))}
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            ) : (
                                <div className="glass p-6 flex-1 flex flex-col justify-center items-center text-center">
                                    <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4 shadow-neon">
                                        <Table2 className="text-primary w-8 h-8" />
                                    </div>
                                    <h3 className="text-lg font-bold text-white mb-2">Data Preview</h3>
                                    <p className="text-sm text-slate-400 max-w-sm mb-6">
                                        Click "Preview Data" above to see sample rows from this table.
                                    </p>
                                    <button
                                        onClick={handlePreview}
                                        className="bg-white/10 hover:bg-white/20 text-white border border-white/20 px-4 py-2 rounded-lg font-medium text-sm transition-all"
                                    >
                                        Preview Data
                                    </button>
                                </div>
                            )}
                        </>
                    ) : (
                        <div className="glass p-6 flex-1 flex flex-col justify-center items-center text-center">
                            <Database size={48} className="text-slate-600 mb-4" />
                            <h3 className="text-lg font-bold text-white mb-2">No Table Selected</h3>
                            <p className="text-sm text-slate-400">Select a table from the left or upload a file to get started.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default DataWorkspace;
