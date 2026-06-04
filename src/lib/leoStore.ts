import { derived, writable } from 'svelte/store';
import { browser } from '$app/environment';
import { satelliteData } from './store';

/** Dữ liệu từ backend/be_final.py — mô phỏng Walker-Delta 32 vệ tinh (đã đồng bộ map) */
export interface LeoSatellite {
    id: string;
    lat: number;
    lng: number;
    alt_km: number;
    elevation: number;
    azimuth: number;
    elevation_danang: number;
    azimuth_danang: number;
    elevation_hcm: number;
    azimuth_hcm: number;
    distance: number;
    status: 'ACTIVE' | 'STANDBY' | 'NO SIGNAL';
    color: string;
    cn: number;
    delay: number;
    fspl: number;
    linkStatus: string;
    
    cn_danang: number;
    delay_danang: number;
    fspl_danang: number;
    linkStatus_danang: string;
    
    cn_hcm: number;
    delay_hcm: number;
    fspl_hcm: number;
    linkStatus_hcm: string;

    velocityKms: number;
    inclinationDeg: number;
    periodMin: number;
    raan: number;
    trueAnomaly: number;
    band: string;
    linkStatus: string;
}

export const selectedLeoId = writable<string | null>(null);

export const leoDetailData = derived(satelliteData, ($data) => {
    return $data.satellites.map(s => {
        // Tái tạo lại khoảng cách xấp xỉ từ elevation
        const dist = s.fspl ? Math.round(Math.pow(10, (s.fspl - 32.44 - 20 * Math.log10(12000)) / 20)) : 10666;
        
     return {
            id: s.id,
            lat: Number(s.lat.toFixed(4)),
            lng: Number(s.lng.toFixed(4)),
            alt_km: s.altKm ?? 1200,
            elevation: s.elevationHanoi ?? 0,
            azimuth: s.azimuthHanoi ?? 0,
            elevation_danang: s.elevationDanang ?? 0,
            azimuth_danang: s.azimuthDanang ?? 0,
            elevation_hcm: s.elevationHCM ?? 0,
            azimuth_hcm: s.azimuthHCM ?? 0,
            distance: dist,
            status: (s.elevationHanoi && s.elevationHanoi > 10) ? (s.elevationHanoi >= 20 ? 'ACTIVE' : 'STANDBY') : 'NO SIGNAL',
            color: (s.elevationHanoi && s.elevationHanoi > 10) ? (s.elevationHanoi >= 20 ? '#10b981' : '#f59e0b') : '#ef4444',
            
            cn: s.cn_hanoi ?? 0,
            delay: s.delay_hanoi_ms ?? 0,
            fspl: s.fspl_hanoi ?? 0,
            linkStatus: s.linkStatusHanoi ?? 'NO SIGNAL',

            cn_danang: s.cn_danang ?? 0,
            delay_danang: s.delay_danang_ms ?? 0,
            fspl_danang: s.fspl_danang ?? 0,
            linkStatus_danang: s.linkStatusDanang ?? 'NO SIGNAL',

            cn_hcm: s.cn_hcm ?? 0,
            delay_hcm: s.delay_hcm_ms ?? 0,
            fspl_hcm: s.fspl_hcm ?? 0,
            linkStatus_hcm: s.linkStatusHCM ?? 'NO SIGNAL',

            velocityKms: s.velocityKms ?? 0,
            inclinationDeg: s.inclinationDeg ?? 0,
            periodMin: s.periodMin ?? 0,
            raan: s.raan ?? 0,
            trueAnomaly: s.trueAnomaly ?? 0,
            band: s.band ?? '',
        };   
    }) as LeoSatellite[];
});

// Lắng nghe sự thay đổi để tự động focus vệ tinh tốt nhất
if (browser) {
    leoDetailData.subscribe(payload => {
        if (!payload || payload.length === 0) return;
        selectedLeoId.update(current => {
            if (!current || !payload.some(s => s.id === current)) {
                const preferred =
                    payload.find((s) => s.status === 'ACTIVE') ??
                    payload.reduce(
                        (best, s) => (s.elevation > best.elevation ? s : best),
                        payload[0]
                    );
                return preferred ? preferred.id : current;
            }
            return current;
        });
    });
}

import { connectWebSocket, disconnectWebSocket } from './store';

// Xóa các websocket độc lập, tab sẽ tự kết nối chung từ file store.ts nếu cần ở +layout.svelte
export function connectLeoWebSocket() {
    connectWebSocket();
}

export function disconnectLeoWebSocket() {
    // Để giữ kết nối ổn định dù chuyển tab, có thể tạm thời không disconnect.
    // Hoặc có thể gọi disconnectWebSocket();
}

