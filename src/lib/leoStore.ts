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
    distance: number;
    status: string;
    color: string;
    cn: number;
    fspl: number;
    delay: number;
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
            alt_km: s.altKm || 1200,
            elevation: s.elevationHanoi || 0,
            azimuth: s.azimuthHanoi || 0,
            distance: dist,
            // Logic status tái tạo lại logic trước đây
            status: (s.elevationHanoi && s.elevationHanoi > 10) ? (s.elevationHanoi >= 20 ? "ACTIVE" : "STANDBY") : "NO SIGNAL",
            color: (s.elevationHanoi && s.elevationHanoi > 10) ? (s.elevationHanoi >= 20 ? "#10b981" : "#f59e0b") : "#ef4444",
            cn: s.cn || 0,
            fspl: s.fspl || 0,
            delay: s.delayMs || 0
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

