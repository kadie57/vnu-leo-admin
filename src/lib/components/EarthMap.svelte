<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { browser } from '$app/environment';
  import { satelliteData, connectWebSocket } from '$lib/store';
  
  let mapElement;
  let map;
  let coverageLayer;
  let satelliteLayer;
  let linksLayer;
  
  // Trạng thái nút bật/tắt vùng phủ
  let showCoverage = true;

  // Dữ liệu 3 trạm Gateway mặt đất tĩnh
  const staticGateways = [
    { name: 'Gateway Hà Nội', lat: 21.0328, lng: 105.8342, statusColor: '#10b981' },
    { name: 'Gateway Đà Nẵng', lat: 16.0544, lng: 108.2022, statusColor: '#f59e0b' },
    { name: 'Gateway TP.HCM', lat: 10.8231, lng: 106.6297, statusColor: '#ef4444' }
  ];

  onMount(async () => {
    if (browser) {
      // Import động leaflet để tránh lỗi SSR trong SvelteKit
      const L = (await import('leaflet')).default;
      await import('leaflet/dist/leaflet.css');

      // Khởi tạo bản đồ, khóa góc nhìn vào Việt Nam
      map = L.map(mapElement, {
        center: [16.0, 106.0], // Tọa độ trung tâm Việt Nam
        zoom: 4.5, // Mở rộng tầm nhìn để thấy nhiều vệ tinh hơn
        zoomControl: false,
        attributionControl: false
      });

      // Sử dụng bản đồ nền Dark Matter (giao diện NOC đen)
      L.tileLayer('http://mt0.google.com/vt/lyrs=m@221097413,highlight:0x9e5540b616a61771&hl=en&gl=vn&src=app&x={x}&y={y}&z={z}&s=Galile', {
  maxZoom: 19
}).addTo(map);

      // Lớp cho vùng phủ sóng, vệ tinh và đường kẻ (links) kết nối
      coverageLayer = L.layerGroup().addTo(map);
      linksLayer = L.layerGroup().addTo(map);
      satelliteLayer = L.layerGroup().addTo(map);

      // Mở kết nối WebSocket tới Python Backend
      connectWebSocket();

      // Vẽ Gateways cố định trên mặt đất 1 lần
      staticGateways.forEach(gw => {
        const gwIcon = L.divIcon({
          className: 'custom-gw-icon',
          html: `<div class="pulse-dot" style="background-color: ${gw.statusColor}; box-shadow: 0 0 10px ${gw.statusColor};"></div>`,
          iconSize: [12, 12]
        });
        L.marker([gw.lat, gw.lng], { icon: gwIcon })
          .bindTooltip(gw.name, { permanent: true, direction: 'right', className: 'gw-label' })
          .addTo(map);
      });

      // Hàm vẽ lại vệ tinh và vùng phủ
      const drawFrame = (data) => {
        if (!map) return;
        satelliteLayer.clearLayers();
        coverageLayer.clearLayers();
        linksLayer.clearLayers();

        const satellites = data.satellites || [];
        const connections = data.connections || [];

        satellites.forEach(sat => {
          // Tính góc xoay vệ tinh theo hướng bay (từ API backend)
          const heading = Math.atan2(sat.lngDir, sat.latDir) * (180 / Math.PI);
          
          // Vẽ icon vệ tinh xịn giống mockup (SVG inline)
          const svgIcon = `
            <div style="transform: rotate(${heading}deg); display: flex; justify-content: center; align-items: center; width: 24px; height: 24px;">
              <svg viewBox="0 0 24 24" width="24" height="24">
                <!-- Quỹ đạo (Đuôi mờ) -->
                ${sat.isActive ? `<line x1="12" y1="24" x2="12" y2="40" stroke="${sat.color}" stroke-width="1" stroke-dasharray="2, 2" opacity="0.6" />` : ''}
                <!-- 2 Tấm pin mặt trời -->
                <rect x="2" y="10" width="7" height="6" fill="#1e293b" stroke="${sat.color}" stroke-width="1"/>
                <rect x="15" y="10" width="7" height="6" fill="#1e293b" stroke="${sat.color}" stroke-width="1"/>
                <!-- Thân vệ tinh -->
                <rect x="9" y="6" width="6" height="14" fill="#e2e8f0"/>
                <circle cx="12" cy="13" r="2" fill="${sat.color}" />
              </svg>
            </div>
          `;

          const satIcon = L.divIcon({
            className: 'custom-sat-icon',
            html: svgIcon,
            iconSize: [24, 24],
            iconAnchor: [12, 12]
          });

          L.marker([sat.lat, sat.lng], { icon: satIcon }).addTo(satelliteLayer);

          // Vẽ vùng phủ sóng
          if (showCoverage && sat.isActive) {
            L.circle([sat.lat, sat.lng], {
              color: sat.color,
              fillColor: sat.color,
              fillOpacity: 0.05, 
              radius: 400000, // phủ 400km
              weight: 0.5,
              dashArray: '3, 3'
            }).addTo(coverageLayer);
          }
        });

        // Vẽ đường nối giữa trạm Gateway mặt đất và Vệ tinh (handover)
        connections.forEach(conn => {
            const lineOptions = conn.isFlash 
              ? { color: '#eab308', weight: 2, dashArray: '5, 5' } 
              : { color: conn.color, weight: 1.5, dashArray: '4, 6' };
              
            L.polyline([[conn.gwLat, conn.gwLng], [conn.satLat, conn.satLng]], lineOptions).addTo(linksLayer);
        });
      };

      // Đăng ký Reactive update: Khi `$satelliteData` thay đổi, gọi `drawFrame()`
      const unsubscribe = satelliteData.subscribe((data) => {
          if (browser && L) drawFrame(data);
      });

      // Cleanup
      map.on('unload', () => { unsubscribe(); });
    }
  });

  onDestroy(() => {
    if (map) map.remove();
  });

  // Hàm xử lý khi bấm nút toggle
  function toggleCoverage() {
    showCoverage = !showCoverage;
  }
