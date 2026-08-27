/**
 * Maritime Oversight & Forensic Intelligence Mock Data
 * Structured based on INC-2026-001 (Bay of Bengal incident)
 */

export const systemMetrics = {
  activeIncidents: 3,
  activeIncidentsChange: "+1 this week",
  monitoredVessels: 1428,
  monitoredVesselsChange: "+12% vs last 24h",
  verifiedSlicks: 12,
  verifiedSlicksArea: "184.6 km² total",
  attributionRate: "94.2%",
  attributionRateStatus: "High confidence",
  surveillanceCoverage: "98.4%",
  surveillanceStatus: "Operational",
  lastSatellitePass: "Sentinel-1A (18 mins ago)",
  systemHealth: "100% Online"
};

export const currentIncident = {
  id: "INC-2026-001",
  title: "Major Marine Hydrocarbon Discharge",
  region: "Bay of Bengal",
  zone: "International Maritime Corridor / Sector 4",
  coordinates: {
    lat: 14.8214,
    lng: 88.2915,
    formatted: "14°49'17\"N, 88°17'29\"E"
  },
  detectionTimestamp: "2026-08-27T04:15:00Z",
  estimatedSpillTime: "2026-08-26T22:30:00Z - 2026-08-27T01:00:00Z",
  confidence: 94,
  severity: "Critical",
  status: "Attributed",
  sensor: "Sentinel-1A C-SAR (Interferometric Wide Swath)",
  slickDimensions: {
    lengthKm: 28.4,
    widthKm: 4.2,
    areaKm2: 46.8,
    estimatedVolumeTonnes: "320 - 450 MT",
    slickType: "Heavy fuel oil (Bunker C emulsion)",
    driftVector: "112° at 1.4 knots (ESE)"
  },
  primarySuspect: {
    name: "MSC Ocean Star",
    mmsi: "211832000",
    imo: "9412345",
    flag: "Liberia",
    flagCode: "LR",
    vesselType: "Crude Oil Tanker",
    dwt: 115000,
    confidence: 94
  },
  assignedInvestigator: "Cmdr. Rajesh Verma (Maritime Enforcement Authority)",
  chainOfCustodyId: "COC-BOB-2026-0827-01",
  legalStatus: "Formal Evidentiary Dossier Compiled"
};

export const detectionsRegistry = [
  {
    id: "DET-2026-089",
    incidentId: "INC-2026-001",
    timestamp: "2026-08-27 04:15 UTC",
    region: "Bay of Bengal",
    coordinates: "14°49'17\"N, 88°17'29\"E",
    sensor: "Sentinel-1A SAR",
    areaKm2: 46.8,
    estimatedVolume: "380 MT",
    confidence: 94,
    severity: "Critical",
    status: "Attributed",
    suspectVessel: "MSC Ocean Star",
    attributionRank: 1
  },
  {
    id: "DET-2026-088",
    incidentId: "INC-2026-002",
    timestamp: "2026-08-26 19:40 UTC",
    region: "Arabian Sea",
    coordinates: "18°12'05\"N, 69°45'22\"E",
    sensor: "Sentinel-1B SAR",
    areaKm2: 18.2,
    estimatedVolume: "110 MT",
    confidence: 88,
    severity: "High",
    status: "Investigating",
    suspectVessel: "Golden Horizon",
    attributionRank: 2
  },
  {
    id: "DET-2026-087",
    incidentId: "INC-2026-003",
    timestamp: "2026-08-26 11:20 UTC",
    region: "Gulf of Mannar",
    coordinates: "08°44'30\"N, 78°51'10\"E",
    sensor: "RADARSAT-2",
    areaKm2: 7.4,
    estimatedVolume: "35 MT",
    confidence: 76,
    severity: "Medium",
    status: "Investigating",
    suspectVessel: "Pacific Pioneer",
    attributionRank: 3
  },
  {
    id: "DET-2026-086",
    incidentId: "INC-2026-004",
    timestamp: "2026-08-25 22:05 UTC",
    region: "Strait of Malacca",
    coordinates: "02°55'18\"N, 101°12'45\"E",
    sensor: "Sentinel-1A SAR",
    areaKm2: 32.6,
    estimatedVolume: "240 MT",
    confidence: 96,
    severity: "Critical",
    status: "Closed / Actioned",
    suspectVessel: "Stellar Galaxy",
    attributionRank: 1
  },
  {
    id: "DET-2026-085",
    incidentId: null,
    timestamp: "2026-08-25 14:18 UTC",
    region: "Laccadive Sea",
    coordinates: "10°05'22\"N, 75°28'14\"E",
    sensor: "ALOS-2 PALSAR",
    areaKm2: 3.1,
    estimatedVolume: "12 MT",
    confidence: 52,
    severity: "Low",
    status: "Natural Seep / Cleared",
    suspectVessel: "None",
    attributionRank: null
  },
  {
    id: "DET-2026-084",
    incidentId: null,
    timestamp: "2026-08-24 08:50 UTC",
    region: "Bay of Bengal (South)",
    coordinates: "11°20'40\"N, 86°35'10\"E",
    sensor: "Sentinel-1B SAR",
    areaKm2: 12.5,
    estimatedVolume: "65 MT",
    confidence: 82,
    severity: "Medium",
    status: "Attributed",
    suspectVessel: "Eastern Navigator",
    attributionRank: 1
  }
];

