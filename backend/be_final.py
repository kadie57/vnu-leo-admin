"""
Backend VNU-LEO: Walker constellation + WebSocket cho frontend.
Chạy: python backend/be_final.py
Yêu cầu: vnu_leo_min_satellite_calculator.py cùng thư mục backend/
"""
import asyncio
import sys
from pathlib import Path

import numpy as np
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Đảm bảo import được module calculator trong thư mục backend
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    import vnu_leo_min_satellite_calculator as calc
except ImportError as e:
    print(
        "Missing vnu_leo_min_satellite_calculator.py in backend/.\n"
        "Copy the calculator file next to be_final.py and retry."
    )
    raise e

# ==========================================
# 1. Cấu hình Walker từ thuật toán quy hoạch
# ==========================================
print("Running minimum satellite configuration search...")
best_coverage = calc.find_minimum_satellites()

if best_coverage is None:
    print("No suitable configuration found. Exiting.")
    sys.exit(1)

config = best_coverage.config
NUM_SATS = config.total_sats
SATS_INC_RAD, SATS_RAAN_RAD, SATS_NU_RAD = calc.generate_walker_orbits(config)

print(
    f"Config: {NUM_SATS} satellites "
    f"(P={config.planes}, S={config.sats_per_plane}, Inc={config.inclination_deg} deg)"
)

# ==========================================
# 2. Thông số vật lý & Gateway (đồng bộ FE)
# ==========================================
R_EARTH = calc.R_EARTH_KM
ALTITUDE = config.altitude_km
R_SAT = R_EARTH + ALTITUDE
MU = calc.MU_EARTH
OMEGA_E = calc.OMEGA_EARTH
MEAN_MOTION = np.sqrt(MU / (R_SAT**3))
MIN_ELEV = calc.MIN_ELEV_DEG

GATEWAYS = [
    {"name": "Hà Nội", "lat": 21.0285, "lon": 105.8542, "color": "#10b981"},
    {"name": "Đà Nẵng", "lat": 16.0421, "lon": 108.2068, "color": "#f59e0b"},
    {"name": "TP.HCM", "lat": 10.8231, "lon": 106.6297, "color": "#eb4f27"},
]

gw_status = {i: None for i in range(len(GATEWAYS))}
handover_flash = {i: 0 for i in range(len(GATEWAYS))}

HANOI_GW = GATEWAYS[0]
ORBIT_V_KMS = float(np.sqrt(MU / R_SAT))
ORBIT_PERIOD_MIN = float(2 * np.pi * np.sqrt(R_SAT**3 / MU) / 60)


def _sat_telemetry(lon: float, lat: float) -> dict:
    """Thông số RF/vị trí tới gateway Hà Nội, Đà Nẵng, TP.HCM."""
    # 1. Tính toán cho Gateway Hà Nội (GATEWAYS[0])
    dist_hn = float(np.sqrt((lon - GATEWAYS[0]["lon"]) ** 2 + (lat - GATEWAYS[0]["lat"]) ** 2))
    elev_hn = 90.0 - dist_hn * 5
    az_hn = float(np.degrees(np.arctan2(GATEWAYS[0]["lon"] - lon, GATEWAYS[0]["lat"] - lat))) % 360

    # 2. Tính toán cho Gateway Đà Nẵng (GATEWAYS[1])
    dist_dn = float(np.sqrt((lon - GATEWAYS[1]["lon"]) ** 2 + (lat - GATEWAYS[1]["lat"]) ** 2))
    elev_dn = 90.0 - dist_dn * 5
    az_dn = float(np.degrees(np.arctan2(GATEWAYS[1]["lon"] - lon, GATEWAYS[1]["lat"] - lat))) % 360

    # 3. Tính toán cho Gateway TP.HCM (GATEWAYS[2])
    dist_hcm = float(np.sqrt((lon - GATEWAYS[2]["lon"]) ** 2 + (lat - GATEWAYS[2]["lat"]) ** 2))
    elev_hcm = 90.0 - dist_hcm * 5
    az_hcm = float(np.degrees(np.arctan2(GATEWAYS[2]["lon"] - lon, GATEWAYS[2]["lat"] - lat))) % 360

    if elev_hn >= MIN_ELEV:
        cn = round(15.0 + ((elev_hn - MIN_ELEV) / 75.0) * 10.0, 1)
        delay_ms = round(15 + (90 - elev_hn) * 0.15)
        link = "Hoạt động tốt" if elev_hn >= 25 else "Trong vùng phủ"
    else:
        cn = 0.0
        delay_ms = 0
        link = "Ngoài vùng phủ"
        
    slant_km = max(R_SAT * np.sin(np.radians(max(elev_hn, 0.1))), R_EARTH)
    fspl = round(20 * np.log10(slant_km) + 20 * np.log10(12000) + 32.44, 1)
    
    return {
        "elevationHanoi": round(elev_hn, 1),
        "azimuthHanoi": round(az_hn, 1),
        "elevationDanang": round(elev_dn, 1),
        "azimuthDanang": round(az_dn, 1),
        "elevationHCM": round(elev_hcm, 1),
        "azimuthHCM": round(az_hcm, 1),
        "cn": cn,
        "delayMs": delay_ms,
        "fspl": fspl,
        "linkStatus": link,
    }

