import React, { useState, useEffect, useRef } from 'react';

const TYPE_COLORS = {
    Person: '#c87d50',
    Topic: '#5888b8',
    Artifact: '#4e9e72',
    Decision: '#b85858',
    Unknown: '#6e6e78',
};
const TYPE_ICONS = {
    Person: '👤',
    Topic: '💡',
    Artifact: '📦',
    Decision: '⚖️',
    Unknown: '❓',
};

export default function GraphView({ graphUrl, meta, selectedTypes, selectedRels }) {
    const [iframeKey, setIframeKey] = useState(0);
    const [loading, setLoading] = useState(false);
    const prevUrlRef = useRef(null);

    // Reload iframe whenever graphUrl changes (with debounce)
    useEffect(() => {
        if (!graphUrl || graphUrl === prevUrlRef.current) return;
        prevUrlRef.current = graphUrl;
        setLoading(true);
        const t = setTimeout(() => setIframeKey(k => k + 1), 300);
        return () => clearTimeout(t);
    }, [graphUrl]);

    const noNodes = meta && selectedTypes.length === 0;

    return (
        <div>
            {/* Topbar */}
            <div className="graph-topbar">
                <span className="pulse" />
                <span>Knowledge Graph</span>
                {meta && (
                    <>
                        <span style={{ color: 'var(--text-faint)' }}>·</span>
                        <b>{meta.node_count}</b><span>nodes</span>
                        <span style={{ color: 'var(--text-faint)' }}>·</span>
                        <b>{meta.edge_count}</b><span>edges</span>
                        <span style={{ color: 'var(--text-faint)' }}>·</span>
                        <span>filtered view</span>
                    </>
                )}
            </div>

            {/* Graph frame */}
            <div className="graph-frame">
                {noNodes ? (
                    <div className="loading" style={{ height: 670 }}>
                        <span>No nodes match the current filters.</span>
                    </div>
                ) : !graphUrl ? (
                    <div className="loading" style={{ height: 670 }}>
                        <div className="spinner" />
                        <span>Connecting to backend…</span>
                    </div>
                ) : (
                    <>
                        {loading && (
                            <div className="loading" style={{ height: 670, position: 'absolute', inset: 0, zIndex: 2, background: 'var(--bg)' }}>
                                <div className="spinner" />
                                <span>Rendering graph…</span>
                            </div>
                        )}
                        <iframe
                            key={iframeKey}
                            src={graphUrl}
                            title="Knowledge Graph"
                            onLoad={() => setLoading(false)}
                        />
                    </>
                )}
            </div>

            {/* Legend */}
            <div className="legend-strip">
                {Object.entries(TYPE_COLORS).map(([t, c]) => (
                    <div key={t} className="legend-item">
                        <div className="legend-dot" style={{ background: c }} />
                        {TYPE_ICONS[t]} {t}
                    </div>
                ))}
            </div>
        </div>
    );
}
