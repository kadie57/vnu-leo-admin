"""
VNU-LEO - Tinh so luong ve tinh toi thieu de phu song lien tuc Viet Nam

Logic chinh:
- Khong dat truoc so ve tinh.
- Thu lan luot cac cau hinh Walker constellation.
- Voi moi cau hinh, tinh vi tri tung ve tinh theo thoi gian.
- Kiem tra moi diem mat dat tren Viet Nam co nhin thay it nhat 1 ve tinh hay khong.
- Cau hinh dau tien co uncovered_count = 0 duoc xem la dat yeu cau.

Yeu cau Python:
    pip install numpy

Chay:
    python vnu_leo_min_satellite_calculator.py
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import List, Tuple, Dict, Any, Optional

import numpy as np

# ============================================================
# 1. THONG SO VAT LY
# ============================================================
R_EARTH_KM = 6371.0
MU_EARTH = 398600.4418          # km^3/s^2
OMEGA_EARTH = 7.2921159e-5     # rad/s
C_KM_S = 299792.458             # km/s

# ============================================================
# 2. THONG SO MO PHONG - CO THE CHINH SUA
# ============================================================
ALTITUDE_KM = 1200.0            # LEO cao de tang vung phu, giam so ve tinh
MIN_ELEV_DEG = 10.0             # goc ngang toi thieu; tang len 15 deg se chat hon
TIME_STEP_SEC = 60              # 60 giay la hop ly cho bai tap
SIMULATION_HOURS = 24           # kiem tra 24 gio

# Tim kiem so ve tinh
MIN_TOTAL_SATS = 4
MAX_TOTAL_SATS = 140

# Cac cau hinh Walker se duoc thu:
# P = so mat phang quy dao, S = so ve tinh/mat phang, N = P*S
MIN_PLANES = 4
MAX_PLANES = 14
MIN_SATS_PER_PLANE = 2
MAX_SATS_PER_PLANE = 20

# Goc nghieng phu hop Viet Nam nam trong khoang 8-23 do Bac.
# 45-60 do giup ve tinh di qua Viet Nam thuong xuyen hon so voi quy dao xich dao.
INCLINATION_CANDIDATES_DEG = [40, 45, 50, 53, 55, 60]

# Che do diem kiem tra:
# - "representative": nhanh, dung tap diem dai dien dat lien + dao/bien
# - "bbox_grid": bao thu lon, kha bao thu vi kiem tra ca hinh chu nhat bao quanh Viet Nam
TARGET_MODE = "representative"
GRID_STEP_DEG = 1.0

# Neu True, in ket qua tot nhat cho tung so luong ve tinh.
VERBOSE = True


# ============================================================
# 3. DU LIEU DIEM KIEM TRA
# ============================================================
# Tap diem dai dien cac vung: mien Bac, Trung, Nam, Tay Nguyen, bien/dao.
# Co the them diem tuy y de tang do chat cua bai toan.
REPRESENTATIVE_TARGETS_DEG = [
    # Mien Bac
    ("Ha Noi", 21.0285, 105.8542),
    ("Hai Phong", 20.8449, 106.6881),
    ("Quang Ninh", 21.0064, 107.2925),
    ("Lang Son", 21.8537, 106.7615),
    ("Lao Cai", 22.4809, 103.9755),
    ("Dien Bien", 21.3860, 103.0230),
    ("Son La", 21.3270, 103.9141),
    ("Thanh Hoa", 19.8067, 105.7852),

    # Mien Trung
    ("Nghe An", 18.6796, 105.6813),
    ("Ha Tinh", 18.3559, 105.8877),
    ("Quang Binh", 17.6103, 106.3487),
    ("Hue", 16.4637, 107.5909),
    ("Da Nang", 16.0471, 108.2068),
    ("Quang Nam", 15.5394, 108.0191),
    ("Quang Ngai", 15.1214, 108.8044),
    ("Binh Dinh", 13.7820, 109.2197),
    ("Phu Yen", 13.0882, 109.0929),
    ("Khanh Hoa", 12.2388, 109.1967),
    ("Ninh Thuan", 11.6739, 108.8620),
    ("Binh Thuan", 10.9333, 108.1000),

    # Tay Nguyen
    ("Kon Tum", 14.3497, 108.0005),
    ("Gia Lai", 13.9833, 108.0000),
    ("Dak Lak", 12.7100, 108.2378),
    ("Dak Nong", 12.2646, 107.6098),
    ("Lam Dong", 11.9404, 108.4583),

    # Mien Nam
    ("TP HCM", 10.8231, 106.6297),
    ("Dong Nai", 10.9574, 106.8427),
    ("Ba Ria Vung Tau", 10.4114, 107.1362),
    ("Can Tho", 10.0452, 105.7469),
    ("An Giang", 10.5216, 105.1259),
    ("Kien Giang", 10.0125, 105.0809),
    ("Ca Mau", 9.1768, 105.1524),

    # Dao / bien
    ("Phu Quoc", 10.2899, 103.9840),
    ("Con Dao", 8.6864, 106.6082),
    ("Ly Son", 15.3833, 109.1167),
    ("Bach Long Vi", 20.1333, 107.7167),
    ("Hoang Sa area", 16.5000, 112.0000),
    ("Truong Sa area", 8.6400, 111.9200),
]


@dataclass
class TargetPoint:
    name: str
    lat_deg: float
    lon_deg: float
    ecef_km: np.ndarray
    up_vec: np.ndarray


@dataclass
class ConstellationConfig:
    total_sats: int
    planes: int
    sats_per_plane: int
    altitude_km: float
    inclination_deg: float
    phasing: int


@dataclass
class CoverageResult:
    config: ConstellationConfig
    uncovered_count: int
    coverage_ratio: float
    min_point_coverage_ratio: float
    max_gap_sec: int
    worst_point_name: str
    avg_visible_sats: float
    max_visible_sats: int
    mean_one_way_delay_ms: Optional[float]
    max_one_way_delay_ms: Optional[float]
    first_uncovered_samples: List[Tuple[str, str]]


# ============================================================
# 4. HAM TOAN HOC CO BAN
# ============================================================
def deg2rad(x: float) -> float:
    return math.radians(x)


def ecef_from_latlon(lat_deg: float, lon_deg: float) -> np.ndarray:
    """Chuyen toa do lat/lon tren mat cau Trai Dat sang ECEF, don vi km."""
    lat = deg2rad(lat_deg)
    lon = deg2rad(lon_deg)
    x = R_EARTH_KM * math.cos(lat) * math.cos(lon)
    y = R_EARTH_KM * math.cos(lat) * math.sin(lon)
    z = R_EARTH_KM * math.sin(lat)
    return np.array([x, y, z], dtype=float)


def hms_from_seconds(sec: int) -> str:
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def max_consecutive_false_gap_seconds(covered: np.ndarray, step_sec: int) -> int:
    """Tinh khoang mat song dai nhat trong chuoi covered True/False."""
    max_run = 0
    cur = 0
    for v in covered:
        if not bool(v):
            cur += 1
            max_run = max(max_run, cur)
        else:
            cur = 0
    return max_run * step_sec


# ============================================================
# 5. TAO DIEM KIEM TRA
# ============================================================
def build_targets_representative() -> List[TargetPoint]:
    targets = []
    for name, lat, lon in REPRESENTATIVE_TARGETS_DEG:
        ecef = ecef_from_latlon(lat, lon)
        targets.append(TargetPoint(name=name, lat_deg=lat, lon_deg=lon,
                                   ecef_km=ecef, up_vec=ecef / R_EARTH_KM))
    return targets


def build_targets_bbox_grid(step_deg: float = 1.0) -> List[TargetPoint]:
    """
    Tao luoi diem bao thu theo hinh chu nhat bao quanh Viet Nam va mot phan bien.
    Cach nay bao thu hon nhung co the lam tang so ve tinh vi gom ca khu vuc ngoai Viet Nam.
    """
    targets = []
    lat_values = np.arange(7.0, 24.1, step_deg)
    lon_values = np.arange(102.0, 113.1, step_deg)
    for lat in lat_values:
        for lon in lon_values:
            name = f"grid_{lat:.1f}_{lon:.1f}"
            ecef = ecef_from_latlon(float(lat), float(lon))
            targets.append(TargetPoint(name=name, lat_deg=float(lat), lon_deg=float(lon),
                                       ecef_km=ecef, up_vec=ecef / R_EARTH_KM))

    # Them cac diem dao/bien quan trong de chac chan khong bi bo sot
    for name, lat, lon in [
        ("Phu Quoc", 10.2899, 103.9840),
        ("Con Dao", 8.6864, 106.6082),
        ("Hoang Sa area", 16.5000, 112.0000),
        ("Truong Sa area", 8.6400, 111.9200),
    ]:
        ecef = ecef_from_latlon(lat, lon)
        targets.append(TargetPoint(name=name, lat_deg=lat, lon_deg=lon,
                                   ecef_km=ecef, up_vec=ecef / R_EARTH_KM))
    return targets


def build_targets(mode: str) -> List[TargetPoint]:
    if mode == "representative":
        return build_targets_representative()
    if mode == "bbox_grid":
        return build_targets_bbox_grid(GRID_STEP_DEG)
    raise ValueError("TARGET_MODE phai la 'representative' hoac 'bbox_grid'")


# ============================================================
# 6. TAO CHOM VE TINH WALKER
# ============================================================
def generate_walker_orbits(config: ConstellationConfig) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Tra ve 3 mang radian: inclination, RAAN, true anomaly ban dau.
    Cau hinh Walker-Delta don gian:
        - RAAN chia deu theo so mat phang
        - Ve tinh trong moi mat phang chia deu theo anomaly
        - phasing lam lech pha giua cac mat phang
    """
    inc_list = []
    raan_list = []
    nu0_list = []

    P = config.planes
    S = config.sats_per_plane
    T = config.total_sats
    inc_rad = math.radians(config.inclination_deg)

    for p in range(P):
        raan = 2.0 * math.pi * p / P
        for s in range(S):
            nu0 = 2.0 * math.pi * s / S + 2.0 * math.pi * config.phasing * p / T
            inc_list.append(inc_rad)
            raan_list.append(raan)
            nu0_list.append(nu0 % (2.0 * math.pi))

    return np.array(inc_list), np.array(raan_list), np.array(nu0_list)


