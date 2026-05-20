import { writable } from 'svelte/store';
import { browser } from '$app/environment';

export interface OverviewStats {
    totalSatellites: number;
    coveringVietnam: number;
    upcomingHandover: number;
    systemStatus: string;
    systemStatusColor: string;
    avgLatencyMs: number;
}

export interface WalkerConfig {
    planes: number;
    satsPerPlane: number;
    inclinationDeg: number;
    altitudeKm: number;
}

export interface Satellite {
    id: string;
    lat: number;
    lng: number;
    latDir?: number;
    lngDir?: number;
    color: string;
    isActive?: boolean;
    status: string;
    altKm?: number;
    elevationHanoi?: number;
    azimuthHanoi?: number;
    cn?: number;
    delayMs?: number;
    fspl?: number;
    velocityKms?: number;
    inclinationDeg?: number;
    periodMin?: number;
    band?: string;
    linkStatus?: string;
}

export const satelliteData = writable<{
    satellites: Satellite[];
    gateways: unknown[];
    connections: unknown[];
    overview: OverviewStats | null;
    config: WalkerConfig | null;
    time: number;
}>({
    satellites: [],
    gateways: [],
    connections: [],
    overview: null,
    config: null,
    time: 0
});

let ws: WebSocket | undefined;

export function connectWebSocket() {
    if (!browser) return;
    if (ws && ws.readyState === WebSocket.OPEN) return;

    ws = new WebSocket('ws://127.0.0.1:8000/ws/vnu-leo');

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            satelliteData.set({
                satellites: data.satellites ?? [],
                gateways: data.gateways ?? [],
                connections: data.connections ?? [],
                overview: data.overview ?? null,
                config: data.config ?? null,
                time: data.time ?? 0
            });
        } catch (err) {
            console.error('Error parsing WS data:', err);
        }
    };

    ws.onclose = () => {
        ws = undefined;
        setTimeout(connectWebSocket, 1000);
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        ws?.close();
    };
}

export function disconnectWebSocket() {
    if (ws) {
        ws.close();
        ws = undefined;
    }
}
