import asyncio
import numpy as np
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants & Data from handover.py
R_EARTH = 6371.0
ALTITUDE = 1200.0
R_SAT = R_EARTH + ALTITUDE
MU = 398600.4418
OMEGA_E = 7.2921159e-5
MEAN_MOTION = np.sqrt(MU / (R_SAT**3))
MIN_ELEV = 15.0

GATEWAYS = [
    {"name": "Hà Nội", "lat": 21.0328, "lon": 105.8342, "color": "#10b981"},  # Xanh lục
    {"name": "Đà Nẵng", "lat": 16.0544, "lon": 108.2022, "color": "#f59e0b"}, # Vàng cam
    {"name": "TP.HCM", "lat": 10.8231, "lon": 106.6297, "color": "#eb4f27"}   # Đỏ
]

NUM_SATS = 82

SATS_INC = np.array([
    90.00, 15.00, 16.55, 18.62, 52.59, 55.55, 19.35, 86.93, 34.23, 34.46, 
    46.35, 22.58, 15.00, 60.72, 49.98, 34.92, 63.77, 90.00, 27.35, 86.20, 
    15.00, 61.44, 43.59, 49.82, 74.58, 60.10, 15.00, 19.22, 50.02, 15.00, 
    16.30, 33.26, 22.88, 51.85, 30.83, 15.00, 88.77, 20.12, 15.00, 19.40, 
    71.67, 77.93, 78.68, 25.18, 89.47, 19.23, 15.00, 87.11, 87.74, 42.20, 
    22.59, 15.00, 68.32, 71.79, 50.28, 46.00, 50.89, 36.34, 25.95, 90.00, 
    43.31, 86.36, 15.00, 38.08, 52.16, 90.00, 63.68, 28.11, 15.00, 32.51, 
    78.60, 34.71, 15.00, 53.92, 66.02, 21.31, 43.05, 31.60, 73.66, 88.94, 
    90.00, 36.81
])

SATS_RAAN = np.array([
    360.00, 174.19, 339.30, 360.00, 185.80, 360.00,  97.94,   0.00, 142.43, 191.26, 
     85.61,   0.00,   4.73, 360.00, 119.31,  57.58,   0.00, 130.25, 125.76, 248.24, 
     82.73,  99.57,  24.05,  97.63, 293.26, 344.42, 351.57, 185.10,  12.20, 200.52, 
      4.33,   0.00, 271.99, 169.01, 153.18, 334.56,  21.54,  47.38, 113.78,  32.36, 
    335.77, 196.33,   3.29, 225.95, 360.00,  29.24, 164.72, 344.35,   0.75, 176.08, 
    199.96, 263.70, 123.78, 311.40,   0.00,   0.00,   0.00,  39.52,  24.10,   3.03, 
      0.00, 182.62,  93.09, 156.10, 251.84, 247.83, 134.10, 188.04, 232.12,  29.58, 
      0.00,  85.63,   3.69, 164.25, 321.76, 360.00, 323.66, 270.65,   2.69, 353.65, 
    350.48, 120.72
])

SATS_NU = np.array([
    264.23, 355.04,   0.00,   0.00, 240.31,   1.13, 273.02,   0.00,  32.51,  76.62, 
     46.62, 208.33, 190.53, 332.48, 202.67, 194.38,  68.60, 223.53, 145.53,  91.32, 
     44.74, 212.77, 337.34, 240.62,  19.65,  46.78, 299.18, 332.89, 103.84, 246.12, 
     49.41, 196.27, 172.19,  14.93, 299.75, 191.39,  62.37, 249.87,  53.63, 279.84, 
    360.00, 341.43, 340.93,   0.00, 360.00,  28.97, 247.49, 212.18,  22.21, 283.79, 
     12.83,  71.40, 329.03, 170.37, 240.71, 360.00, 360.00,   8.70, 304.30,   0.00, 
     29.55, 304.87, 126.06, 258.86, 151.26,   3.69, 259.28, 126.77,  41.15, 104.72, 
    359.32,   0.00, 154.63,  44.87, 264.09, 112.78, 312.90, 205.32, 321.89,  94.97, 
    340.03,  28.89
])

gw_status = {i: None for i in range(len(GATEWAYS))}
handover_flash = {i: 0 for i in range(len(GATEWAYS))}

