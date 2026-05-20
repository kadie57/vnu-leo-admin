from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import math
import time

app = FastAPI()

# Cấu hình CORS cho phép SvelteKit kết nối công nghệ kết nối chéo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 1. CẤU HÌNH THÔNG SỐ QUỸ ĐẠO WALKER-DELTA (32 VỆ TINH)
# ==========================================
# Cấu hình tối ưu cho khu vực Việt Nam: 32 vệ tinh, 4 mặt phẳng, 8 vệ tinh/mặt phẳng
NUM_SATS = 32
PLANES = 4
SATS_PER_PLANE = 8
PHASING_F = 1
INCLINATION_DEG = 45.0  # Góc nghiêng quỹ đạo tối ưu để phủ sóng Việt Nam
ALTITUDE_KM = 1200.0    # Độ cao vệ tinh LEO

# Các hằng số vật lý thiên văn
R_EARTH = 6371.0                             # Bán kính Trái Đất (km)
R_SAT = R_EARTH + ALTITUDE_KM                # Khoảng cách từ tâm Trái Đất đến vệ tinh
MU_EARTH = 398600.4418                        # Hằng số hấp dẫn Trái Đất (km^3/s^2)
OMEGA_EARTH = 7.292115e-5                    # Vận tốc tự quay của Trái Đất (rad/s)
MEAN_MOTION = math.sqrt(MU_EARTH / (R_SAT**3)) # Vận tốc góc quỹ đạo của vệ tinh (rad/s)

# Tọa độ trạm mặt đất Gateway Hà Nội
HANOI_LAT = 21.0328
HANOI_LON = 105.8342

# ==========================================
# 2. KHỞI TẠO MA TRẬN QUỸ ĐẠO BAN ĐẦU CHO 32 VỆ TINH
# ==========================================
satellite_registry = []
sat_id_counter = 1

for p in range(PLANES):
    # Kinh độ điểm nút lên (RAAN) chia đều không gian 360 độ cho số mặt phẳng
    raan = p * (2 * math.pi / PLANES)
    for s in range(SATS_PER_PLANE):
        # Dị thường thực ban đầu (True Anomaly) tính theo Walker Phasing để đan xen nhau
        nu_0 = s * (2 * math.pi / SATS_PER_PLANE) + p * (2 * math.pi * PHASING_F / NUM_SATS)
        
        satellite_registry.append({
            "name": f"LEO-{sat_id_counter:02d}",
            "inc": math.radians(INCLINATION_DEG),
            "raan": raan,
            "nu_0": nu_0
        })
        sat_id_counter += 1