# ============================================================
# 7. TINH VI TRI VE TINH THEO THOI GIAN
# ============================================================
def satellite_positions_ecef(config: ConstellationConfig, times_sec: np.ndarray) -> np.ndarray:
    """
    Tinh vi tri tat ca ve tinh theo thoi gian.

    Output:
        sat_ecef: shape = [N_sat, N_time, 3], don vi km
    """
    r_sat = R_EARTH_KM + config.altitude_km
    mean_motion = math.sqrt(MU_EARTH / (r_sat ** 3))

    inc, raan, nu0 = generate_walker_orbits(config)

    theta = nu0[:, None] + mean_motion * times_sec[None, :]

    cos_raan = np.cos(raan)[:, None]
    sin_raan = np.sin(raan)[:, None]
    cos_inc = np.cos(inc)[:, None]
    sin_inc = np.sin(inc)[:, None]

    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)

    # Quy dao tron trong he ECI
    x_eci = r_sat * (cos_raan * cos_theta - sin_raan * cos_inc * sin_theta)
    y_eci = r_sat * (sin_raan * cos_theta + cos_raan * cos_inc * sin_theta)
    z_eci = r_sat * (sin_inc * sin_theta)

    # Chuyen ECI -> ECEF bang cach quay theo toc do tu quay Trai Dat
    theta_g = OMEGA_EARTH * times_sec
    cos_tg = np.cos(theta_g)[None, :]
    sin_tg = np.sin(theta_g)[None, :]

    x_ecef = x_eci * cos_tg + y_eci * sin_tg
    y_ecef = -x_eci * sin_tg + y_eci * cos_tg
    z_ecef = z_eci

    return np.stack([x_ecef, y_ecef, z_ecef], axis=2)


