import { get, writable } from 'svelte/store';
import { browser } from '$app/environment';

/** Dữ liệu từ backend/main.py — mô phỏng Walker-Delta 32 vệ tinh */
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

export const leoDetailData = writable<LeoSatellite[]>([]);
export const selectedLeoId = writable<string | null>(null);

/** Tab Lớp 3 — main.py cổng 8001 */
const LEO_WS = 'ws://127.0.0.1:8001/ws/vnu-leo';

let ws: WebSocket | undefined;

export function connectLeoWebSocket() {
    if (!browser) return;
    if (ws && ws.readyState === WebSocket.OPEN) return;

    ws = new WebSocket(LEO_WS);

    ws.onmessage = (event) => {
        try {
            const payload = JSON.parse(event.data) as LeoSatellite[];
            if (!Array.isArray(payload)) return;

            leoDetailData.set(payload);

            const current = get(selectedLeoId);
            if (!current || !payload.some((s) => s.id === current)) {
                const preferred =
                    payload.find((s) => s.status === 'ACTIVE') ??
                    payload.reduce(
                        (best, s) => (s.elevation > best.elevation ? s : best),
                        payload[0]
                    );
                if (preferred) selectedLeoId.set(preferred.id);
            }
        } catch (err) {
            console.error('LEO WS parse error:', err);
        }
    };

    ws.onclose = () => {
        ws = undefined;
        setTimeout(connectLeoWebSocket, 2000);
    };

    ws.onerror = () => {
        ws?.close();
    };
}

export function disconnectLeoWebSocket() {
    if (ws) {
        ws.close();
        ws = undefined;
    }
}

