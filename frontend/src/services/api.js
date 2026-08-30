/**
 * API Service Layer
 *
 * Connects React frontend to the FastAPI backend at VITE_API_URL.
 * Falls back to mock data if the backend is unavailable (dev/offline mode).
 *
 * Backend endpoints used:
 *   POST /auth/login          — get JWT token
 *   GET  /auth/me             — get logged-in user profile
 *   GET  /incidents           — list all incidents
 *   GET  /incidents/:id       — single incident detail
 *   GET  /vessels             — list all vessels
 *   GET  /vessels/:id         — single vessel detail
 *   GET  /vessels/:id/track   — AIS track points for a vessel
 *   GET  /ais                 — AIS tracks filtered by time & bbox
 *   POST /attribution/score   — run vessel attribution scoring
 *   POST /detections/analyze  — analyze a satellite scene for oil slick
 *
 * Map tiles (CartoDB/OSM) are loaded directly by Leaflet — no backend needed.
 */

import {
  systemMetrics,
  currentIncident,
  detectionsRegistry,
  candidateVessels,
  vesselProfileMSC,
  securityAlerts,
  geographicLayers
} from './mockData';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// ─── Auth Token Helpers ──────────────────────────────────────────────────────

function getToken() {
  return localStorage.getItem('auth_token');
}

function setToken(token) {
  localStorage.setItem('auth_token', token);
}

function clearToken() {
  localStorage.removeItem('auth_token');
}

// ─── Core Fetch Wrapper ──────────────────────────────────────────────────────

async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers });

  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({}));
    throw new Error(errorBody.detail || `HTTP ${res.status}: ${res.statusText}`);
  }

  return res.json();
}

// ─── Simulated delay for mock fallback (realistic UX) ───────────────────────
const delay = (ms = 100) => new Promise(resolve => setTimeout(resolve, ms));

// ─── API Methods ─────────────────────────────────────────────────────────────

