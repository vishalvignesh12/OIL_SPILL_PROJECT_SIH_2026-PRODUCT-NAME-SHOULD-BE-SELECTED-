import React, { useState, useEffect, useMemo } from 'react';
import { useNavigation } from '../../context/NavigationContext';
import api from '../../services/api';
import DataTable from '../common/DataTable';
import StatusChip from '../common/StatusChip';
import Button from '../common/Button';
import Modal from '../common/Modal';

export default function DetectionRegistryView() {
  const { navigateTo } = useNavigation();
  const [detections, setDetections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newSighting, setNewSighting] = useState({
    region: 'Bay of Bengal',
    lat: '15.1024',
    lng: '88.4512',
    sensor: 'Visual Coastguard Aerial Patrol',
    estimatedVolume: '50 MT',
    severity: 'Medium'
  });

  useEffect(() => {
    async function loadDetections() {
      try {
        const data = await api.getDetections();
        setDetections(data);
      } catch (err) {
        console.error('Error fetching detections:', err);
      } finally {
        setLoading(false);
      }
    }
    loadDetections();
  }, []);

  const filteredDetections = useMemo(() => {
    return detections.filter(item => {
      if (severityFilter !== 'ALL' && item.severity.toUpperCase() !== severityFilter) {
        return false;
      }
      if (statusFilter !== 'ALL' && !item.status.toUpperCase().includes(statusFilter)) {
        return false;
      }
      if (search.trim()) {
        const q = search.toLowerCase();
        return (
          item.id.toLowerCase().includes(q) ||
          item.region.toLowerCase().includes(q) ||
          item.coordinates.toLowerCase().includes(q) ||
          (item.suspectVessel && item.suspectVessel.toLowerCase().includes(q)) ||
          item.sensor.toLowerCase().includes(q)
        );
      }
      return true;
    });
  }, [detections, severityFilter, statusFilter, search]);

  const handleAddSighting = (e) => {
    e.preventDefault();
    const newEntry = {
      id: `DET-2026-${String(detections.length + 90).padStart(3, '0')}`,
      incidentId: 'INC-2026-005',
      timestamp: `${new Date().toISOString().substring(0, 10)} ${new Date().toISOString().substring(11, 16)} UTC`,
      region: newSighting.region,
      coordinates: `${newSighting.lat}°N, ${newSighting.lng}°E`,
      sensor: newSighting.sensor,
      areaKm2: 14.2,
      estimatedVolume: newSighting.estimatedVolume,
      confidence: 85,
      severity: newSighting.severity,
      status: 'Investigating',
      suspectVessel: 'Under Attribution',
      attributionRank: null
    };

    setDetections([newEntry, ...detections]);
    setIsModalOpen(false);
  };

  const columns = [
    {
      header: 'Detection ID',
      key: 'id',
      width: '130px',
      render: (val, row) => (
        <span className="font-mono font-bold text-primary hover:underline cursor-pointer">
          {val}
        </span>
      )
    },
    {
      header: 'Timestamp (UTC)',
      key: 'timestamp',
      width: '160px',
      render: (val) => <span className="font-mono text-on-surface-variant text-[12px]">{val}</span>
    },
    {
      header: 'Region & Coordinates',
      key: 'region',
      render: (val, row) => (
        <div>
          <strong className="text-primary block text-label-md">{val}</strong>
          <span className="text-[11px] font-mono text-on-surface-variant">{row.coordinates}</span>
        </div>
      )
    },
    {
      header: 'Sensor / Source',
      key: 'sensor',
      render: (val) => (
        <span className="inline-flex items-center gap-1 text-[12px] font-medium text-on-surface">
          <span className="material-symbols-outlined text-[15px] text-secondary">satellite_alt</span>
          {val}
        </span>
      )
    },
    {
      header: 'Area (km²)',
      key: 'areaKm2',
      render: (val) => <strong className="text-primary font-mono">{val} km²</strong>
    },
    {
      header: 'Confidence',
      key: 'confidence',
      render: (val) => (
        <div className="flex items-center gap-2">
          <div className="w-16 bg-surface-container-high rounded-full h-1.5 overflow-hidden">
            <div
              className={`h-full rounded-full ${val >= 90 ? 'bg-secondary' : val >= 70 ? 'bg-tertiary-container' : 'bg-outline'}`}
              style={{ width: `${val}%` }}
            ></div>
          </div>
          <span className="font-mono font-bold text-[12px]">{val}%</span>
        </div>
      )
    },
    {
      header: 'Severity',
      key: 'severity',
      render: (val) => <StatusChip status={val} size="sm" />
    },
    {
      header: 'Attribution / Suspect',
      key: 'suspectVessel',
      render: (val, row) => (
        <div>
          <span className="text-label-md font-semibold text-primary block">{val}</span>
          <span className="text-[11px] text-on-surface-variant">{row.status}</span>
        </div>
      )
    },
    {
      header: 'Actions',
      key: 'actions',
      sortable: false,
      width: '180px',
      render: (_, row) => (
        <div className="flex items-center gap-1.5">
          <Button
            size="sm"
            variant="teal"
            icon="map"
            onClick={(e) => {
              e.stopPropagation();
              navigateTo('gis', { incidentId: row.incidentId || 'INC-2026-001' });
            }}
          >
            Inspect
          </Button>
          {row.suspectVessel && row.suspectVessel !== 'None' && (
            <Button
              size="sm"
              variant="outline"
              icon="fingerprint"
              onClick={(e) => {
                e.stopPropagation();
                navigateTo('attribution', { incidentId: row.incidentId || 'INC-2026-001' });
              }}
            >
              Attribution
            </Button>
          )}
        </div>
      )
    }
  ];

  return (
    <div className="flex flex-col gap-6 animate-in fade-in duration-150">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-headline-lg font-bold text-primary tracking-tight">
            Oil Spill Detection Registry
          </h1>
          <p className="text-body-md text-on-surface-variant">
            Master repository of satellite radar, optical, and aerial surveillance hydrocarbon observations.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            icon="download"
            onClick={() => alert('Registry exported to official CSV format.')}
          >
            Export CSV
          </Button>
          <Button
            variant="primary"
            icon="add_circle"
            onClick={() => setIsModalOpen(true)}
          >
            Manual Sighting Entry
          </Button>
        </div>
      </div>

      {/* Registry Summary KPI Strip */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-surface-container-low border border-outline-variant rounded-lg">
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-on-surface-variant block">
            Cataloged Slicks
          </span>
          <span className="text-[24px] font-bold text-primary font-mono">{detections.length}</span>
        </div>
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-on-surface-variant block">
            Active Discharges
          </span>
          <span className="text-[24px] font-bold text-error font-mono">
            {detections.filter(d => d.severity === 'Critical' || d.severity === 'High').length}
          </span>
        </div>
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-on-surface-variant block">
            Total Slick Coverage
          </span>
          <span className="text-[24px] font-bold text-secondary font-mono">
            {detections.reduce((acc, curr) => acc + curr.areaKm2, 0).toFixed(1)} km²
          </span>
        </div>
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-on-surface-variant block">
            Attributed Slicks
          </span>
          <span className="text-[24px] font-bold text-primary font-mono">
            {detections.filter(d => d.status === 'Attributed').length} / {detections.length}
          </span>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-4 p-4 bg-surface-container-lowest border border-outline-variant rounded">
        {/* Search */}
        <div className="relative w-full md:w-80">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-[18px]">
            search
          </span>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Filter by ID, region, vessel, sensor..."
            className="w-full pl-9 pr-4 py-2 bg-surface-container-low border border-outline-variant rounded text-label-md text-on-surface focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all"
          />
        </div>

        {/* Dropdown Filters */}
        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          <div className="flex items-center gap-2">
            <label className="text-label-sm font-bold text-on-surface-variant">Severity:</label>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="py-1.5 px-3 bg-surface-container-low border border-outline-variant rounded text-label-sm font-semibold text-primary focus:border-primary outline-none"
            >
              <option value="ALL">All Severities</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <label className="text-label-sm font-bold text-on-surface-variant">Status:</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="py-1.5 px-3 bg-surface-container-low border border-outline-variant rounded text-label-sm font-semibold text-primary focus:border-primary outline-none"
            >
              <option value="ALL">All Statuses</option>
              <option value="ATTRIBUTED">Attributed</option>
              <option value="INVESTIGATING">Investigating</option>
              <option value="CLOSED">Closed</option>
              <option value="CLEARED">Natural / Cleared</option>
            </select>
          </div>

          {(search || severityFilter !== 'ALL' || statusFilter !== 'ALL') && (
            <button
              onClick={() => {
                setSearch('');
                setSeverityFilter('ALL');
                setStatusFilter('ALL');
              }}
              className="text-label-sm text-secondary font-bold hover:underline ml-2"
            >
              Reset Filters
            </button>
          )}
        </div>
      </div>

      {/* Detections Data Table */}
      <DataTable
        columns={columns}
        data={filteredDetections}
        pageSize={8}
        onRowClick={(row) => navigateTo('gis', { incidentId: row.incidentId || 'INC-2026-001' })}
      />

      {/* Manual Sighting Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Register Manual Sighting Observation"
        subtitle="Log visual or radar reconnaissance telemetry into national database"
        footer={
          <>
            <Button variant="ghost" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleAddSighting}>
              Save Observation Record
            </Button>
          </>
        }
      >
        <form onSubmit={handleAddSighting} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-label-sm font-bold text-on-surface mb-1">
                Surveillance Region
              </label>
              <select
                value={newSighting.region}
                onChange={(e) => setNewSighting({ ...newSighting, region: e.target.value })}
                className="w-full p-2 bg-surface-container-low border border-outline-variant rounded text-label-md text-on-surface"
              >
                <option>Bay of Bengal</option>
                <option>Arabian Sea</option>
                <option>Gulf of Mannar</option>
                <option>Andaman & Nicobar</option>
                <option>Laccadive Sea</option>
              </select>
            </div>
            <div>
              <label className="block text-label-sm font-bold text-on-surface mb-1">
                Estimated Severity
              </label>
              <select
                value={newSighting.severity}
                onChange={(e) => setNewSighting({ ...newSighting, severity: e.target.value })}
                className="w-full p-2 bg-surface-container-low border border-outline-variant rounded text-label-md text-on-surface"
              >
                <option>Critical</option>
                <option>High</option>
                <option>Medium</option>
                <option>Low</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-label-sm font-bold text-on-surface mb-1">
                Latitude (°N)
              </label>
              <input
                type="text"
                value={newSighting.lat}
                onChange={(e) => setNewSighting({ ...newSighting, lat: e.target.value })}
                className="w-full p-2 bg-surface-container-low border border-outline-variant rounded text-label-md text-on-surface font-mono"
              />
            </div>
            <div>
              <label className="block text-label-sm font-bold text-on-surface mb-1">
                Longitude (°E)
              </label>
              <input
                type="text"
                value={newSighting.lng}
                onChange={(e) => setNewSighting({ ...newSighting, lng: e.target.value })}
                className="w-full p-2 bg-surface-container-low border border-outline-variant rounded text-label-md text-on-surface font-mono"
              />
            </div>
          </div>

          <div>
            <label className="block text-label-sm font-bold text-on-surface mb-1">
              Observation Sensor / Source
            </label>
            <input
              type="text"
              value={newSighting.sensor}
              onChange={(e) => setNewSighting({ ...newSighting, sensor: e.target.value })}
              className="w-full p-2 bg-surface-container-low border border-outline-variant rounded text-label-md text-on-surface"
            />
          </div>

          <div>
            <label className="block text-label-sm font-bold text-on-surface mb-1">
              Estimated Spill Volume (MT)
            </label>
            <input
              type="text"
              value={newSighting.estimatedVolume}
              onChange={(e) => setNewSighting({ ...newSighting, estimatedVolume: e.target.value })}
              className="w-full p-2 bg-surface-container-low border border-outline-variant rounded text-label-md text-on-surface"
            />
          </div>
        </form>
      </Modal>
    </div>
  );
}
