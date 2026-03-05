import React, { useState, useEffect } from 'react';
import './index.css';
import Sidebar from './components/Sidebar';
import MetricsBar from './components/MetricsBar';
import GraphView from './components/GraphView';
import Analytics from './components/Analytics';
import NodeExplorer from './components/NodeExplorer';
import { getGraphMeta, buildGraphRenderUrl } from './api/api';


export default function App() {
  const [meta, setMeta] = useState(null);
  const [activeTab, setActiveTab] = useState('graph');

  // Filter state
  const [selectedTypes, setSelectedTypes] = useState([]);
  const [selectedRels, setSelectedRels]   = useState([]);
  const [minDegree, setMinDegree]         = useState(1);
  const [maxNodes, setMaxNodes]           = useState(200);
  const [search, setSearch]               = useState('');
  const [physicsOn, setPhysicsOn]         = useState(true);
  const [gravity, setGravity]             = useState(-200);

  useEffect(() => {
    getGraphMeta()
      .then(d => {
        setMeta(d);
        setSelectedTypes(d.entity_types);
        setSelectedRels(d.relationship_types);
      })
      .catch(console.error);
  }, []);

  const graphUrl = meta
    ? buildGraphRenderUrl({
        types: selectedTypes,
        rels: selectedRels,
        minDegree,
        maxNodes,
        search,
        physics: physicsOn,
        gravity,
      })
    : null;

  return (
    <div className="app-shell">
      <Sidebar
        meta={meta}
        selectedTypes={selectedTypes} setSelectedTypes={setSelectedTypes}
        selectedRels={selectedRels}   setSelectedRels={setSelectedRels}
        minDegree={minDegree}         setMinDegree={setMinDegree}
        maxNodes={maxNodes}           setMaxNodes={setMaxNodes}
        search={search}               setSearch={setSearch}
        physicsOn={physicsOn}         setPhysicsOn={setPhysicsOn}
        gravity={gravity}             setGravity={setGravity}
      />

      <div className="main">
        {/* Header */}
        <div className="page-header">
          <div className="page-header-badge">LAYER10</div>
          <div>
            <h1>Organizational Knowledge Graph</h1>
            <p>Capturing entities, decisions, and relationships from GitHub project history.</p>
          </div>
        </div>

        <MetricsBar meta={meta} />

        <div className="tabs">
          {[
            { id: 'graph',    label: 'Knowledge Graph' },
            { id: 'analytics', label: 'Analytics' },
            { id: 'explorer',  label: 'Node Explorer' },
          ].map(t => (
            <button
              key={t.id}
              className={`tab-btn ${activeTab === t.id ? 'active' : ''}`}
              onClick={() => setActiveTab(t.id)}
            >
              {t.label}
            </button>
          ))}
        </div>

        <div className="tab-content">
          {activeTab === 'graph'     && <GraphView graphUrl={graphUrl} meta={meta} selectedTypes={selectedTypes} selectedRels={selectedRels} />}
          {activeTab === 'analytics' && <Analytics />}
          {activeTab === 'explorer'  && <NodeExplorer />}
        </div>
      </div>
    </div>
  );
}