async def simulation_loop(websocket: WebSocket):
    await websocket.accept()
    frame = 0
    prev_coords = {i: (0, 0) for i in range(NUM_SATS)}
    
    try:
        while True:
            t = frame * 15 # Tăng tốc thời gian để nhận ra sự di chuyển nhanh chóng
            theta_g = OMEGA_E * t
            
            sat_list = []
            sat_coords = []
            
            for i in range(NUM_SATS):
                inc, raan, nu = np.radians(SATS_INC[i]), np.radians(SATS_RAAN[i]), np.radians(SATS_NU[i])
                theta = nu + MEAN_MOTION * t
                
                x_eci = R_SAT * (np.cos(raan)*np.cos(theta) - np.sin(raan)*np.cos(inc)*np.sin(theta))
                y_eci = R_SAT * (np.sin(raan)*np.cos(theta) + np.cos(raan)*np.cos(inc)*np.sin(theta))
                z_eci = R_SAT * (np.sin(inc)*np.sin(theta))
                
                x_ecef = x_eci * np.cos(theta_g) + y_eci * np.sin(theta_g)
                y_ecef = -x_eci * np.sin(theta_g) + y_eci * np.cos(theta_g)
                z_ecef = z_eci
                
                lon = float(np.degrees(np.arctan2(y_ecef, x_ecef)))
                lat = float(np.degrees(np.arcsin(z_ecef / R_SAT)))
                
                # Tính hướng di chuyển
                old_lon, old_lat = prev_coords[i]
                lon_dir = lon - old_lon
                lat_dir = lat - old_lat
                if frame == 0:
                    lon_dir, lat_dir = 0, 0
                
                prev_coords[i] = (lon, lat)
                sat_coords.append((lon, lat))
                
                sat_list.append({
                    "id": f"LEO-{i:02d}",
                    "lat": lat,
                    "lng": lon,
                    "latDir": lat_dir,
                    "lngDir": lon_dir,
                    "color": "#475569" # Màu mặc định cho vệ tinh không làm việc
                })

            gw_data = []
            connections = []
            in_view_sats = set()
            connected_sats = set()
            flash_sats = set()
            
            for i, gw in enumerate(GATEWAYS):
                best_sat_id = None
                max_el = -90
                
                for s_id, (slon, slat) in enumerate(sat_coords):
                    # Tính toán khoảng cách đơn giản
                    dist = np.sqrt((slon - gw["lon"])**2 + (slat - gw["lat"])**2)
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
                        old_el = 90 - np.sqrt((old_lon - gw["lon"])**2 + (old_lat - gw["lat"])**2) * 5
                        if max_el > old_el + 4.0: 
                            gw_status[i] = best_sat_id
                            handover_flash[i] = 10 # Flash color for 10 frames
                
                connected_id = gw_status[i]
                is_flash = False
                if handover_flash[i] > 0:
                    handover_flash[i] -= 1
                    is_flash = True
                
                # Gán màu và link nếu có kết nối
                if connected_id is not None:
                    connected_sats.add(connected_id)
                    if is_flash:
                        flash_sats.add(connected_id)
                    
                    final_color = "#f59e0b" if is_flash else "#10b981" # Vàng nếu đang chuyển giao, Xanh nếu ổn định
                    
                    connections.append({
                        "gwLat": gw["lat"],
                        "gwLng": gw["lon"],
                        "satLat": sat_coords[connected_id][1],
                        "satLng": sat_coords[connected_id][0],
                        "color": final_color,
                        "isFlash": is_flash
                    })

                cn_val = round((max_el / 90) * 30, 1) if connected_id is not None else 0
                
                gw_data.append({
                    "city": gw["name"].replace("Gateway ", ""),
                    "status": "STANDBY (HANDOVER)" if is_flash else ("ACTIVE" if connected_id is not None else "NO SIGNAL"),
                    "statusColor": "#f59e0b" if is_flash else ("#10b981" if connected_id is not None else "#ef4444"),
                    "titleColor": "#e2e8f0" if connected_id is None else "#10b981",
                    "tracking": f"LEO-{connected_id:02d}" if connected_id is not None else "—",
                    "lat": f"{gw['lat']:.4f}° N",
                    "lng": f"{gw['lon']:.4f}° E",
                    "elevation": f"{max_el:.1f}°" if connected_id is not None else "—",
                    "cn": str(max(cn_val, 0)),
                    "linkStatus": "Chuyển giao" if is_flash else ("Tốt" if connected_id is not None else "Mất t/h"),
                    "session": "Có" if connected_id is not None else "Không",
                    "sessionColor": "#10b981" if connected_id is not None else "#ef4444",
                    "imgSrc": "https://avajsc.com/hoanghung/30/images/2(9).jpg"
                })

            # Cập nhật màu sắc cho các vệ tinh dựa trên trạng thái chung
            for s_id in range(NUM_SATS):
                if s_id in flash_sats:
                    sat_list[s_id]["color"] = "#f59e0b" # Vàng: Đang chuyển giao (Handover)
                    sat_list[s_id]["isActive"] = True
                elif s_id in connected_sats:
                    sat_list[s_id]["color"] = "#10b981" # Xanh lục: Đang kết nối phân phát mạng (Active)
                    sat_list[s_id]["isActive"] = True
                elif s_id in in_view_sats:
                    sat_list[s_id]["color"] = "#f59e0b" # Vàng: Trạng thái chờ rảnh rỗi trong vùng phủ sóng (Standby)
                    sat_list[s_id]["isActive"] = True
                else:
                    sat_list[s_id]["color"] = "#ef4444" # Đỏ: Mất tín hiệu do bay ra ngoài đại dương / ngoài vùng (No Signal)
                    sat_list[s_id]["isActive"] = False

            await websocket.send_json({
                "time": t,
                "satellites": sat_list,
                "gateways": gw_data,
                "connections": connections
            })
            
            frame += 1
            await asyncio.sleep(0.1)
    except Exception as e:
        print("Disconnected", e)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await simulation_loop(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