</script>

<div class="map-container">
  <div class="map-controls">
    <button class="toggle-btn" class:active={showCoverage} on:click={toggleCoverage}>
      <span class="indicator"></span>
      {showCoverage ? 'Đang bật vùng phủ' : 'Đã ẩn vùng phủ'}
    </button>
  </div>

  <div bind:this={mapElement} class="map-view"></div>
</div>

<style>
  .map-container {
    position: relative;
    width: 100%;
    height: 100%;
    border-radius: 6px;
    overflow: hidden;
    border: 1px solid #1e293b;
    display: flex;
    flex-direction: column;
  }

  .map-controls {
    position: absolute;
    top: 15px;
    right: 15px;
    z-index: 1000; /* Đảm bảo nút nổi lên trên bản đồ */
  }

  .toggle-btn {
    display: flex;
    align-items: center;
    gap: 8px;
    background-color: rgba(15, 23, 42, 0.9);
    border: 1px solid #334155;
    color: #cbd5e1;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.85rem;
    font-family: 'Inter', sans-serif;
    transition: all 0.2s;
  }

  .toggle-btn:hover {
    background-color: #1e293b;
  }

  .indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #64748b;
  }

  .toggle-btn.active .indicator {
    background-color: #2563eb;
    box-shadow: 0 0 8px #2563eb;
  }

  .toggle-btn.active {
    border-color: #2563eb;
  }

  .map-view {
    flex: 1;
    width: 100%;
    background-color: #020617;
  }

  /* CSS cho nhãn vệ tinh (Sẽ được Leaflet inject vào DOM) */
  :global(.gw-label) {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #e2e8f0;
    font-weight: 500;
    font-size: 0.75rem;
    text-shadow: 1px 1px 2px black;
  }
  
  :global(.custom-sat-icon) {
    background: transparent;
    border: none;
  }

  /* Hiệu ứng nhịp đập cho gateway dưới mặt đất */
  :global(.pulse-dot) {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    position: relative;
  }

  :global(.pulse-dot::after) {
    content: '';
    position: absolute;
    top: -4px;
    left: -4px;
    right: -4px;
    bottom: -4px;
    border-radius: 50%;
    /* Viền trắng mờ tỏa ra xung quanh */
    border: 2px solid rgba(255, 255, 255, 0.8);
    animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;
  }

  @keyframes ping {
    75%, 100% {
      transform: scale(2.5);
      opacity: 0;
    }
  }
</style>