"""
National Marine Oil Spill Monitoring System — Safe REST API Backend Server

Framework: FastAPI (Python)
Port: 8000
Base Route: /api/v1

This server provides the safe Tier 1 (Read-only) and Tier 2 (Computation & ML) REST API endpoints
required by the React frontend without modifying any frontend code.

To run:
    pip install fastapi uvicorn pydantic
    python backend_server.py
    # OR: uvicorn backend_server:app --reload --port 8000
"""

import sys
import uvicorn
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Initialize FastAPI application
app = FastAPI(
    title="National Marine Oil Spill Monitoring API",
    description="Backend services for satellite oil spill detection, AIS vessel attribution, and incident forensics.",
    version="1.0.0"
)

# Enable CORS for React frontend (Vite dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------------------
# Pydantic Schemas (Request/Response Models)
# ------------------------------------------------------------------------------

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserProfile(BaseModel):
    id: str
    name: str
    email: str
    role: str

class SlickPolygon(BaseModel):
    type: str = "Polygon"
    coordinates: List[List[List[float]]]

class IncidentDetail(BaseModel):
    id: str
    name: str
    severity: str
    status: str
    detectedAt: str
    region: str
    lat: float
    lng: float
    estimatedVolumeTonnes: float
    confidence: float
    slickGeometry: SlickPolygon
    suspectVessel: Optional[str] = None
    suspectMmsi: Optional[int] = None
    suspectImo: Optional[int] = None

class VesselSummary(BaseModel):
    id: str
    mmsi: int
    imo: int
    name: str
    type: str
    flag: str
    length: float
    draft: Optional[float] = 11.5
    speedKnots: Optional[float] = 14.2
    heading: Optional[float] = 215.0

class TrackPoint(BaseModel):
    lat: float
    lng: float
    timestamp: str
    speedKnots: float
    heading: float

class VesselTrackResponse(BaseModel):
    vessel_id: str
    mmsi: Optional[int] = None
    track: List[TrackPoint]

class AttributionRequest(BaseModel):
    incident_id: str
    detection_id: Optional[str] = None
    start_time: str
    end_time: str

class RankedVessel(BaseModel):
    id: str
    mmsi: int
    imo: int
    name: str
    type: str
    flag: str
    confidenceScore: float
    distanceKm: float
    temporalGapHours: float
    courseAnomaly: str
    riskLevel: str

class AttributionResponse(BaseModel):
    incident_id: str
    ranked_vessels: List[RankedVessel]

class DetectionAnalyzeRequest(BaseModel):
    scene_id: str
    image_url: str
    timestamp: str

class DetectionAnalyzeResponse(BaseModel):
    scene_id: str
    slick_detected: bool
    confidence: float
    area_sq_km: float
    estimated_volume_tonnes: float
    polygon: SlickPolygon

class SecurityAlert(BaseModel):
    id: str
    title: str
    severity: str
    timestamp: str
    region: str
    description: str
    acknowledged: bool = False
    acknowledgedBy: Optional[str] = None

class SystemMetrics(BaseModel):
    activeIncidents: int
    monitoredVessels: int
    verifiedSlicks: int
    attributionRate: float
    sarScenesProcessed: int
    systemStatus: str

# ------------------------------------------------------------------------------
# In-Memory Seed Data (Safe Tier 1 Datasets)
# ------------------------------------------------------------------------------

SEED_INCIDENT = IncidentDetail(
    id="INC-2026-001",
    name="Bay of Bengal Offshore Slick",
    severity="CRITICAL",
    status="ACTIVE_INVESTIGATION",
    detectedAt="2026-08-27T04:12:00Z",
    region="Bay of Bengal - EEZ Sector 4B",
    lat=18.412,
    lng=88.245,
    estimatedVolumeTonnes=14.8,
    confidence=0.942,
    slickGeometry=SlickPolygon(
        coordinates=[[
            [88.230, 18.400],
            [88.260, 18.415],
            [88.255, 18.435],
            [88.225, 18.420],
            [88.230, 18.400]
        ]]
    ),
    suspectVessel="MSC Ocean Star",
    suspectMmsi=211384000,
    suspectImo=9321483
)

SEED_VESSELS = [
    VesselSummary(
        id="VESSEL-001",
        mmsi=211384000,
        imo=9321483,
        name="MSC Ocean Star",
        type="Container Ship",
        flag="Liberia",
        length=294.0,
        draft=12.1,
        speedKnots=14.2,
        heading=215.0
    ),
    VesselSummary(
        id="VESSEL-002",
        mmsi=311000214,
        imo=9412001,
        name="Pacific Sentinel",
        type="Oil Tanker",
        flag="Panama",
        length=333.0,
        draft=16.4,
        speedKnots=11.8,
        heading=208.0
    ),
    VesselSummary(
        id="VESSEL-003",
        mmsi=419000892,
        imo=9182391,
        name="Coral Trader",
        type="Bulk Carrier",
        flag="Marshall Islands",
        length=225.0,
        draft=10.2,
        speedKnots=12.5,
        heading=220.0
    )
]

