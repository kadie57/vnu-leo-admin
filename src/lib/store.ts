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

export const satelliteData = writable<{
    satellites: unknown[];
    gateways: unknown[];
    connections: unknown[];
    overview: OverviewStats | null;
}>({
    satellites: [],
    gateways: [],
    connections: [],
    overview: null
});

let ws: WebSocket | undefined;

export function connectWebSocket() {
    if (!browser) return;
    if (ws && ws.readyState === WebSocket.OPEN) return;
    
    ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            satelliteData.set(data);
        } catch (err) {
            console.error('Error parsing WS data:', err);
        }
    };

    ws.onclose = () => {
        setTimeout(connectWebSocket, 1000);
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        ws?.close();
    };
}
