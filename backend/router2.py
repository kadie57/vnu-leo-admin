import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.gridspec as gridspec
import itertools
from collections import deque

# ==========================================
# 1. THÔNG SỐ VẬT LÝ VÀ VIỄN THÔNG
# ==========================================
R_EARTH = 6371.0
ALTITUDE = 1200.0
R_SAT = R_EARTH + ALTITUDE
MU = 398600.4418
OMEGA_E = 7.2921159e-5
MEAN_MOTION = np.sqrt(MU / (R_SAT**3))

FREQ_GHZ = 12.0
FREQ_MHZ = FREQ_GHZ * 1000
MIN_ELEV = 15.0

# Khai báo 3 trạm Gateway (Tọa độ thực tế)
GATEWAYS = [
    {"name": "HÀ NỘI", "lat": 21.0285, "lon": 105.8542, "color": "cyan"},
    {"name": "ĐÀ NẴNG", "lat": 16.0470, "lon": 108.2062, "color": "lime"},
    {"name": "TP. HỒ CHÍ MINH", "lat": 10.8231, "lon": 106.6297, "color": "yellow"}
]

# Tính toán trước tọa độ ECEF gốc cho 3 trạm để tối ưu tốc độ
for gw in GATEWAYS:
    gw["lat_rad"] = np.radians(gw["lat"])
    gw["lon_rad"] = np.radians(gw["lon"])
    gw["X"] = R_EARTH * np.cos(gw["lat_rad"]) * np.cos(gw["lon_rad"])
    gw["Y"] = R_EARTH * np.cos(gw["lat_rad"]) * np.sin(gw["lon_rad"])
    gw["Z"] = R_EARTH * np.sin(gw["lat_rad"])

def calc_fspl(distance_km, freq_mhz):
    return 20 * np.log10(distance_km) + 20 * np.log10(freq_mhz) + 32.44

# ==========================================
# 2. DỮ LIỆU CHÙM SAO 82 VỆ TINH
# ==========================================
NUM_SATS = 82
SATS_INC = np.array([90.0, 15.0, 16.55, 18.62, 52.59, 55.55, 19.35, 86.93, 34.23, 34.46, 46.35, 22.58, 15.0, 60.72, 49.98, 34.92, 63.77, 90.0, 27.35, 86.2, 15.0, 61.44, 43.59, 49.82, 74.58, 60.1, 15.0, 19.22, 50.02, 15.0, 16.3, 33.26, 22.88, 51.85, 30.83, 15.0, 88.77, 20.12, 15.0, 19.4, 71.67, 77.93, 78.68, 25.18, 89.47, 19.23, 15.0, 87.11, 87.74, 42.2, 22.59, 15.0, 68.32, 71.79, 50.28, 46.0, 50.89, 36.34, 25.95, 90.0, 43.31, 86.36, 15.0, 38.08, 52.16, 90.0, 63.68, 28.11, 15.0, 32.51, 78.6, 34.71, 15.0, 53.92, 66.02, 21.31, 43.05, 31.6, 73.66, 88.94, 90.0, 36.81])
SATS_RAAN = np.array([360.0, 174.19, 339.3, 360.0, 185.8, 360.0, 97.94, 0.0, 142.43, 191.26, 85.61, 0.0, 4.73, 360.0, 119.31, 57.58, 0.0, 130.25, 125.76, 248.24, 82.73, 99.57, 24.05, 97.63, 293.26, 344.42, 351.57, 185.1, 12.2, 200.52, 4.33, 0.0, 271.99, 169.01, 153.18, 334.56, 21.54, 47.38, 113.78, 32.36, 335.77, 196.33, 3.29, 225.95, 360.0, 29.24, 164.72, 344.35, 0.75, 176.08, 199.96, 263.7, 123.78, 311.4, 0.0, 0.0, 0.0, 39.52, 24.1, 3.03, 0.0, 182.62, 93.09, 156.1, 251.84, 247.83, 134.1, 188.04, 232.12, 29.58, 0.0, 85.63, 3.69, 164.25, 321.76, 360.0, 323.66, 270.65, 2.69, 353.65, 350.48, 120.72])
SATS_NU = np.array([264.23, 355.04, 0.0, 0.0, 240.31, 1.13, 273.02, 0.0, 32.51, 76.62, 46.62, 208.33, 190.53, 332.48, 202.67, 194.38, 68.60, 223.53, 145.53, 91.32, 44.74, 212.77, 337.34, 240.62, 19.65, 46.78, 299.18, 332.89, 103.84, 246.12, 49.41, 196.27, 172.19, 14.93, 299.75, 191.39, 62.37, 249.87, 53.63, 279.84, 360.0, 341.43, 340.93, 0.0, 360.0, 28.97, 247.49, 212.18, 22.21, 283.79, 12.83, 71.4, 329.03, 170.37, 240.71, 360.0, 360.0, 8.7, 304.3, 0.0, 29.55, 304.87, 126.06, 258.86, 151.26, 3.69, 259.28, 126.77, 41.15, 104.72, 359.32, 0.0, 154.63, 44.87, 264.09, 112.78, 312.9, 205.32, 321.89, 94.97, 340.03, 28.89])

