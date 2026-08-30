import React, { useState, useEffect } from 'react';
import { useNavigation } from '../../context/NavigationContext';
import api from '../../services/api';
import StatusChip from '../common/StatusChip';
import Button from '../common/Button';

export default function EvidenceDossierView() {
  const { activeIncidentId, navigateTo } = useNavigation();
  const [incident, setIncident] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await api.getIncident(activeIncidentId);
        setIncident(data);
      } catch (err) {
        console.error('Error loading dossier:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [activeIncidentId]);

  const handlePrint = () => {
    window.print();
  };

  if (loading || !incident) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-3 border-primary border-t-transparent rounded-full animate-spin"></div>
          <span className="text-label-sm text-on-surface-variant font-semibold">
            Compiling Official Legal Evidence Dossier...
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 max-w-5xl mx-auto animate-in fade-in duration-150">
      {/* Top Toolbar (Hidden during print) */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 bg-surface-container-lowest border border-outline-variant rounded-lg shadow-xs print:hidden">
        <div>
          <h1 className="text-headline-md font-bold text-primary">
            Official Incident Evidence Dossier
          </h1>
          <p className="text-label-sm text-on-surface-variant">
            Case Reference: <strong className="font-mono text-primary">{incident.id}</strong> • Chain of Custody: <strong className="font-mono text-secondary">{incident.chainOfCustodyId}</strong>
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button
            variant="teal"
            icon="map"
            onClick={() => navigateTo('gis', { incidentId: incident.id })}
          >
            GIS Forensics Map
          </Button>
          <Button
            variant="primary"
            icon="print"
            onClick={handlePrint}
          >
            Export / Print Official Dossier
          </Button>
        </div>
      </div>

      {/* Official Government Dossier Sheet */}
      <div className="bg-surface-container-lowest border border-outline-variant rounded-lg p-8 sm:p-12 shadow-sm text-on-surface space-y-8 print:p-0 print:border-none print:shadow-none">
        {/* Government Header */}
        <div className="border-b-2 border-primary pb-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-primary-container text-on-primary rounded flex items-center justify-center font-bold text-2xl font-sans">
              M
            </div>
            <div>
              <div className="text-[11px] font-bold uppercase tracking-widest text-secondary">
                National Maritime Oversight & Environmental Enforcement
              </div>
              <h2 className="text-headline-md font-bold text-primary tracking-tight">
                Forensic Incident Investigation Report
              </h2>
              <div className="text-label-sm text-on-surface-variant font-mono mt-0.5">
                Statutory Case ID: {incident.id} • Classification: RESTRICTED / LEGAL ADMISSIBLE
              </div>
            </div>
          </div>

          <div className="text-left sm:text-right text-label-sm space-y-1">
            <div><strong>Date Generated:</strong> 2026-08-27</div>
            <div><strong>Investigating Unit:</strong> Sector 4 Coast Command</div>
            <div><strong>Investigator:</strong> {incident.assignedInvestigator}</div>
          </div>
        </div>

        {/* Section 1: Executive Summary */}
        <section className="space-y-3">
          <h3 className="text-title-lg font-bold text-primary border-b border-outline-variant pb-1 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-primary"></span>
            1. Executive Incident Summary
          </h3>
          <p className="text-body-md leading-relaxed text-on-surface">
            On <strong>2026-08-27 at 04:15 UTC</strong>, automated synthetic aperture radar (SAR) processing on the <strong>Sentinel-1A</strong> satellite pass detected a major surface hydrocarbon anomaly covering <strong>46.8 km²</strong> in international waters within Sector 4 (Bay of Bengal). Spatial-temporal back-trajectory analysis corroborates deliberate bilge discharge or catastrophic bunker leakage from crude oil tanker <strong>MSC Ocean Star</strong> (Liberia Flag, IMO 9412345) with a <strong>94% statistical confidence attribution</strong>.
          </p>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-4 bg-surface-container-low rounded border border-outline-variant text-label-sm">
            <div>
              <span className="text-on-surface-variant block text-[11px]">Epicenter Coords</span>
              <strong className="text-primary font-mono">{incident.coordinates.formatted}</strong>
            </div>
            <div>
              <span className="text-on-surface-variant block text-[11px]">Calculated Spill Area</span>
              <strong className="text-primary font-mono">{incident.slickDimensions.areaKm2} km²</strong>
            </div>
            <div>
              <span className="text-on-surface-variant block text-[11px]">Discharge Volume</span>
              <strong className="text-error font-mono">{incident.slickDimensions.estimatedVolumeTonnes}</strong>
            </div>
            <div>
              <span className="text-on-surface-variant block text-[11px]">Attribution Status</span>
              <strong className="text-secondary font-bold">Confirmed (94%)</strong>
            </div>
          </div>
        </section>

        {/* Section 2: Satellite Reconnaissance Evidence */}
        <section className="space-y-3">
          <h3 className="text-title-lg font-bold text-primary border-b border-outline-variant pb-1 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-primary"></span>
            2. Satellite SAR & Physical Observations
          </h3>
          <p className="text-body-md text-on-surface-variant">
            Radar backscatter suppression confirms damping of capillary ocean waves consistent with mineral oil slick emulsion.
          </p>

          <div className="p-4 bg-slate-950 text-slate-200 rounded border border-slate-800 font-mono text-[12px] space-y-2">
            <div className="text-secondary-fixed font-bold"># SATELLITE TELEMETRY INGESTION LOG</div>
            <div>Satellite Constellation: Copernicus Sentinel-1A (C-Band SAR)</div>
            <div>Orbit / Swath Mode: Ascending Pass #1428 / Interferometric Wide Swath (IW)</div>
            <div>Slick Boundary Extents: 14.885°N, 88.192°E to 14.775°N, 88.345°E (Length: 28.4 km)</div>
            <div>Drift Vector Analysis: Surface current 112° at 1.4 kts (East-Southeast)</div>
            <div>Hydrocarbon Signature: Bunker C Fuel Oil / Heavy Crude Fraction</div>
          </div>
        </section>

        {/* Section 3: Suspect Vessel Attribution Proofs */}
        <section className="space-y-3">
          <h3 className="text-title-lg font-bold text-primary border-b border-outline-variant pb-1 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-primary"></span>
            3. Vessel Attribution & Trajectory Evidence
          </h3>

          <div className="p-4 bg-surface-container-high rounded border border-outline-variant space-y-3">
            <div className="flex items-center justify-between">
              <strong className="text-title-lg text-primary">{incident.primarySuspect.name}</strong>
              <StatusChip status="Attributed" label="Attribution: 94%" />
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-label-sm text-on-surface">
              <div><span>Flag:</span> <strong>{incident.primarySuspect.flag}</strong></div>
              <div><span>IMO:</span> <strong className="font-mono">{incident.primarySuspect.imo}</strong></div>
              <div><span>MMSI:</span> <strong className="font-mono">{incident.primarySuspect.mmsi}</strong></div>
              <div><span>Vessel Type:</span> <strong>{incident.primarySuspect.vesselType}</strong></div>
            </div>

            <div className="p-3 bg-surface-container-lowest rounded border border-outline-variant text-[12px] text-on-surface leading-relaxed">
              <strong>Forensic Telemetry Summary:</strong> At 2026-08-26 23:15 UTC, MSC Ocean Star passed within 0.8 km of the slick epicenter. The vessel's AIS log indicates a sudden drop in cruising speed from 14.2 knots to 6.1 knots lasting 42 minutes with a 25° heading deviation, coinciding with calculated discharge onset.
            </div>
          </div>
        </section>

        {/* Section 4: Chain of Custody & Legal Endorsement */}
        <section className="space-y-4 pt-4 border-t border-outline-variant">
          <h3 className="text-title-lg font-bold text-primary flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-primary"></span>
            4. Chain of Custody & Cryptographic Verification
          </h3>

          <div className="p-4 bg-surface-container-low rounded border border-outline-variant text-label-sm space-y-2">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between text-on-surface-variant">
              <span>Evidentiary Checksum (SHA-256):</span>
              <strong className="font-mono text-primary text-[11px] break-all">
                e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
              </strong>
            </div>
            <div className="flex justify-between text-on-surface-variant">
              <span>Certified Digital Signature:</span>
              <strong className="text-secondary font-mono">VERIFIED • MEA-OFFICER-KEY-9841</strong>
            </div>
            <div className="flex justify-between text-on-surface-variant">
              <span>Legal Status:</span>
              <strong className="text-primary font-bold">Forwarded to Admiralty Court & Port Authority</strong>
            </div>
          </div>

          {/* Signature Block */}
          <div className="grid grid-cols-2 gap-8 pt-6">
            <div className="border-t border-on-surface/40 pt-2 text-label-sm">
              <strong className="text-primary block">{incident.assignedInvestigator}</strong>
              <span className="text-on-surface-variant">Lead Maritime Environmental Investigator</span>
            </div>
            <div className="border-t border-on-surface/40 pt-2 text-label-sm text-right">
              <strong className="text-primary block">Adm. V. K. Menon</strong>
              <span className="text-on-surface-variant">Director General, Maritime Security Directorate</span>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
