import React, { useState } from 'react';
import Button from '../common/Button';

export default function SettingsView() {
  const [sarConfidenceThreshold, setSarConfidenceThreshold] = useState(75);
  const [aisBufferDistanceKm, setAisBufferDistanceKm] = useState(15);
  const [autoDossierGeneration, setAutoDossierGeneration] = useState(true);
  const [darkMapTiles, setDarkMapTiles] = useState(true);

  return (
    <div className="flex flex-col gap-6 max-w-4xl mx-auto animate-in fade-in duration-150">
      <div>
        <h1 className="text-headline-lg font-bold text-primary tracking-tight">
          Surveillance System & Terminal Configuration
        </h1>
        <p className="text-body-md text-on-surface-variant">
          Manage officer operational parameters, machine learning attribution sensitivity, and display preferences.
        </p>
      </div>

      {/* Officer Terminal Profile */}
      <div className="bg-surface-container-lowest border border-outline-variant rounded-lg p-6 space-y-4">
        <h3 className="text-title-lg font-bold text-primary border-b border-outline-variant pb-2">
          Officer Operational Credentials
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-label-md">
          <div>
            <label className="block text-label-sm font-bold text-on-surface-variant mb-1">
              Officer Name
            </label>
            <input
              type="text"
              readOnly
              value="Cmdr. Rajesh Verma"
              className="w-full p-2.5 bg-surface-container-low border border-outline-variant rounded font-semibold text-primary"
            />
          </div>

          <div>
            <label className="block text-label-sm font-bold text-on-surface-variant mb-1">
              Command Unit / Directorate
            </label>
            <input
              type="text"
              readOnly
              value="Sector 4 Maritime Environmental Enforcement Command"
              className="w-full p-2.5 bg-surface-container-low border border-outline-variant rounded font-semibold text-primary"
            />
          </div>

          <div>
            <label className="block text-label-sm font-bold text-on-surface-variant mb-1">
              Security Clearance Level
            </label>
            <input
              type="text"
              readOnly
              value="Level 4 (Admiralty Forensic Investigator)"
              className="w-full p-2.5 bg-surface-container-low border border-outline-variant rounded font-semibold text-secondary font-mono"
            />
          </div>

          <div>
            <label className="block text-label-sm font-bold text-on-surface-variant mb-1">
              Cryptographic Token ID
            </label>
            <input
              type="text"
              readOnly
              value="MEA-OFFICER-KEY-9841-SHA256"
              className="w-full p-2.5 bg-surface-container-low border border-outline-variant rounded font-semibold text-primary font-mono text-[12px]"
            />
          </div>
        </div>
      </div>

      {/* ML Attribution Engine Sensitivity Controls */}
      <div className="bg-surface-container-lowest border border-outline-variant rounded-lg p-6 space-y-5">
        <h3 className="text-title-lg font-bold text-primary border-b border-outline-variant pb-2">
          Automated Attribution & GIS Model Parameters
        </h3>

        <div className="space-y-4">
          <div>
            <div className="flex items-center justify-between text-label-md mb-1">
              <span className="font-bold text-primary">Minimum SAR Detection Confidence Threshold</span>
              <strong className="text-secondary font-mono text-[16px]">{sarConfidenceThreshold}%</strong>
            </div>
            <input
              type="range"
              min="50"
              max="95"
              value={sarConfidenceThreshold}
              onChange={(e) => setSarConfidenceThreshold(parseInt(e.target.value, 10))}
              className="w-full h-2 bg-surface-container-high rounded appearance-none cursor-pointer accent-primary"
            />
            <p className="text-[12px] text-on-surface-variant mt-1">
              Satellite radar observations below this threshold are categorized as natural seeps or unverified.
            </p>
          </div>

          <div>
            <div className="flex items-center justify-between text-label-md mb-1">
              <span className="font-bold text-primary">AIS Corridor Trajectory Buffer Distance</span>
              <strong className="text-secondary font-mono text-[16px]">{aisBufferDistanceKm} km</strong>
            </div>
            <input
              type="range"
              min="5"
              max="50"
              value={aisBufferDistanceKm}
              onChange={(e) => setAisBufferDistanceKm(parseInt(e.target.value, 10))}
              className="w-full h-2 bg-surface-container-high rounded appearance-none cursor-pointer accent-primary"
            />
            <p className="text-[12px] text-on-surface-variant mt-1">
              Spatial radius around slick epicenter queried for suspect vessel transponder pings.
            </p>
          </div>

          <div className="flex items-center justify-between p-3 bg-surface-container-low rounded border border-outline-variant">
            <div>
              <strong className="text-label-md text-primary block">Auto-Compile Legal Evidence Dossier</strong>
              <span className="text-[12px] text-on-surface-variant">
                Automatically generate cryptographic chain-of-custody for attributions &gt; 90% confidence.
              </span>
            </div>
            <input
              type="checkbox"
              checked={autoDossierGeneration}
              onChange={(e) => setAutoDossierGeneration(e.target.checked)}
              className="rounded border-outline text-primary focus:ring-primary h-5 w-5 cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between p-3 bg-surface-container-low rounded border border-outline-variant">
            <div>
              <strong className="text-label-md text-primary block">High-Contrast Tactical Dark Map Tiles</strong>
              <span className="text-[12px] text-on-surface-variant">
                Recommended for low-light command center operational rooms.
              </span>
            </div>
            <input
              type="checkbox"
              checked={darkMapTiles}
              onChange={(e) => setDarkMapTiles(e.target.checked)}
              className="rounded border-outline text-primary focus:ring-primary h-5 w-5 cursor-pointer"
            />
          </div>
        </div>

        <div className="flex justify-end pt-2">
          <Button
            variant="primary"
            icon="save"
            onClick={() => alert('Operational settings saved successfully.')}
          >
            Save Parameter Changes
          </Button>
        </div>
      </div>
    </div>
  );
}