# ==========================================
# 3. KHỞI TẠO DASHBOARD ĐA ĐIỂM (MULTIPLE VIEWPORTS)
# ==========================================
plt.style.use('dark_background')
fig = plt.figure(figsize=(18, 9.5))
fig.canvas.manager.set_window_title('Trung tâm Điều hành Mạng Vệ tinh Quốc gia (National NOC)')
gs = gridspec.GridSpec(2, 3, height_ratios=[1.3, 1])

# Cửa sổ trượt bộ nhớ (90 phút)
DISPLAY_MINUTES = 90
FRAME_STEP = 20
MAX_FRAMES = int((DISPLAY_MINUTES * 60) / FRAME_STEP)

history_t = deque(maxlen=MAX_FRAMES)
history_cn = {gw["name"]: deque(maxlen=MAX_FRAMES) for gw in GATEWAYS}
history_fspl = {gw["name"]: deque(maxlen=MAX_FRAMES) for gw in GATEWAYS}

# --- KHỞI TẠO 3 RADAR ---
radars = []
for i, gw in enumerate(GATEWAYS):
    ax = fig.add_subplot(gs[0, i], projection='polar')
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_ylim(0, 90)
    ax.set_yticks([0, 30, 60, 75])
    ax.set_yticklabels(['90°', '60°', '30°', '15°'], color='gray', fontsize=8)
    ax.set_title(f"GATEWAY: {gw['name']}", fontsize=13, color=gw['color'], pad=15, fontweight='bold')
    
    dots, = ax.plot([], [], 'o', color='gray', markersize=2, alpha=0.5)
    marker, = ax.plot([], [], 'o', color=gw['color'], markersize=10, markeredgecolor='white')
    beam, = ax.plot([], [], '-', color=gw['color'], lw=3, alpha=0.7)
    
    radars.append({"ax": ax, "dots": dots, "marker": marker, "beam": beam})

# --- KHỞI TẠO CÁC ĐỒ THỊ CHUNG BÊN DƯỚI ---
ax_cn = fig.add_subplot(gs[1, 0])
ax_cn.set_ylim(0, 25)
ax_cn.set_title("So sánh Chất lượng Tín hiệu C/N", color='white')
ax_cn.set_ylabel("C/N (dB)")
ax_cn.grid(True, alpha=0.2)

ax_fspl = fig.add_subplot(gs[1, 1])
ax_fspl.set_ylim(160, 185)
ax_fspl.set_title("So sánh Suy hao Đường truyền (FSPL)", color='white')
ax_fspl.set_ylabel("FSPL (dB)")
ax_fspl.set_xlabel("Thời gian (Phút)")
ax_fspl.grid(True, alpha=0.2)

lines_cn = {}
lines_fspl = {}
for gw in GATEWAYS:
    lines_cn[gw["name"]], = ax_cn.plot([], [], color=gw["color"], lw=2, label=gw["name"])
    lines_fspl[gw["name"]], = ax_fspl.plot([], [], color=gw["color"], lw=2, label=gw["name"])
    
ax_cn.legend(loc='lower left', fontsize=9)
ax_fspl.legend(loc='lower left', fontsize=9)

# --- KHUNG VĂN BẢN (TEXT BOX) ---
ax_text = fig.add_subplot(gs[1, 2])
ax_text.axis('off') # Ẩn trục đi, chỉ dùng để hiển thị chữ
info_text = ax_text.text(0.05, 0.9, "", fontsize=11, color='white', family='monospace', verticalalignment='top')

