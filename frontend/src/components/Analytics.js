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
    Person:     '#ff2244',
    Topic:      '#00e5ff',
    Artifact:   '#b400ff',
    Decision:   '#ffe100',
    Unknown:    '#3a5570',
};
const TYPE_ICONS = {
    Person:     '👤',
    Topic:      '💡',
    Artifact:   '📦',
    Decision:   '⚖️',
    Unknown:    '❓',
};

const CHART_OPTS = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
        x: {
            ticks: {
                color: '#6b8fa8',
                font: { family: "'Share Tech Mono', monospace", size: 10 },
            },
            grid: { color: 'rgba(0, 180, 255, 0.06)' },
            border: { color: 'rgba(0, 180, 255, 0.12)' },
        },
        y: {
            ticks: {
                color: '#6b8fa8',
                font: { family: "'Share Tech Mono', monospace", size: 10 },
            },
            grid: { color: 'rgba(0, 180, 255, 0.06)' },
            border: { color: 'rgba(0, 180, 255, 0.12)' },
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

    const typeLabels = Object.keys(data.type_counts);
    const typeDataset = {
        labels: typeLabels,
        datasets: [{
            data: typeLabels.map(t => data.type_counts[t]),
            backgroundColor: typeLabels.map(t => (TYPE_COLORS[t] || '#00b4ff') + '66'),
            borderColor:     typeLabels.map(t => TYPE_COLORS[t] || '#00b4ff'),
            borderWidth: 1,
            borderRadius: 0,
            borderSkipped: false,
        }],
    };

    const relLabels = Object.keys(data.top_rel_counts).map(r => r.replace(/_/g, ' '));
    const relDataset = {
        labels: relLabels,
        datasets: [{
            data: Object.values(data.top_rel_counts),
            backgroundColor: 'rgba(180, 0, 255, 0.25)',
            borderColor:     '#b400ff',
            borderWidth: 1,
            borderRadius: 0,
            borderSkipped: false,
        }],
    };

    return (
        <div>
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
                            <td>{n.name}</td>
                            <td>
                                <span style={{
                                    color: TYPE_COLORS[n.type] || 'var(--text-mid)',
                                    textShadow: `0 0 6px ${TYPE_COLORS[n.type] || 'transparent'}`,
                                }}>
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
