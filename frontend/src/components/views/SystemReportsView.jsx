import React, { useState } from 'react';
import Button from '../common/Button';

export default function SystemReportsView() {
  const [reportFormat, setReportFormat] = useState('PDF');
  const [schedule, setSchedule] = useState('DAILY');

  const reportTemplates = [
    {
      id: 'REP-01',
      title: 'National Coastal Surveillance Summary',
      frequency: 'Daily (06:00 UTC)',
      type: 'Executive Overview',
      format: 'PDF / GeoJSON',
      recipients: 'Ministry of Environment, Coast Guard HQ'
    },
    {
      id: 'REP-02',
      title: 'Hydrocarbon Discharge Evidentiary Registry',
      frequency: 'Weekly (Monday)',
      type: 'Legal Audit Dossier',
      format: 'PDF / CSV',
      recipients: 'Maritime Enforcement Directorate'
    },
    {
      id: 'REP-03',
      title: 'AIS Vessel Dark-Event & AIS Gap Analysis',
      frequency: 'Real-time On Demand',
      type: 'Tactical Reconnaissance',
      format: 'Shapefile / KML',
      recipients: 'Port State Control & Patrol Cutters'
    }
  ];

  return (
    <div className="flex flex-col gap-6 max-w-5xl mx-auto animate-in fade-in duration-150">
      <div>
        <h1 className="text-headline-lg font-bold text-primary tracking-tight">
          System Reports & Automated Intelligence
        </h1>
        <p className="text-body-md text-on-surface-variant">
          Schedule automated governmental briefings, export GIS spatial datasets, and configure sensor ingestion parameters.
        </p>
      </div>

      {/* Quick Generate Action Box */}
      <div className="bg-surface-container-lowest border border-outline-variant rounded-lg p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 shadow-xs">
        <div className="space-y-1">
          <h3 className="text-title-lg font-bold text-primary">Generate Custom Intelligence Report</h3>
          <p className="text-label-sm text-on-surface-variant">
            Export unified analytics across all active incidents, radar satellite passes, and vessel attributions.
          </p>
        </div>

        <div className="flex items-center gap-3 w-full md:w-auto">
          <select
            value={reportFormat}
            onChange={(e) => setReportFormat(e.target.value)}
            className="p-2.5 bg-surface-container-low border border-outline-variant rounded text-label-md text-primary font-bold outline-none"
          >
            <option value="PDF">Format: Official PDF</option>
            <option value="GEOJSON">Format: GeoJSON Vector</option>
            <option value="CSV">Format: Raw CSV Data</option>
            <option value="SHP">Format: ESRI Shapefile</option>
          </select>
          <Button
            variant="primary"
            icon="download"
            onClick={() => alert(`Generating ${reportFormat} report package...`)}
          >
            Export Now
          </Button>
        </div>
      </div>

      {/* Scheduled Briefings Table */}
      <div className="bg-surface-container-lowest border border-outline-variant rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-title-lg font-bold text-primary">Scheduled Surveillance Briefings</h3>
          <span className="text-label-sm text-secondary font-bold flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-secondary animate-pulse"></span>
            Cron Dispatcher Active
          </span>
        </div>

        <div className="divide-y divide-outline-variant/60">
          {reportTemplates.map((rep) => (
            <div key={rep.id} className="py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-label-sm font-bold text-primary">{rep.id}</span>
                  <strong className="text-title-lg text-primary">{rep.title}</strong>
                </div>
                <div className="text-label-sm text-on-surface-variant">
                  <span>Frequency: <strong>{rep.frequency}</strong></span> • <span>Recipients: {rep.recipients}</span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  icon="visibility"
                  onClick={() => alert(`Previewing template ${rep.id}`)}
                >
                  Preview
                </Button>
                <Button
                  size="sm"
                  variant="primary"
                  icon="send"
                  onClick={() => alert(`Triggering instant dispatch for ${rep.title}`)}
                >
                  Dispatch
                </Button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