# ==========================================
# 4. HÀM CẬP NHẬT TRUNG TÂM (CORE ENGINE)
# ==========================================
def update(frame):
    t = frame * FRAME_STEP
    theta_g = OMEGA_E * t
    current_time_min = t / 60.0
    history_t.append(current_time_min)
    
    # Tính tọa độ ECEF của toàn bộ 82 vệ tinh trước (Tiết kiệm CPU)
    sats_ecef = []
    for i in range(NUM_SATS):
        inc, raan, nu = np.radians(SATS_INC[i]), np.radians(SATS_RAAN[i]), np.radians(SATS_NU[i])
        theta = nu + MEAN_MOTION * t
        
        x_eci = R_SAT * (np.cos(raan)*np.cos(theta) - np.sin(raan)*np.cos(inc)*np.sin(theta))
        y_eci = R_SAT * (np.sin(raan)*np.cos(theta) + np.cos(raan)*np.cos(inc)*np.sin(theta))
        z_eci = R_SAT * (np.sin(inc)*np.sin(theta))
        
        x_ecef = x_eci * np.cos(theta_g) + y_eci * np.sin(theta_g)
        y_ecef = -x_eci * np.sin(theta_g) + y_eci * np.cos(theta_g)
        z_ecef = z_eci
        sats_ecef.append((x_ecef, y_ecef, z_ecef))

    # Xử lý riêng cho từng Gateway
    text_lines = [f"THỜI GIAN UPTIME: {int(t//3600):02d}h {int((t%3600)//60):02d}m {int(t%60):02d}s", "-"*45]
    
    for idx, gw in enumerate(GATEWAYS):
        gw_name = gw["name"]
        visible_az = []
        visible_r = []
        best_id, best_el, best_az, best_range = -1, -90, 0, 0
        
        for i, (x_ecef, y_ecef, z_ecef) in enumerate(sats_ecef):
            dx, dy, dz = x_ecef - gw["X"], y_ecef - gw["Y"], z_ecef - gw["Z"]
            
            E = -dx * np.sin(gw["lon_rad"]) + dy * np.cos(gw["lon_rad"])
            N = -dx * np.sin(gw["lat_rad"]) * np.cos(gw["lon_rad"]) - dy * np.sin(gw["lat_rad"]) * np.sin(gw["lon_rad"]) + dz * np.cos(gw["lat_rad"])
            U = dx * np.cos(gw["lat_rad"]) * np.cos(gw["lon_rad"]) + dy * np.cos(gw["lat_rad"]) * np.sin(gw["lon_rad"]) + dz * np.sin(gw["lat_rad"])
            
            s_range = np.sqrt(E**2 + N**2 + U**2)
            el = np.degrees(np.arcsin(U / s_range))
            az = np.degrees(np.arctan2(E, N)) % 360
            
            if el > 0:
                visible_az.append(np.radians(az))
                visible_r.append(90 - el)
                
            if el > best_el:
                best_el, best_az, best_range, best_id = el, az, s_range, i + 1

        # Tính chỉ số và cập nhật bộ nhớ
        if best_el >= MIN_ELEV:
            fspl = calc_fspl(best_range, FREQ_MHZ)
            cn = 185.0 - fspl
        else:
            fspl, cn, best_id = 0, 0, -1

        history_cn[gw_name].append(cn)
        history_fspl[gw_name].append(fspl if fspl > 0 else np.nan)

        # Cập nhật Radar UI
        radars[idx]["dots"].set_data(visible_az, visible_r)
        if best_id != -1:
            r_display = 90 - best_el
            radars[idx]["marker"].set_data([np.radians(best_az)], [r_display])
            radars[idx]["beam"].set_data([np.radians(best_az), np.radians(best_az)], [0, r_display])
            status = f"SAT-{best_id:02d} (El: {best_el:4.1f}° | CN: {cn:4.1f}dB)"
        else:
            radars[idx]["marker"].set_data([], [])
            radars[idx]["beam"].set_data([], [])
            status = "NO SIGNAL (HANDOVER DELAY)"
            
        # Thêm thông tin vào Bảng Text
        text_lines.append(f"[{gw_name}]")
        text_lines.append(f" > Sats in view : {len(visible_az)} vệ tinh")
        text_lines.append(f" > Tracking     : {status}")
        text_lines.append("")

        # Cập nhật Đồ thị Line
        lines_cn[gw_name].set_data(list(history_t), list(history_cn[gw_name]))
        lines_fspl[gw_name].set_data(list(history_t), list(history_fspl[gw_name]))

    # Cửa sổ cuộn (Sliding View X-Axis)
    min_t = history_t[0]
    max_t = max(current_time_min, min_t + 20) 
    ax_cn.set_xlim(min_t, max_t)
    ax_fspl.set_xlim(min_t, max_t)

    # In Box Text
    info_text.set_text("\n".join(text_lines))

    # Tạo danh sách các đối tượng vẽ cần trả về (cho Matplotlib blit dù đang tắt)
    artists = [radars[i]["dots"] for i in range(3)] + \
              [radars[i]["marker"] for i in range(3)] + \
              [radars[i]["beam"] for i in range(3)] + \
              list(lines_cn.values()) + list(lines_fspl.values()) + [info_text]
    return artists

# Chạy Animation vô hạn
ani = FuncAnimation(fig, update, frames=itertools.count(), interval=50, blit=False)
plt.tight_layout()
plt.show()