export const api = {

  // ── Authentication ──────────────────────────────────────────────────────

  /**
   * Log in with username/password → returns JWT access_token.
   * Stores token in localStorage for subsequent protected requests.
   */
  async login(username, password) {
    try {
      const data = await apiFetch('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      });
      if (data.access_token) {
        setToken(data.access_token);
      }
      return data;
    } catch {
      // Mock fallback for dev/demo
      await delay();
      const mockToken = 'mock_jwt_token_dev_only';
      setToken(mockToken);
      return { access_token: mockToken, token_type: 'bearer' };
    }
  },

  /** Get the currently logged-in user's profile. */
  async getMe() {
    try {
      return await apiFetch('/auth/me');
    } catch {
      await delay();
      return { id: '1', name: 'Demo Analyst', email: 'analyst@nmoss.gov', role: 'analyst' };
    }
  },

  /** Remove token and log out. */
  logout() {
    clearToken();
  },

  // ── Incidents ────────────────────────────────────────────────────────────

  /**
   * List all incidents (optionally filtered by status, start_date, end_date).
   * Backend: GET /incidents?status=...&start_date=...&end_date=...
   */
  async getIncidents(filters = {}) {
    try {
      const params = new URLSearchParams();
      if (filters.status) params.set('status', filters.status);
      if (filters.start_date) params.set('start_date', filters.start_date);
      if (filters.end_date) params.set('end_date', filters.end_date);
      const qs = params.toString() ? `?${params}` : '';
      return await apiFetch(`/incidents${qs}`);
    } catch {
      await delay();
      return [currentIncident];
    }
  },

  /**
   * Get a single incident by ID.
   * Backend: GET /incidents/:id
   */
  async getIncident(id = 'INC-2026-001') {
    try {
      return await apiFetch(`/incidents/${id}`);
    } catch {
      await delay();
      return { ...currentIncident, id };
    }
  },

  // ── System Metrics (mock only — no dedicated backend endpoint yet) ────────

  /**
   * Overview KPI metrics for the command dashboard.
   * Falls back to mock data until a /metrics endpoint is added to the backend.
   */
  async getSystemMetrics() {
    await delay();
    return { ...systemMetrics };
  },

  // ── Vessels ──────────────────────────────────────────────────────────────

  /**
   * List all registered vessels.
   * Backend: GET /vessels
   */
  async getVessels() {
    try {
      return await apiFetch('/vessels');
    } catch {
      await delay();
      return candidateVessels.map(v => ({
        id: v.id,
        mmsi: v.mmsi,
        imo: v.imo,
        name: v.name,
        type: v.type,
        flag: v.flag,
        length: v.length,
      }));
    }
  },

  /**
   * Get details for a single vessel.
   * Backend: GET /vessels/:id
   */
  async getVesselById(id) {
    try {
      return await apiFetch(`/vessels/${id}`);
    } catch {
      await delay();
      return { ...vesselProfileMSC };
    }
  },

  /**
   * Get forensic profile for a vessel by name (uses mock lookup by name).
   * For real backend use getVesselById(id) instead.
   */
  async getVesselProfile(vesselName = 'MSC Ocean Star') {
    try {
      // Try to find by name via list endpoint
      const vessels = await apiFetch('/vessels');
      const match = vessels.find(v => v.name?.toLowerCase() === vesselName.toLowerCase());
      if (match) {
        return await apiFetch(`/vessels/${match.id}`);
      }
      throw new Error('Vessel not found');
    } catch {
      await delay();
      if (vesselName.toLowerCase().includes('ocean star') || vesselName.toLowerCase().includes('msc')) {
        return { ...vesselProfileMSC };
      }
      const match = candidateVessels.find(v => v.name.toLowerCase() === vesselName.toLowerCase());
      return match
        ? { ...match, ...vesselProfileMSC, name: match.name, imo: match.imo, mmsi: match.mmsi }
        : vesselProfileMSC;
    }
  },

  /**
   * Get AIS track history for a specific vessel.
   * Backend: GET /vessels/:id/track
   */
  async getVesselTrack(vesselId) {
    try {
      return await apiFetch(`/vessels/${vesselId}/track`);
    } catch {
      await delay();
      return { vessel_id: vesselId, track: [] };
    }
  },

  // ── AIS Tracks ───────────────────────────────────────────────────────────

  /**
   * Retrieve AIS tracks filtered by time window and optional bounding box.
   * Backend: GET /ais?start_time=...&end_time=...&bbox=...&vessel_id=...
   *
   * @param {string} startTime  ISO datetime string
   * @param {string} endTime    ISO datetime string
   * @param {string} [bbox]     "minLon,minLat,maxLon,maxLat"
   * @param {string} [vesselId] UUID of specific vessel
   */
  async getAISTracks(startTime, endTime, bbox = null, vesselId = null) {
    try {
      const params = new URLSearchParams({ start_time: startTime, end_time: endTime });
      if (bbox) params.set('bbox', bbox);
      if (vesselId) params.set('vessel_id', vesselId);
      return await apiFetch(`/ais?${params}`);
    } catch {
      await delay();
      return [];
    }
  },

  // ── Attribution ──────────────────────────────────────────────────────────

  /**
   * Run vessel attribution scoring for an incident.
   * Backend: POST /attribution/score
   *
   * @param {string} incidentId   UUID of the incident
   * @param {string} detectionId  UUID of the slick detection
   * @param {string} startTime    ISO datetime — beginning of spill window
   * @param {string} endTime      ISO datetime — end of spill window
   */
  async getAttributionScores(incidentId, detectionId, startTime, endTime) {
    try {
      return await apiFetch('/attribution/score', {
        method: 'POST',
        body: JSON.stringify({ incident_id: incidentId, detection_id: detectionId, start_time: startTime, end_time: endTime }),
      });
    } catch {
      await delay();
      return { ranked_vessels: candidateVessels };
    }
  },

  /**
   * Get ranked candidate vessels for an incident (mock-compatible alias).
   * Uses attribution scoring with default time window if no IDs provided.
   */
  async getAttributedVessels(incidentId = 'INC-2026-001') {
    try {
      const now = new Date().toISOString();
      const yesterday = new Date(Date.now() - 86400000).toISOString();
      const result = await apiFetch('/attribution/score', {
        method: 'POST',
        body: JSON.stringify({ incident_id: incidentId, start_time: yesterday, end_time: now }),
      });
      return result.ranked_vessels || [];
    } catch {
      await delay();
      return [...candidateVessels];
    }
  },

  // ── Detections ───────────────────────────────────────────────────────────

  /**
   * Get all oil spill detection records from mock data (filtered locally).
   * No dedicated GET /detections list endpoint exists yet — using mock.
   */
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

  /**
   * Analyze a satellite scene for oil slick detection.
   * Backend: POST /detections/analyze
   *
   * @param {string} sceneId   Scene ID string
   * @param {string} imageUrl  URL of the satellite scene image
   * @param {string} timestamp ISO datetime of the scene
   */
  async analyzeScene(sceneId, imageUrl, timestamp) {
    try {
      return await apiFetch('/detections/analyze', {
        method: 'POST',
        body: JSON.stringify({ scene_id: sceneId, image_url: imageUrl, timestamp }),
      });
    } catch {
      await delay();
      return null;
    }
  },

  // ── Alerts ───────────────────────────────────────────────────────────────

  /**
   * Get security alerts list (mock only — no backend alerts endpoint yet).
   */
  async getAlerts() {
    await delay();
    return [...securityAlerts];
  },

  /**
   * Acknowledge an alert (mock only).
   */
  async acknowledgeAlert(alertId, acknowledgedBy = 'Surveillance Officer') {
    await delay();
    const alert = securityAlerts.find(a => a.id === alertId);
    if (alert) {
      alert.acknowledged = true;
      alert.acknowledgedBy = `${acknowledgedBy} (${new Date().toISOString().substring(11, 16)} UTC)`;
    }
    return { success: true, alert };
  },

  // ── Map Layers ───────────────────────────────────────────────────────────

  /**
   * Get GeoJSON map layer geometries (mock only).
   * Map tiles are loaded directly by Leaflet from CartoDB/OSM — no backend needed.
   */
  async getMapLayers(incidentId = 'INC-2026-001') {
    await delay();
    return { ...geographicLayers };
  },
};

export default api;
