import React, { useState, useEffect } from 'react';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Tooltip,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import { getAnalytics } from '../api/api';

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip);

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

const CHART_OPTS = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
        x: {
            ticks: { color: '#5e5e68', font: { family: 'Syne, sans-serif', size: 11 } },
            grid: { color: '#1e1e22' },
        },
        y: {
            ticks: { color: '#5e5e68', font: { family: 'IBM Plex Mono, monospace', size: 10 } },
            grid: { color: '#1e1e22' },
        },
    },
};

export default function Analytics() {
    const [data, setData] = useState(null);

    useEffect(() => {
        getAnalytics().then(setData).catch(console.error);
    }, []);

    if (!data) {
        return (
            <div className="loading">
                <div className="spinner" />
                <span>Loading analytics…</span>
            </div>
        );
    }

    // Entity type chart data
    const typeLabels = Object.keys(data.type_counts);
    const typeDataset = {
        labels: typeLabels,
        datasets: [{
            data: typeLabels.map(t => data.type_counts[t]),
            backgroundColor: typeLabels.map(t => TYPE_COLORS[t] || '#b8955a'),
            borderRadius: 4,
            borderSkipped: false,
        }],
    };

    // Relationship chart data
    const relLabels = Object.keys(data.top_rel_counts).map(r => r.replace(/_/g, ' '));
    const relDataset = {
        labels: relLabels,
        datasets: [{
            data: Object.values(data.top_rel_counts),
            backgroundColor: '#5888b866',
            borderColor: '#5888b8',
            borderWidth: 1,
            borderRadius: 4,
            borderSkipped: false,
        }],
    };

    return (
        <div>
            {/* Two charts side-by-side */}
            <div className="analytics-grid">
                <div className="analytics-card">
                    <div className="sec-label">Entity Type Distribution</div>
                    <div style={{ height: 220 }}>
                        <Bar data={typeDataset} options={CHART_OPTS} />
                    </div>
                </div>
                <div className="analytics-card">
                    <div className="sec-label">Top 10 Relationship Types</div>
                    <div style={{ height: 220 }}>
                        <Bar data={relDataset} options={CHART_OPTS} />
                    </div>
                </div>
            </div>

            {/* Top-15 nodes table */}
            <div className="sec-label">Top 15 Most-Connected Nodes</div>
            <table className="node-table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Type</th>
                        <th>Total Degree</th>
                        <th>In-edges</th>
                        <th>Out-edges</th>
                    </tr>
                </thead>
                <tbody>
                    {data.top_nodes.map(n => (
                        <tr key={n.id}>
                            <td style={{ color: 'var(--text)' }}>{n.name}</td>
                            <td>
                                <span style={{ color: TYPE_COLORS[n.type] || 'var(--text-dim)' }}>
                                    {TYPE_ICONS[n.type] || '❓'} {n.type}
                                </span>
                            </td>
                            <td>{n.total_degree}</td>
                            <td>{n.in_degree}</td>
                            <td>{n.out_degree}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
