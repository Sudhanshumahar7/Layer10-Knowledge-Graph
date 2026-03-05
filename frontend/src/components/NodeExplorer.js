import React, { useState, useEffect } from 'react';
import { getAllNodes, getNodeDetail } from '../api/api';

export default function NodeExplorer() {
    const [nodeList, setNodeList]     = useState([]);
    const [chosenId, setChosenId]     = useState('');
    const [nodeDetail, setNodeDetail] = useState(null);
    const [loading, setLoading]       = useState(false);

    useEffect(() => {
        getAllNodes()
            .then(list => {
                const sorted = [...list].sort((a, b) => a.label.localeCompare(b.label));
                setNodeList(sorted);
                if (sorted.length > 0) setChosenId(sorted[0].id);
            })
            .catch(console.error);
    }, []);

    useEffect(() => {
        if (!chosenId) return;
        setLoading(true);
        setNodeDetail(null);
        getNodeDetail(chosenId)
            .then(d => { setNodeDetail(d); setLoading(false); })
            .catch(() => setLoading(false));
    }, [chosenId]);

    return (
        <div>
            {/* Node selector */}
            <div className="explorer-select-row">
                <label>Select a node</label>
                <select value={chosenId} onChange={e => setChosenId(e.target.value)}>
                    {nodeList.map(n => (
                        <option key={n.id} value={n.id}>{n.label}</option>
                    ))}
                </select>
            </div>

            {loading && (
                <div className="loading" style={{ height: 200 }}>
                    <div className="spinner" />
                    <span>Loading node detail…</span>
                </div>
            )}

            {nodeDetail && !loading && (
                <>
                    <div className="node-card">
                        <div className="node-card-header">
                            <div
                                className="node-dot"
                                style={{
                                    background: nodeDetail.color,
                                    boxShadow: `0 0 10px ${nodeDetail.color}`,
                                }}
                            />
                            <h3>{nodeDetail.icon} {nodeDetail.display_name}</h3>
                        </div>
                        <div className="node-meta">
                            <span><b>Type</b>&nbsp;{nodeDetail.type}</span>
                            <span><b>ID</b>&nbsp;<code>{nodeDetail.id}</code></span>
                            <span><b>Degree</b>&nbsp;{nodeDetail.degree}</span>
                            <span><b>In</b>&nbsp;{nodeDetail.in_degree}</span>
                            <span><b>Out</b>&nbsp;{nodeDetail.out_degree}</span>
                        </div>
                    </div>

                    <div className="edge-columns">
                        {/* Incoming */}
                        <div>
                            <div className="sec-label">← Incoming</div>
                            <div className="edge-list">
                                {nodeDetail.in_edges.length === 0 ? (
                                    <div className="empty">No incoming edges.</div>
                                ) : (
                                    nodeDetail.in_edges.map((e, i) => (
                                        <details key={i} className="edge-expander">
                                            <summary>
                                                {e.source_name} → {e.relationship.replace(/_/g, ' ')}
                                            </summary>
                                            <div className="edge-body">
                                                {e.quote || 'No quote available.'}
                                                {e.source_url && (
                                                    <a href={e.source_url} target="_blank" rel="noreferrer">
                                                        ↗ Source
                                                    </a>
                                                )}
                                            </div>
                                        </details>
                                    ))
                                )}
                            </div>
                        </div>

                        {/* Outgoing */}
                        <div>
                            <div className="sec-label">→ Outgoing</div>
                            <div className="edge-list">
                                {nodeDetail.out_edges.length === 0 ? (
                                    <div className="empty">No outgoing edges.</div>
                                ) : (
                                    nodeDetail.out_edges.map((e, i) => (
                                        <details key={i} className="edge-expander">
                                            <summary>
                                                {e.relationship.replace(/_/g, ' ')} → {e.target_name}
                                            </summary>
                                            <div className="edge-body">
                                                {e.quote || 'No quote available.'}
                                                {e.source_url && (
                                                    <a href={e.source_url} target="_blank" rel="noreferrer">
                                                        ↗ Source
                                                    </a>
                                                )}
                                            </div>
                                        </details>
                                    ))
                                )}
                            </div>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}
