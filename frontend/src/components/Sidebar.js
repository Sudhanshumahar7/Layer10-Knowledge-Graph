import React from 'react';

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

export default function Sidebar({
    meta,
    selectedTypes, setSelectedTypes,
    selectedRels, setSelectedRels,
    minDegree, setMinDegree,
    maxNodes, setMaxNodes,
    search, setSearch,
    physicsOn, setPhysicsOn,
    gravity, setGravity,
}) {
    const toggleType = (t) =>
        setSelectedTypes(prev =>
            prev.includes(t) ? prev.filter(x => x !== t) : [...prev, t]
        );

    const toggleRel = (r) =>
        setSelectedRels(prev =>
            prev.includes(r) ? prev.filter(x => x !== r) : [...prev, r]
        );

    return (
        <aside className="sidebar">
            <div className="sidebar-inner-scroll">

                {/* Brand */}
                <div className="sidebar-logo">
                    <span className="sidebar-badge">LAYER10</span>
                    <span className="sidebar-logo-name">Knowledge Graph</span>
                </div>

                {/* Entity Types */}
                <div className="sidebar-section">
                    <div className="sidebar-section-label">Entity Types</div>
                    {meta ? (
                        <div className="tag-list">
                            {meta.entity_types.map(t => (
                                <button
                                    key={t}
                                    className={`tag ${selectedTypes.includes(t) ? 'active' : ''}`}
                                    onClick={() => toggleType(t)}
                                    style={selectedTypes.includes(t) ? {
                                        borderColor: TYPE_COLORS[t] || 'var(--cyan-bright)',
                                        color: TYPE_COLORS[t] || 'var(--cyan-bright)',
                                        background: (TYPE_COLORS[t] || '#00b4ff') + '18',
                                        textShadow: `0 0 6px ${TYPE_COLORS[t] || 'var(--cyan-bright)'}`,
                                    } : {}}
                                >
                                    {TYPE_ICONS[t] || '❓'} {t}
                                </button>
                            ))}
                        </div>
                    ) : (
                        <div className="empty">Loading…</div>
                    )}
                </div>

                <hr />

                {/* Relationship Types */}
                <div className="sidebar-section">
                    <div className="sidebar-section-label">Relationship Types</div>
                    {meta ? (
                        <div className="tag-list">
                            {meta.relationship_types.map(r => (
                                <button
                                    key={r}
                                    className={`tag ${selectedRels.includes(r) ? 'active' : ''}`}
                                    onClick={() => toggleRel(r)}
                                >
                                    {r.replace(/_/g, ' ')}
                                </button>
                            ))}
                        </div>
                    ) : (
                        <div className="empty">Loading…</div>
                    )}
                </div>

                <hr />

                {/* Sliders */}
                <div className="sidebar-section">
                    <div className="sidebar-section-label">Display</div>

                    <div className="field">
                        <label>Min. Node Degree</label>
                        <div className="slider-row">
                            <input
                                type="range" min={1} max={20} value={minDegree}
                                onChange={e => setMinDegree(+e.target.value)}
                            />
                            <span className="slider-val">{minDegree}</span>
                        </div>
                    </div>

                    <div className="field">
                        <label>Max Nodes to Render</label>
                        <div className="slider-row">
                            <input
                                type="range" min={50} max={500} step={50} value={maxNodes}
                                onChange={e => setMaxNodes(+e.target.value)}
                            />
                            <span className="slider-val">{maxNodes}</span>
                        </div>
                    </div>
                </div>

                <hr />

                {/* Search */}
                <div className="sidebar-section">
                    <div className="sidebar-section-label">Search</div>
                    <div className="field">
                        <label>Node name contains</label>
                        <input
                            type="text"
                            placeholder="e.g. langchain"
                            value={search}
                            onChange={e => setSearch(e.target.value)}
                        />
                    </div>
                </div>

                <hr />

                {/* Physics */}
                <div className="sidebar-section">
                    <div className="sidebar-section-label">Physics</div>
                    <div className="field">
                        <div className="toggle-row">
                            <span>Enable simulation</span>
                            <label className="toggle">
                                <input
                                    type="checkbox"
                                    checked={physicsOn}
                                    onChange={e => setPhysicsOn(e.target.checked)}
                                />
                                <span className="toggle-track" />
                            </label>
                        </div>
                    </div>
                    <div className="field">
                        <label>Gravity</label>
                        <div className="slider-row">
                            <input
                                type="range" min={-5000} max={0} step={100} value={gravity}
                                onChange={e => setGravity(+e.target.value)}
                            />
                            <span className="slider-val">{gravity}</span>
                        </div>
                    </div>
                </div>

            </div>
        </aside>
    );
}