export const candidateVessels = [
  {
    rank: 1,
    name: "MSC Ocean Star",
    imo: "9412345",
    mmsi: "211832000",
    flag: "Liberia",
    flagCode: "LR",
    type: "Crude Oil Tanker",
    dwt: 115000,
    builtYear: 2014,
    owner: "Mediterranean Shipping Corp",
    operator: "Ocean Star Shipping Ltd",
    confidence: 94,
    status: "Primary Suspect",
    riskCategory: "Critical",
    factors: {
      spatialTemporalScore: 98,
      spatialDistanceKm: 0.8,
      timeDeltaMinutes: 18,
      trajectoryMatch: 96,
      speedCourseAnomaly: 91,
      historicalComplianceRisk: 88,
      cargoHazardWeight: 95
    },
    aisEvent: "Speed dropped from 14.2 knots to 6.1 knots for 42 minutes with erratic 25° heading oscillations directly upstream of slick origin.",
    lastKnownPosition: {
      lat: 14.9542,
      lng: 88.4218,
      speedKnots: 13.8,
      heading: 108,
      destination: "Singapore",
      eta: "2026-08-30 18:00 UTC"
    }
  },
  {
    rank: 2,
    name: "Nordic Voyager",
    imo: "9387612",
    mmsi: "257129000",
    flag: "Norway",
    flagCode: "NO",
    type: "Chemical / Product Tanker",
    dwt: 49990,
    builtYear: 2018,
    owner: "Nordic Maritime Logistics",
    operator: "Oslo Tanker Management",
    confidence: 68,
    status: "Secondary Candidate",
    riskCategory: "Moderate",
    factors: {
      spatialTemporalScore: 74,
      spatialDistanceKm: 4.2,
      timeDeltaMinutes: 65,
      trajectoryMatch: 68,
      speedCourseAnomaly: 62,
      historicalComplianceRisk: 45,
      cargoHazardWeight: 80
    },
    aisEvent: "Maintained constant speed (12.4 kts) across corridor; passed 4.2 km west of discharge zone 65 minutes prior.",
    lastKnownPosition: {
      lat: 15.2105,
      lng: 88.7512,
      speedKnots: 12.4,
      heading: 95,
      destination: "Port Klang",
      eta: "2026-08-31 06:00 UTC"
    }
  },
  {
    rank: 3,
    name: "Pacific Titan",
    imo: "9654128",
    mmsi: "354982000",
    flag: "Panama",
    flagCode: "PA",
    type: "Bulk Carrier (Capesize)",
    dwt: 180000,
    builtYear: 2016,
    owner: "Pacific Bulk Holdings",
    operator: "Titan Shipping Management",
    confidence: 34,
    status: "Unlikely Candidate",
    riskCategory: "Low",
    factors: {
      spatialTemporalScore: 40,
      spatialDistanceKm: 11.5,
      timeDeltaMinutes: 140,
      trajectoryMatch: 35,
      speedCourseAnomaly: 20,
      historicalComplianceRisk: 30,
      cargoHazardWeight: 40
    },
    aisEvent: "Passed 11.5 km northeast on scheduled transit; no AIS gaps or course variations.",
    lastKnownPosition: {
      lat: 15.6540,
      lng: 89.1200,
      speedKnots: 11.2,
      heading: 120,
      destination: "Chittagong",
      eta: "2026-08-28 22:00 UTC"
    }
  },
  {
    rank: 4,
    name: "Golden Fortune",
    imo: "9218744",
    mmsi: "477123900",
    flag: "Hong Kong",
    flagCode: "HK",
    type: "Container Ship",
    dwt: 68000,
    builtYear: 2008,
    owner: "Fortune Lines HK",
    operator: "Global Express Carriers",
    confidence: 12,
    status: "Cleared",
    riskCategory: "Minimal",
    factors: {
      spatialTemporalScore: 15,
      spatialDistanceKm: 18.4,
      timeDeltaMinutes: 210,
      trajectoryMatch: 10,
      speedCourseAnomaly: 8,
      historicalComplianceRisk: 22,
      cargoHazardWeight: 25
    },
    aisEvent: "Transit occurred 3.5 hours before calculated spill onset; course downstream of plume drift.",
    lastKnownPosition: {
      lat: 14.1200,
      lng: 87.8900,
      speedKnots: 17.5,
      heading: 210,
      destination: "Colombo",
      eta: "2026-08-29 10:00 UTC"
    }
  }
];

