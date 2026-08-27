import {
  systemMetrics,
  currentIncident,
  detectionsRegistry,
  candidateVessels,
  vesselProfileMSC,
  securityAlerts,
  geographicLayers
} from './mockData';

// Simulated network latency (100ms) for realistic UX and testing
const delay = (ms = 100) => new Promise(resolve => setTimeout(resolve, ms));

export const api = {
  // Get overview KPI metrics
  async getSystemMetrics() {
    await delay();
    return { ...systemMetrics };
  },

  // Get active incident details
  async getIncident(id = 'INC-2026-001') {
    await delay();
    if (id === currentIncident.id) {
      return { ...currentIncident };
    }
    return { ...currentIncident, id };
  },

  // Get all oil spill detection records with optional filters
  async getDetections(filters = {}) {
    await delay();
    let list = [...detectionsRegistry];
    if (filters.severity) {
      list = list.filter(d => d.severity.toLowerCase() === filters.severity.toLowerCase());
    }
    if (filters.status) {
      list = list.filter(d => d.status.toLowerCase().includes(filters.status.toLowerCase()));
    }
    if (filters.search) {
      const q = filters.search.toLowerCase();
      list = list.filter(d => 
        d.id.toLowerCase().includes(q) ||
        d.region.toLowerCase().includes(q) ||
        (d.suspectVessel && d.suspectVessel.toLowerCase().includes(q))
      );
    }
    return list;
  },

  // Get ranked candidate vessels for attribution
  async getAttributedVessels(incidentId = 'INC-2026-001') {
    await delay();
    return [...candidateVessels];
  },

  // Get deep forensic profile for a specific vessel
  async getVesselProfile(vesselName = 'MSC Ocean Star') {
    await delay();
    if (vesselName.toLowerCase().includes('ocean star') || vesselName.toLowerCase().includes('msc')) {
      return { ...vesselProfileMSC };
    }
    const match = candidateVessels.find(v => v.name.toLowerCase() === vesselName.toLowerCase());
    return match ? { ...match, ...vesselProfileMSC, name: match.name, imo: match.imo, mmsi: match.mmsi } : vesselProfileMSC;
  },

  // Get alerts list
  async getAlerts() {
    await delay();
    return [...securityAlerts];
  },

  // Acknowledge an alert
  async acknowledgeAlert(alertId, acknowledgedBy = 'Surveillance Officer') {
    await delay();
    const alert = securityAlerts.find(a => a.id === alertId);
    if (alert) {
      alert.acknowledged = true;
      alert.acknowledgedBy = `${acknowledgedBy} (${new Date().toISOString().substring(11, 16)} UTC)`;
    }
    return { success: true, alert };
  },

  // Get map layers geometry
  async getMapLayers(incidentId = 'INC-2026-001') {
    await delay();
    return { ...geographicLayers };
  }
};

export default api;