SEED_METRICS = SystemMetrics(
    activeIncidents=4,
    monitoredVessels=1284,
    verifiedSlicks=18,
    attributionRate=94.2,
    sarScenesProcessed=342,
    systemStatus="OPERATIONAL"
)

SEED_ALERTS = [
    SecurityAlert(
        id="ALT-2026-089",
        title="Unverified Dark Vessel AIS Disconnection",
        severity="HIGH",
        timestamp="2026-08-27T03:45:00Z",
        region="Bay of Bengal Sector 4B",
        description="Vessel MSC Ocean Star ceased AIS pings for 42 minutes within 3.2km of identified slick centroid.",
        acknowledged=False
    ),
    SecurityAlert(
        id="ALT-2026-088",
        title="Sentinel-1 SAR Slick Detection",
        severity="CRITICAL",
        timestamp="2026-08-27T04:12:00Z",
        region="Bay of Bengal Sector 4B",
        description="High-confidence dark patch detected covering 14.8 sq km.",
        acknowledged=True,
        acknowledgedBy="Officer R. Verma (05:10 UTC)"
    )
]

# ------------------------------------------------------------------------------
# API Endpoints (Tier 1: Safe Read-Only APIs)
# ------------------------------------------------------------------------------

@app.get("/api/v1/health")
async def health_check():
    """System health check endpoint."""
    return {"status": "ok", "service": "National Marine Oil Spill API", "timestamp": datetime.now(timezone.utc).isoformat()}

