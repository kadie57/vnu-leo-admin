<script lang="ts">
  import { leoDetailData, selectedLeoId } from '$lib/leoStore';
  import EarthMap from './EarthMap.svelte';

  let satellites = $derived($leoDetailData);
  let selectedId = $derived($selectedLeoId);
  let sat = $derived(satellites.find((s) => s.id === selectedId) ?? null);
</script>

{#if !sat}
  <div class="empty">Chọn vệ tinh hoặc đang chờ main.py (Walker-Delta, cổng 8001)...</div>
{:else}
  <div class="detail-header">
    <h2>
      {sat.id}
      <span class="status-badge" style:color={sat.color} style:border-color={sat.color}>{sat.status}</span>
    </h2>
    <div class="tabs">
      <span class="active">Tổng quan</span>
      <span>Quỹ đạo</span>
      <span>Liên kết</span>
    </div>
  </div>

  <div class="detail-content">
    <div class="visual-section">
      <div class="sat-image-placeholder">
        <EarthMap />
      </div>

      <div class="basic-stats">
        <div class="stat-box"><span>Altitude</span><strong>{sat.alt_km} km</strong></div>
        <div class="stat-box"><span>Distance</span><strong>{sat.distance} km</strong></div>
        <div class="stat-box"><span>Elevation</span><strong>{sat.elevation}°</strong></div>
        <div class="stat-box"><span>Azimuth</span><strong>{sat.azimuth}°</strong></div>
        <div class="stat-box"><span>Gateway</span><strong>Hà Nội</strong></div>
        <div class="stat-box"><span>Nguồn</span><strong>Walker-Delta</strong></div>
      </div>
    </div>

    <div class="info-table">
      <h3>THÔNG TIN VỆ TINH</h3>
      <div class="info-row"><span class="lbl">Vị trí</span><span class="val">{sat.lat}°, {sat.lng}°</span></div>
      <div class="info-row"><span class="lbl">Elevation (Hà Nội)</span><span class="val">{sat.elevation}°</span></div>
      <div class="info-row"><span class="lbl">Azimuth (Hà Nội)</span><span class="val">{sat.azimuth}°</span></div>
      <div class="info-row"><span class="lbl">C/N</span><span class="val highlight">{sat.status === 'NO SIGNAL' ? 'Không liên kết' : `${sat.cn} dB-Hz`}</span></div>
      <div class="info-row"><span class="lbl">FSPL</span><span class="val">{sat.status === 'NO SIGNAL' ? '—' : `${sat.fspl} dB`}</span></div>
      <div class="info-row"><span class="lbl">Trễ một chiều</span><span class="val">{sat.status === 'NO SIGNAL' ? '—' : `${sat.delay} ms`}</span></div>
      <div class="info-row"><span class="lbl">Khoảng cách</span><span class="val">{sat.distance} km</span></div>
    </div>
  </div>
{/if}

<style>
  .empty { color: #64748b; font-size: 0.85rem; text-align: center; margin-top: 2rem; }
  .detail-header { display: flex; align-items: center; gap: 1rem; border-bottom: 1px solid #1e293b; padding-bottom: 0.75rem; margin-bottom: 1rem; }
  .detail-header h2 { margin: 0; font-size: 1.1rem; color: #f8fafc; display: flex; align-items: center; gap: 0.5rem; }
  .status-badge { font-size: 0.65rem; padding: 0.2rem 0.5rem; border-radius: 12px; background: rgba(16, 185, 129, 0.1); border: 1px solid; }

  .tabs { display: flex; gap: 1rem; font-size: 0.8rem; color: #64748b; margin-left: auto; }
  .tabs span { cursor: pointer; padding-bottom: 0.75rem; margin-bottom: -0.75rem; }
  .tabs span.active { color: #3b82f6; border-bottom: 2px solid #3b82f6; font-weight: 500; }

  .detail-content { display: flex; gap: 1.5rem; flex: 1; min-height: 0; }
  .visual-section { flex: 1; display: flex; flex-direction: column; gap: 1rem; }
  .sat-image-placeholder { flex: 1; border-radius: 8px; overflow: hidden; border: 1px solid #334155; background: #020617; min-height: 120px; }

  .basic-stats { display: flex; justify-content: space-between; background: #0d1424; padding: 0.75rem; border-radius: 6px; border: 1px solid #1e293b; flex-wrap: wrap; gap: 0.5rem; }
  .stat-box { display: flex; flex-direction: column; align-items: center; gap: 4px; }
  .stat-box span { font-size: 0.65rem; color: #94a3b8; }
  .stat-box strong { font-size: 0.8rem; color: #e2e8f0; }

  .info-table { width: 280px; display: flex; flex-direction: column; gap: 0.75rem; flex-shrink: 0; }
  .info-table h3 { font-size: 0.8rem; color: #cbd5e1; margin: 0 0 0.5rem 0; }
  .info-row { display: flex; justify-content: space-between; font-size: 0.75rem; align-items: center; border-bottom: 1px dashed #1e293b; padding-bottom: 0.4rem; gap: 0.5rem; }
  .lbl { color: #94a3b8; }
  .val { color: #f8fafc; font-weight: 500; text-align: right; }
  .highlight { color: #10b981; }
</style>