export const vesselProfileMSC = {
  ...candidateVessels[0],
  callSign: "D5AB4",
  grossTonnage: "62,400 GT",
  lengthMeters: 244,
  beamMeters: 42,
  draughtMeters: 14.8,
  engineType: "MAN B&W 6S60MC-C (13,560 kW)",
  hullType: "Double Hull Oil Tanker",
  pAndIClub: "Gard P&I (Bermuda) Ltd",
  classificationSociety: "DNV GL",
  sanctionHistory: "None",
  priorViolations: [
    {
      date: "2023-11-14",
      port: "Rotterdam, Netherlands",
      deficiency: "MARPOL Annex I - Oily water separator sensor calibration overdue",
      action: "Rectified before departure"
    },
    {
      date: "2021-04-09",
      port: "Fujairah, UAE",
      deficiency: "Oil Record Book Part II incomplete log entry",
      action: "Warning issued by port state control"
    }
  ],
  currentVoyage: {
    originPort: "Ras Tanura, Saudi Arabia (Loaded 2026-08-18)",
    destinationPort: "Singapore Anchorage (ETA 2026-08-30)",
    cargoManifest: "Arabian Light Crude (104,200 MT)",
    fuelBunkers: "VLSFO (1,850 MT), MGO (220 MT)",
    totalDistanceNm: 3640,
    distanceRemainingNm: 890
  },
  aisTrajectory: [
    { time: "2026-08-26 21:00 UTC", lat: 14.6210, lng: 87.9120, speed: 14.2, heading: 108 },
    { time: "2026-08-26 22:00 UTC", lat: 14.7140, lng: 88.0850, speed: 14.0, heading: 108 },
    { time: "2026-08-26 22:45 UTC", lat: 14.7820, lng: 88.2140, speed: 9.4, heading: 115 }, // Speed reduction begins
    { time: "2026-08-26 23:15 UTC", lat: 14.8214, lng: 88.2915, speed: 6.1, heading: 133 }, // Discharge epicenter
    { time: "2026-08-26 23:55 UTC", lat: 14.8490, lng: 88.3420, speed: 7.8, heading: 122 },
    { time: "2026-08-27 00:30 UTC", lat: 14.8910, lng: 88.3980, speed: 13.5, heading: 108 }, // Resumed cruising speed
    { time: "2026-08-27 02:00 UTC", lat: 14.9542, lng: 88.4218, speed: 13.8, heading: 108 }
  ]
};

export const securityAlerts = [
  {
    id: "ALT-2026-441",
    incidentId: "INC-2026-001",
    timestamp: "2026-08-27 04:22 UTC",
    severity: "Critical",
    title: "High-Confidence Slick Attribution: MSC Ocean Star (94%)",
    description: "Spatial-temporal back-trajectory analysis overlaps with heavy bunker emulsion plume in Sector 4.",
    acknowledged: false,
    acknowledgedBy: null
  },
  {
    id: "ALT-2026-440",
    incidentId: "INC-2026-001",
    timestamp: "2026-08-27 04:15 UTC",
    severity: "Critical",
    title: "Satellite SAR Anomaly Detection — Bay of Bengal",
    description: "Sentinel-1A pass captured 46.8 km² slick polygon at 14°49'17\"N, 88°17'29\"E.",
    acknowledged: true,
    acknowledgedBy: "Lt. A. Sharma (04:18 UTC)"
  },
  {
    id: "ALT-2026-439",
    incidentId: "INC-2026-002",
    timestamp: "2026-08-26 19:45 UTC",
    severity: "High",
    title: "Potential Bilge Dump in Arabian Sea EEZ Boundary",
    description: "Synthetic aperture radar detected 18.2 km² plume along international shipping lane.",
    acknowledged: true,
    acknowledgedBy: "Duty Officer K. Nair (19:50 UTC)"
  },
  {
    id: "ALT-2026-438",
    incidentId: null,
    timestamp: "2026-08-26 15:10 UTC",
    severity: "Medium",
    title: "AIS Signal Gap Detected — Chemical Tanker Silver Fern",
    description: "Vessel went dark for 114 minutes inside Marine Protected Area off Andaman coast.",
    acknowledged: true,
    acknowledgedBy: "Automated System (15:10 UTC)"
  },
  {
    id: "ALT-2026-437",
    incidentId: null,
    timestamp: "2026-08-26 09:30 UTC",
    severity: "Info",
    title: "Scheduled SAR Satellite Constellation Pass Complete",
    description: "Sentinel-1B and RADARSAT-2 swaths ingested successfully into detection pipeline.",
    acknowledged: true,
    acknowledgedBy: "System Daemon (09:30 UTC)"
  }
];

export const geographicLayers = {
  incidentCenter: [14.8214, 88.2915],
  slickPolygonCoordinates: [
    [14.8850, 88.1920],
    [14.8980, 88.2450],
    [14.8620, 88.3580],
    [14.8120, 88.3980],
    [14.7750, 88.3450],
    [14.7920, 88.2410],
    [14.8350, 88.1850]
  ],
  eezBoundaryCoordinates: [
    [16.5000, 86.0000],
    [15.8000, 87.5000],
    [14.2000, 89.2000],
    [12.8000, 90.5000]
  ],
  shippingLaneCoordinates: [
    [14.5000, 86.5000],
    [14.7500, 88.0000],
    [14.8500, 88.5000],
    [15.1000, 90.0000]
  ]
};