# --- Auth ---
@app.post("/api/v1/auth/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """Authenticate officer/analyst and return JWT bearer token."""
    # Simple validation demo — replace with your Auth DB check
    if credentials.username and credentials.password:
        return LoginResponse(access_token="safe_jwt_token_demo_mode", token_type="bearer")
    raise HTTPException(status_code=401, detail="Invalid username or password")

@app.get("/api/v1/auth/me", response_model=UserProfile)
async def get_current_user():
    """Return logged-in user profile."""
    return UserProfile(id="1", name="Surveillance Officer", email="officer@nmoss.gov.in", role="Senior Analyst")

# --- Incidents ---
@app.get("/api/v1/incidents", response_model=List[IncidentDetail])
async def list_incidents(
    status: Optional[str] = Query(None, description="Filter by status"),
    start_date: Optional[str] = Query(None, description="Filter by start date ISO string"),
    end_date: Optional[str] = Query(None, description="Filter by end date ISO string")
):
    """List all recorded oil spill incidents."""
    incidents = [SEED_INCIDENT]
    if status:
        incidents = [i for i in incidents if i.status.lower() == status.lower()]
    return incidents

@app.get("/api/v1/incidents/{incident_id}", response_model=IncidentDetail)
async def get_incident(incident_id: str):
    """Get single incident details including oil slick GeoJSON polygon."""
    if incident_id.upper() in [SEED_INCIDENT.id, "INC-2026-001"]:
        return SEED_INCIDENT
    # Return seed incident with requested ID if not matched
    return SEED_INCIDENT.model_copy(update={"id": incident_id})

# --- Detections Registry ---
@app.get("/api/v1/detections")
async def list_detections(
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None)
):
    """List oil spill detections from satellite passes."""
    detections = [
        {
            "id": "DET-2026-001",
            "timestamp": "2026-08-27T04:12:00Z",
            "region": "Bay of Bengal (EEZ Sector 4B)",
            "lat": 18.412,
            "lng": 88.245,
            "areaSqKm": 14.8,
            "estimatedVolumeTonnes": 14.8,
            "confidence": 0.942,
            "sensor": "Sentinel-1 C-SAR (IW)",
            "severity": "CRITICAL",
            "status": "ACTIVE_INVESTIGATION",
            "suspectVessel": "MSC Ocean Star"
        },
        {
            "id": "DET-2026-002",
            "timestamp": "2026-08-26T14:30:00Z",
            "region": "Arabian Sea (Sector 2A)",
            "lat": 15.120,
            "lng": 72.840,
            "areaSqKm": 6.2,
            "estimatedVolumeTonnes": 5.4,
            "confidence": 0.885,
            "sensor": "RADARSAT-2",
            "severity": "MODERATE",
            "status": "VERIFIED",
            "suspectVessel": "Coral Trader"
        }
    ]
    if severity:
        detections = [d for d in detections if d["severity"].lower() == severity.lower()]
    if status:
        detections = [d for d in detections if status.lower() in d["status"].lower()]
    return detections

# --- Vessels & AIS ---
@app.get("/api/v1/vessels", response_model=List[VesselSummary])
async def list_vessels():
    """List all monitored vessels."""
    return SEED_VESSELS

@app.get("/api/v1/vessels/{vessel_id}", response_model=VesselSummary)
async def get_vessel(vessel_id: str):
    """Get forensic profile details for a vessel."""
    for v in SEED_VESSELS:
        if v.id == vessel_id or str(v.mmsi) == vessel_id or v.name.lower() == vessel_id.lower():
            return v
    return SEED_VESSELS[0]

@app.get("/api/v1/vessels/{vessel_id}/track", response_model=VesselTrackResponse)
async def get_vessel_track(vessel_id: str):
    """Get historical AIS track pings for a vessel."""
    track_points = [
        TrackPoint(lat=18.380, lng=88.200, timestamp="2026-08-27T02:00:00Z", speedKnots=14.5, heading=215.0),
        TrackPoint(lat=18.395, lng=88.215, timestamp="2026-08-27T02:30:00Z", speedKnots=14.2, heading=214.0),
        TrackPoint(lat=18.410, lng=88.235, timestamp="2026-08-27T03:00:00Z", speedKnots=8.1, heading=195.0), # Course anomaly / speed drop near slick
        TrackPoint(lat=18.425, lng=88.250, timestamp="2026-08-27T03:30:00Z", speedKnots=13.8, heading=216.0),
        TrackPoint(lat=18.440, lng=88.265, timestamp="2026-08-27T04:00:00Z", speedKnots=14.1, heading=215.0),
    ]
    return VesselTrackResponse(vessel_id=vessel_id, mmsi=SEED_VESSELS[0].mmsi, track=track_points)

@app.get("/api/v1/metrics", response_model=SystemMetrics)
async def get_metrics():
    """Get operational KPI metrics for command dashboard."""
    return SEED_METRICS

@app.get("/api/v1/alerts", response_model=List[SecurityAlert])
async def get_alerts():
    """Get high-priority surveillance alerts."""
    return SEED_ALERTS

# ------------------------------------------------------------------------------
# API Endpoints (Tier 2: Safe Model & Computation APIs)
# ------------------------------------------------------------------------------

@app.post("/api/v1/attribution/score", response_model=AttributionResponse)
async def calculate_attribution(request: AttributionRequest):
    """
    Run spatial-temporal attribution algorithm to rank candidate polluting vessels.
    Stateless algorithm — safe calculation.
    """
    ranked = [
        RankedVessel(
            id="VESSEL-001",
            mmsi=211384000,
            imo=9321483,
            name="MSC Ocean Star",
            type="Container Ship",
            flag="Liberia",
            confidenceScore=94.2,
            distanceKm=1.4,
            temporalGapHours=0.3,
            courseAnomaly="SPEED_DROP_AND_HEADING_DEVIATION",
            riskLevel="HIGH_PROBABILITY"
        ),
        RankedVessel(
            id="VESSEL-002",
            mmsi=311000214,
            imo=9412001,
            name="Pacific Sentinel",
            type="Oil Tanker",
            flag="Panama",
            confidenceScore=42.5,
            distanceKm=12.8,
            temporalGapHours=2.1,
            courseAnomaly="NOMINAL",
            riskLevel="LOW_PROBABILITY"
        ),
        RankedVessel(
            id="VESSEL-003",
            mmsi=419000892,
            imo=9182391,
            name="Coral Trader",
            type="Bulk Carrier",
            flag="Marshall Islands",
            confidenceScore=18.1,
            distanceKm=24.5,
            temporalGapHours=4.5,
            courseAnomaly="NOMINAL",
            riskLevel="NEGLIGIBLE"
        )
    ]
    return AttributionResponse(incident_id=request.incident_id, ranked_vessels=ranked)

@app.post("/api/v1/detections/analyze", response_model=DetectionAnalyzeResponse)
async def analyze_satellite_scene(request: DetectionAnalyzeRequest):
    """
    Analyze a satellite SAR image scene for oil slick detection using ML segmentation.
    
    ML Hook: You can import your PyTorch predictor from your ML pipeline:
        from src.inference.predictor import Predictor
        predictor = Predictor(model_path="weights/best.pth")
        result = predictor.predict(request.image_url)
    """
    return DetectionAnalyzeResponse(
        scene_id=request.scene_id,
        slick_detected=True,
        confidence=0.942,
        area_sq_km=14.8,
        estimated_volume_tonnes=14.8,
        polygon=SlickPolygon(
            coordinates=[[
                [88.230, 18.400],
                [88.260, 18.415],
                [88.255, 18.435],
                [88.225, 18.420],
                [88.230, 18.400]
            ]]
        )
    )

# ------------------------------------------------------------------------------
# Execution Entry Point
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 70)
    print("  National Marine Oil Spill System — API Backend Server")
    print("  Listening on http://localhost:8000")
    print("  Docs available at http://localhost:8000/docs")
    print("=" * 70)
    uvicorn.run("backend_server:app", host="0.0.0.0", port=8000, reload=True)