# ==========================================
# 3. THUẬT TOÁN CHUYỂN ĐỔI TỌA ĐỘ & TÍNH TOÁN VIỄN THÔNG
# ==========================================
def compute_satellite_state(sat, t_sim):
    """Tính toán vị trí (Lat, Lon) và các thông số hình học viễn thông"""
    # 1. Tính toán vị trí vệ tinh trong hệ ECI theo thời gian mô phỏng t_sim
    theta = sat["nu_0"] + MEAN_MOTION * t_sim
    inc = sat["inc"]
    raan = sat["raan"]
    
    x_eci = R_SAT * (math.cos(raan) * math.cos(theta) - math.sin(raan) * math.cos(inc) * math.sin(theta))
    y_eci = R_SAT * (math.sin(raan) * math.cos(theta) + math.cos(raan) * math.cos(inc) * math.sin(theta))
    z_eci = R_SAT * (math.sin(inc) * math.sin(theta))
    
    # 2. Xoay hệ tọa độ theo sự tự quay của Trái Đất (Chuyển từ ECI sang ECEF)
    theta_g = OMEGA_EARTH * t_sim
    x_ecef = x_eci * math.cos(theta_g) + y_eci * math.sin(theta_g)
    y_ecef = -x_eci * math.sin(theta_g) + y_eci * math.cos(theta_g)
    z_ecef = z_eci
    
    # Kinh độ và Vĩ độ của vệ tinh chiếu xuống mặt đất
    sat_lon = math.degrees(math.atan2(y_ecef, x_ecef))
    sat_lat = math.degrees(math.asin(max(-1.0, min(1.0, z_ecef / R_SAT))))
    
    # 3. Tính toán hình học đối với Gateway Hà Nội
    lat_g_rad = math.radians(HANOI_LAT)
    lon_g_rad = math.radians(HANOI_LON)
    
    # Tọa độ ECEF của trạm mặt đất Hà Nội
    x_g = R_EARTH * math.cos(lat_g_rad) * math.cos(lon_g_rad)
    y_g = R_EARTH * math.cos(lat_g_rad) * math.sin(lon_g_rad)
    z_g = R_EARTH * math.sin(lat_g_rad)
    
    # Vector khoảng cách từ trạm mặt đất tới vệ tinh
    dx, dy, dz = x_ecef - x_g, y_ecef - y_g, z_ecef - z_g
    distance_km = math.sqrt(dx**2 + dy**2 + dz**2)
    
    # Chuyển đổi sang hệ tọa độ chân trời địa phương (East-North-Up) tại Hà Nội để tính góc ngẩng
    up_x = math.cos(lat_g_rad) * math.cos(lon_g_rad)
    up_y = math.cos(lat_g_rad) * math.sin(lon_g_rad)
    up_z = math.sin(lat_g_rad)
    
    east_x, east_y, east_z = -math.sin(lon_g_rad), math.cos(lon_g_rad), 0
    
    north_x = -math.sin(lat_g_rad) * math.cos(lon_g_rad)
    north_y = -math.sin(lat_g_rad) * math.sin(lon_g_rad)
    north_z = math.cos(lat_g_rad)
    
    e = dx * east_x + dy * east_y + dz * east_z
    n = dx * north_x + dy * north_y + dz * north_z
    u = dx * up_x + dy * up_y + dz * up_z
    
    elevation_deg = math.degrees(math.asin(max(-1.0, min(1.0, u / distance_km))))
    azimuth_deg = math.degrees(math.atan2(e, n)) % 360
    
    # 4. ÁP DỤNG CÔNG THỨC VIỄN THÔNG
    if elevation_deg < 10.0:  # Nếu góc ngẩng nhỏ hơn 10 độ -> Ngoài vùng phủ sóng
        return {
            "id": sat["name"], "lat": round(sat_lat, 4), "lng": round(sat_lon, 4),
            "alt_km": ALTITUDE_KM, "elevation": round(elevation_deg, 1), "azimuth": round(azimuth_deg, 1),
            "distance": round(distance_km, 1), "status": "NO SIGNAL", "color": "#ef4444",
            "cn": 0, "fspl": 0, "delay": 0
        }
    
    # Tính độ trễ truyền dẫn ánh sáng (khoảng cách / 300,000 km/s)
    delay_ms = (distance_km / 300000.0) * 1000
    
    # Tính toán suy hao không gian tự do FSPL (Băng tần Ku: Tần số f = 12,000 MHz)
    fspl = 20 * math.log10(distance_km) + 20 * math.log10(12000) + 32.44
    
    # Tính tỷ số tín hiệu trên nhiễu C/N chân thực (Góc ngẩng càng cao -> Tín hiệu càng nét)
    cn = 14.0 + ((elevation_deg - 10) / 80.0) * 12.0
    
    return {
        "id": sat["name"], "lat": round(sat_lat, 4), "lng": round(sat_lon, 4),
        "alt_km": ALTITUDE_KM, "elevation": round(elevation_deg, 1), "azimuth": round(azimuth_deg, 1),
        "distance": round(distance_km, 1),
        "status": "ACTIVE" if elevation_deg >= 20 else "STANDBY",
        "color": "#10b981" if elevation_deg >= 20 else "#f59e0b",
        "cn": round(cn, 1), "fspl": round(fspl, 1), "delay": round(delay_ms, 1)
    }

# ==========================================
# 4. KÊNH STREAMING WEBSOCKET THỜI GIAN THỰC
# ==========================================
@app.websocket("/ws/vnu-leo")
async def vnu_leo_stream(websocket: WebSocket):
    await websocket.accept()
    print("SvelteKit Dashboard connected")
    
    t_sim = 0 # Khởi tạo thời gian mô phỏng ban đầu
    
    try:
        while True:
            payload = []
            for sat in satellite_registry:
                sat_state = compute_satellite_state(sat, t_sim)
                payload.append(sat_state)
            
            # Gửi toàn bộ mảng dữ liệu 32 vệ tinh về Frontend
            await websocket.send_json(payload)
            
            # Tăng tốc độ mô phỏng (Mỗi 1 giây thực tế = tiến lên 15 giây trong không gian để thấy rõ chuyển động)
            t_sim += 60
            
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        print("SvelteKit Dashboard disconnected")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "source": "walker-delta",
        "satellites": NUM_SATS,
        "planes": PLANES,
        "satsPerPlane": SATS_PER_PLANE,
        "inclinationDeg": INCLINATION_DEG,
        "altitudeKm": ALTITUDE_KM,
        "websocket": "/ws/vnu-leo",
    }


if __name__ == "__main__":
    # Cổng 8001 — tab Lớp 3 FE. Cổng 8000 dành cho be_final (tab Overview).
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)