# ============================================================
# 8. DANH GIA PHU SONG
# ============================================================
def evaluate_coverage(config: ConstellationConfig,
                      targets: List[TargetPoint],
                      times_sec: np.ndarray,
                      min_elev_deg: float) -> CoverageResult:
    """
    Dieu kien dat:
        uncovered_count == 0
    Nghia la moi diem kiem tra, moi thoi diem deu co it nhat 1 ve tinh kha kien.
    """
    min_elev_sin = math.sin(math.radians(min_elev_deg))
    sat_ecef = satellite_positions_ecef(config, times_sec)

    n_targets = len(targets)
    n_times = len(times_sec)
    covered_matrix = np.zeros((n_targets, n_times), dtype=bool)
    visible_count_matrix = np.zeros((n_targets, n_times), dtype=np.int16)

    # Luu slant range cua ve tinh tot nhat de uoc tinh delay mot chieu
    best_range_matrix = np.full((n_targets, n_times), np.nan, dtype=float)

    for i, target in enumerate(targets):
        # vec shape = [N_sat, N_time, 3]
        vec = sat_ecef - target.ecef_km[None, None, :]
        dot = np.einsum("ntk,k->nt", vec, target.up_vec)
        slant_range = np.linalg.norm(vec, axis=2)
        sin_elev = dot / slant_range

        visible = sin_elev >= min_elev_sin
        visible_any = np.any(visible, axis=0)
        visible_count = np.sum(visible, axis=0)

        covered_matrix[i, :] = visible_any
        visible_count_matrix[i, :] = visible_count

        # Khoang cach tot nhat trong cac ve tinh dang thay duoc
        # Neu khong co ve tinh nao kha kien thi de nan
        masked_range = np.where(visible, slant_range, np.inf)
        best_range = np.min(masked_range, axis=0)
        best_range[~visible_any] = np.nan
        best_range_matrix[i, :] = best_range

    uncovered_count = int(np.size(covered_matrix) - np.sum(covered_matrix))
    coverage_ratio = float(np.mean(covered_matrix))

    point_coverage = np.mean(covered_matrix, axis=1)
    worst_idx = int(np.argmin(point_coverage))
    min_point_coverage_ratio = float(point_coverage[worst_idx])
    worst_point_name = targets[worst_idx].name

    max_gap_sec = 0
    first_uncovered_samples: List[Tuple[str, str]] = []

    for i, target in enumerate(targets):
        gap = max_consecutive_false_gap_seconds(covered_matrix[i, :], TIME_STEP_SEC)
        max_gap_sec = max(max_gap_sec, gap)

        if not np.all(covered_matrix[i, :]) and len(first_uncovered_samples) < 10:
            first_bad_idx = int(np.where(~covered_matrix[i, :])[0][0])
            first_uncovered_samples.append((target.name, hms_from_seconds(int(times_sec[first_bad_idx]))))

    avg_visible_sats = float(np.mean(visible_count_matrix))
    max_visible_sats = int(np.max(visible_count_matrix))

    if np.all(np.isnan(best_range_matrix)):
        mean_one_way_delay_ms = None
        max_one_way_delay_ms = None
    else:
        mean_range = float(np.nanmean(best_range_matrix))
        max_range = float(np.nanmax(best_range_matrix))
        mean_one_way_delay_ms = mean_range / C_KM_S * 1000.0
        max_one_way_delay_ms = max_range / C_KM_S * 1000.0

    return CoverageResult(
        config=config,
        uncovered_count=uncovered_count,
        coverage_ratio=coverage_ratio,
        min_point_coverage_ratio=min_point_coverage_ratio,
        max_gap_sec=max_gap_sec,
        worst_point_name=worst_point_name,
        avg_visible_sats=avg_visible_sats,
        max_visible_sats=max_visible_sats,
        mean_one_way_delay_ms=mean_one_way_delay_ms,
        max_one_way_delay_ms=max_one_way_delay_ms,
        first_uncovered_samples=first_uncovered_samples,
    )