# ==========================================
# 3. FastAPI + WebSocket
# ==========================================
app = FastAPI(title="VNU-LEO Walker Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def simulation_loop(websocket: WebSocket):
    await websocket.accept()
    frame = 0
    prev_coords = {i: (0.0, 0.0) for i in range(NUM_SATS)}

    try:
        while True:
            t = frame * 30  # 30 giây mô phỏng mỗi frame (giống be_final gốc)
            theta_g = OMEGA_E * t

            sat_list = []
            sat_coords = []

            for i in range(NUM_SATS):
                inc = SATS_INC_RAD[i]
                raan = SATS_RAAN_RAD[i]
                nu = SATS_NU_RAD[i]
                theta = nu + MEAN_MOTION * t

                x_eci = R_SAT * (
                    np.cos(raan) * np.cos(theta)
                    - np.sin(raan) * np.cos(inc) * np.sin(theta)
                )
                y_eci = R_SAT * (
                    np.sin(raan) * np.cos(theta)
                    + np.cos(raan) * np.cos(inc) * np.sin(theta)
                )
                z_eci = R_SAT * (np.sin(inc) * np.sin(theta))

                x_ecef = x_eci * np.cos(theta_g) + y_eci * np.sin(theta_g)
                y_ecef = -x_eci * np.sin(theta_g) + y_eci * np.cos(theta_g)
                z_ecef = z_eci

                lon = float(np.degrees(np.arctan2(y_ecef, x_ecef)))
                lat = float(np.degrees(np.arcsin(z_ecef / R_SAT)))

                old_lon, old_lat = prev_coords[i]
                lon_dir = lon - old_lon
                lat_dir = lat - old_lat
                if frame == 0:
                    lon_dir, lat_dir = 0.0, 0.0

                prev_coords[i] = (lon, lat)
                sat_coords.append((lon, lat))

                telem = _sat_telemetry(lon, lat)
                sat_list.append({
                    "id": f"LEO-{i:02d}",
                    "lat": lat,
                    "lng": lon,
                    "latDir": lat_dir,
                    "lngDir": lon_dir,
                    "color": "#475569",
                    "altKm": ALTITUDE,
                    "velocityKms": round(ORBIT_V_KMS, 2),
                    "inclinationDeg": config.inclination_deg,
                    "periodMin": round(ORBIT_PERIOD_MIN, 1),
                    "band": "Ku-Band",
                    **telem,
                    "status": "OFFLINE",
                })

            gw_data = []
            connections = []
            in_view_sats = set()
            connected_sats = set()
            flash_sats = set()
            handover_count = 0
            connected_elevations = []

            for i, gw in enumerate(GATEWAYS):
                best_sat_id = None
                max_el = -90.0

                for s_id, (slon, slat) in enumerate(sat_coords):
                    dist = np.sqrt((slon - gw["lon"]) ** 2 + (slat - gw["lat"]) ** 2)
                    elevation = 90 - dist * 5
                    if elevation >= MIN_ELEV:
                        in_view_sats.add(s_id)
                    if elevation > max_el:
                        max_el = elevation
                        best_sat_id = s_id

                old_sat_id = gw_status[i]

                if max_el < MIN_ELEV:
                    gw_status[i] = None
                else:
                    if old_sat_id is None:
                        gw_status[i] = best_sat_id
                    elif old_sat_id != best_sat_id:
                        old_lon, old_lat = sat_coords[old_sat_id]
                        old_el = 90 - np.sqrt(
                            (old_lon - gw["lon"]) ** 2 + (old_lat - gw["lat"]) ** 2
                        ) * 5
                        if max_el > old_el + 4.0:
                            gw_status[i] = best_sat_id
                            handover_flash[i] = 4

                connected_id = gw_status[i]
                is_flash = False
                if handover_flash[i] > 0:
                    handover_flash[i] -= 1
                    is_flash = True

                if is_flash:
                    handover_count += 1
                if connected_id is not None:
                    connected_elevations.append(max_el)

                if connected_id is not None:
                    connected_sats.add(connected_id)
                    if is_flash:
                        flash_sats.add(connected_id)

                    final_color = "#f59e0b" if is_flash else "#10b981"

                    connections.append({
                        "gwLat": gw["lat"],
                        "gwLng": gw["lon"],
                        "satLat": sat_coords[connected_id][1],
                        "satLng": sat_coords[connected_id][0],
                        "color": final_color,
                        "isFlash": is_flash,
                    })

                cn_val = round((max_el / 90) * 30, 1) if connected_id is not None else 0

                gw_data.append({
                    "city": gw["name"],
                    "status": (
                        "STANDBY (HANDOVER)"
                        if is_flash
                        else ("ACTIVE" if connected_id is not None else "NO SIGNAL")
                    ),
                    "statusColor": (
                        "#f59e0b"
                        if is_flash
                        else ("#10b981" if connected_id is not None else "#ef4444")
                    ),
                    "titleColor": "#e2e8f0" if connected_id is None else "#10b981",
                    "tracking": (
                        f"LEO-{connected_id:02d}" if connected_id is not None else "—"
                    ),
                    "lat": f"{gw['lat']:.4f}° N",
                    "lng": f"{gw['lon']:.4f}° E",
                    "elevation": f"{max_el:.1f}°" if connected_id is not None else "—",
                    "cn": str(max(cn_val, 0)),
                    "linkStatus": (
                        "Chuyển giao"
                        if is_flash
                        else ("Tốt" if connected_id is not None else "Mất t/h")
                    ),
                    "session": "Có" if connected_id is not None else "Không",
                    "sessionColor": (
                        "#10b981" if connected_id is not None else "#ef4444"
                    ),
                    "imgSrc": "https://avajsc.com/hoanghung/30/images/2(9).jpg",
                })

            for s_id in range(NUM_SATS):
                if s_id in flash_sats:
                    sat_list[s_id]["color"] = "#f59e0b"
                    sat_list[s_id]["isActive"] = True
                    sat_list[s_id]["status"] = "HANDOVER"
                elif s_id in connected_sats:
                    sat_list[s_id]["color"] = "#10b981"
                    sat_list[s_id]["isActive"] = True
                    sat_list[s_id]["status"] = "ACTIVE"
                elif s_id in in_view_sats:
                    sat_list[s_id]["color"] = "#f59e0b"
                    sat_list[s_id]["isActive"] = True
                    sat_list[s_id]["status"] = "IN VIEW"
                else:
                    sat_list[s_id]["color"] = "#ef4444"
                    sat_list[s_id]["isActive"] = False
                    sat_list[s_id]["status"] = "OFFLINE"

            no_signal_count = sum(1 for gw in gw_data if gw["status"] == "NO SIGNAL")
            if no_signal_count >= 2:
                system_status = "Suy giảm"
                system_status_color = "#ef4444"
            elif handover_count > 0 or no_signal_count >= 1:
                system_status = "Cảnh báo handover"
                system_status_color = "#f59e0b"
            else:
                system_status = "Hoạt động bình thường"
                system_status_color = "#10b981"

            if connected_elevations:
                avg_el = sum(connected_elevations) / len(connected_elevations)
                avg_latency_ms = round(15 + (90 - avg_el) * 0.15)
            else:
                avg_latency_ms = 0

            await websocket.send_json({
                "time": t,
                "satellites": sat_list,
                "gateways": gw_data,
                "connections": connections,
                "overview": {
                    "totalSatellites": NUM_SATS,
                    "coveringVietnam": len(in_view_sats),
                    "upcomingHandover": handover_count,
                    "systemStatus": system_status,
                    "systemStatusColor": system_status_color,
                    "avgLatencyMs": avg_latency_ms,
                },
                "config": {
                    "planes": config.planes,
                    "satsPerPlane": config.sats_per_plane,
                    "inclinationDeg": config.inclination_deg,
                    "altitudeKm": config.altitude_km,
                },
            })

            frame += 1
            await asyncio.sleep(0.1)
    except Exception as e:
        print("Disconnected", e)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "satellites": NUM_SATS,
        "config": {
            "planes": config.planes,
            "satsPerPlane": config.sats_per_plane,
            "inclinationDeg": config.inclination_deg,
        },
    }


@app.websocket("/ws/vnu-leo")
async def websocket_endpoint(websocket: WebSocket):
    # Đây là nơi quan trọng: Gọi hàm mô phỏng khi có kết nối
    await simulation_loop(websocket)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
