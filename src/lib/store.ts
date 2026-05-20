import { writable } from 'svelte/store';
import { browser } from '$app/environment';

export const satelliteData = writable({
    satellites: [],
    gateways: [],
    connections: []
});

let ws;

export function connectWebSocket() {
    if (!browser) return; // Only run on client side
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
        // Tự động kết nối lại sau 1s nếu bị đứt
        setTimeout(connectWebSocket, 1000);
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        ws.close();
    };
}