# ============================================================
# 9. TIM SO VE TINH TOI THIEU
# ============================================================
def candidate_configs_for_total_sats(total_sats: int) -> List[ConstellationConfig]:
    configs = []
    for planes in range(MIN_PLANES, MAX_PLANES + 1):
        if total_sats % planes != 0:
            continue

        sats_per_plane = total_sats // planes
        if not (MIN_SATS_PER_PLANE <= sats_per_plane <= MAX_SATS_PER_PLANE):
            continue

        for inc in INCLINATION_CANDIDATES_DEG:
            # Phasing tu 0 den planes-1
            for phasing in range(planes):
                configs.append(ConstellationConfig(
                    total_sats=total_sats,
                    planes=planes,
                    sats_per_plane=sats_per_plane,
                    altitude_km=ALTITUDE_KM,
                    inclination_deg=float(inc),
                    phasing=phasing,
                ))
    return configs


def is_better_result(a: CoverageResult, b: Optional[CoverageResult]) -> bool:
    """True neu a tot hon b."""
    if b is None:
        return True

    # Uu tien it diem-thoi-diem bi mat phu song hon
    if a.uncovered_count != b.uncovered_count:
        return a.uncovered_count < b.uncovered_count

    # Sau do uu tien ty le phu cua diem xau nhat cao hon
    if abs(a.min_point_coverage_ratio - b.min_point_coverage_ratio) > 1e-12:
        return a.min_point_coverage_ratio > b.min_point_coverage_ratio

    # Sau do uu tien gap mat song lon nhat nho hon
    if a.max_gap_sec != b.max_gap_sec:
        return a.max_gap_sec < b.max_gap_sec

    # Cuoi cung uu tien nhieu ve tinh kha kien trung binh hon
    return a.avg_visible_sats > b.avg_visible_sats


