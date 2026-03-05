import React from 'react';

export default function MetricsBar({ meta }) {
    const metrics = meta
        ? [
            { label: 'Total Nodes',        value: meta.node_count },
            { label: 'Total Edges',         value: meta.edge_count },
            { label: 'Entity Types',        value: meta.entity_types.length },
            { label: 'Relationship Types',  value: meta.relationship_types.length },
        ]
        : [
            { label: 'Total Nodes',        value: '—' },
            { label: 'Total Edges',         value: '—' },
            { label: 'Entity Types',        value: '—' },
            { label: 'Relationship Types',  value: '—' },
        ];

    return (
        <div className="metrics-bar">
            {metrics.map(m => (
                <div key={m.label} className="metric-card">
                    <div className="metric-label">{m.label}</div>
                    <div className="metric-value">{m.value}</div>
                </div>
            ))}
        </div>
    );
}