def find_minimum_satellites() -> Optional[CoverageResult]:
    targets = build_targets(TARGET_MODE)
    times_sec = np.arange(0, SIMULATION_HOURS * 3600, TIME_STEP_SEC, dtype=float)

    print("=" * 72)
    print("VNU-LEO: TIM SO VE TINH TOI THIEU CHO PHU SONG LIEN TUC")
    print("=" * 72)
    print(f"Altitude              : {ALTITUDE_KM:.0f} km")
    print(f"Minimum elevation     : {MIN_ELEV_DEG:.1f} deg")
    print(f"Simulation time       : {SIMULATION_HOURS} h")
    print(f"Time step             : {TIME_STEP_SEC} s")
    print(f"Target mode           : {TARGET_MODE}")
    print(f"Number of targets     : {len(targets)}")
    print("Requirement           : moi target, moi thoi diem co >= 1 ve tinh kha kien")
    print("Pass condition         : uncovered_count == 0")
    print("=" * 72)

    global_best: Optional[CoverageResult] = None

    for total_sats in range(MIN_TOTAL_SATS, MAX_TOTAL_SATS + 1):
        configs = candidate_configs_for_total_sats(total_sats)
        if not configs:
            continue

        best_for_n: Optional[CoverageResult] = None

        for cfg in configs:
            result = evaluate_coverage(cfg, targets, times_sec, MIN_ELEV_DEG)
            if is_better_result(result, best_for_n):
                best_for_n = result

        assert best_for_n is not None
        if is_better_result(best_for_n, global_best):
            global_best = best_for_n

        if VERBOSE:
            cfg = best_for_n.config
            print(
                f"N={total_sats:3d} | best: "
                f"P={cfg.planes:2d}, S={cfg.sats_per_plane:2d}, "
                f"inc={cfg.inclination_deg:5.1f}, f={cfg.phasing:2d} | "
                f"coverage={best_for_n.coverage_ratio*100:8.4f}% | "
                f"min_point={best_for_n.min_point_coverage_ratio*100:8.4f}% | "
                f"uncovered={best_for_n.uncovered_count:6d} | "
                f"max_gap={best_for_n.max_gap_sec:5d}s | "
                f"worst={best_for_n.worst_point_name}"
            )

        if best_for_n.uncovered_count == 0:
            print_result(best_for_n)
            return best_for_n

    print("\nKHONG TIM THAY cau hinh dat yeu cau trong gioi han MAX_TOTAL_SATS.")
    if global_best is not None:
        print("\nCau hinh gan dat nhat:")
        print_result(global_best)
    return None


# ============================================================
# 10. IN KET QUA
# ============================================================
def print_result(result: CoverageResult) -> None:
    cfg = result.config
    print("\n" + "=" * 72)
    if result.uncovered_count == 0:
        print("DAT YEU CAU PHU SONG LIEN TUC 24/7")
    else:
        print("CHUA DAT YEU CAU, DAY LA CAU HINH TOT NHAT TIM DUOC")
    print("=" * 72)
    print(f"So ve tinh toi thieu / dang xet : {cfg.total_sats}")
    print(f"So mat phang quy dao           : {cfg.planes}")
    print(f"So ve tinh moi mat phang       : {cfg.sats_per_plane}")
    print(f"Do cao quy dao                 : {cfg.altitude_km:.1f} km")
    print(f"Goc nghieng quy dao            : {cfg.inclination_deg:.1f} deg")
    print(f"Walker phasing                 : {cfg.phasing}")
    print(f"Goc ngang toi thieu            : {MIN_ELEV_DEG:.1f} deg")
    print(f"Ty le phu song trung binh      : {result.coverage_ratio*100:.6f}%")
    print(f"Ty le phu diem xau nhat        : {result.min_point_coverage_ratio*100:.6f}%")
    print(f"So diem-thoi-diem mat phu      : {result.uncovered_count}")
    print(f"Khoang mat song dai nhat       : {result.max_gap_sec} s")
    print(f"Diem xau nhat                  : {result.worst_point_name}")
    print(f"So ve tinh kha kien trung binh : {result.avg_visible_sats:.3f}")
    print(f"So ve tinh kha kien lon nhat   : {result.max_visible_sats}")

    if result.mean_one_way_delay_ms is not None:
        print(f"Tre truyen song 1 chieu TB     : {result.mean_one_way_delay_ms:.3f} ms")
        print(f"Tre truyen song 1 chieu max    : {result.max_one_way_delay_ms:.3f} ms")
        print(f"RTT toi thieu gan dung         : {2*result.mean_one_way_delay_ms:.3f} ms")

    if result.first_uncovered_samples:
        print("\nMot so mau thoi diem mat phu song dau tien:")
        for name, hms in result.first_uncovered_samples:
            print(f"  - {name}: {hms}")

    print("=" * 72)


if __name__ == "__main__":
    find_minimum_satellites()
