<script lang="ts">
  import { leoDetailData, selectedLeoId } from '$lib/leoStore';
  import EarthMap from './EarthMap.svelte';

  let satellites = $derived($leoDetailData);
  let selectedId = $derived($selectedLeoId);
  let sat = $derived(satellites.find((s) => s.id === selectedId) ?? null);

  // 1. Thêm biến quản lý trạng thái Tab (Svelte 5 syntax)
  let activeTab = $state('tong_quan'); // Các giá trị: 'tong_quan' | 'quy_dao' | 'lien_ket'
</script>

{#if !sat}
  <div class="empty">Chọn vệ tinh hoặc đang chờ main.py (Walker-Delta, cổng 8000)...</div>
{:else}
  <div class="detail-header">
    <h2>
      {sat.id}
      <span class="status-badge" style:color={sat.color} style:border-color={sat.color}>{sat.status}</span>
    </h2>
    <div class="tabs">
      <span class={activeTab === 'tong_quan' ? 'active' : ''} onclick={() => activeTab = 'tong_quan'}>Tổng quan</span>
      <span class={activeTab === 'quy_dao' ? 'active' : ''} onclick={() => activeTab = 'quy_dao'}>Quỹ đạo</span>
      <span class={activeTab === 'lien_ket' ? 'active' : ''} onclick={() => activeTab = 'lien_ket'}>Liên kết</span>
    </div>
  </div>

  {#if activeTab === 'tong_quan'}
    <div class="detail-content">
      <div class="visual-section">
        <div class="sat-image-placeholder">
          <EarthMap />
        </div>
        <div class="basic-stats">
          <div class="stat-box"><span>Altitude</span><strong>{sat.alt_km ?? '--'} km</strong></div>
          <div class="stat-box"><span>Distance</span><strong>{sat.distance ?? '--'} km</strong></div>
          <div class="stat-box"><span>Elevation</span><strong>{sat.elevation ?? '--'}°</strong></div>
          <div class="stat-box"><span>Azimuth</span><strong>{sat.azimuth ?? '--'}°</strong></div>
          <div class="stat-box"><span>Gateway</span><strong>Hà Nội</strong></div>
          <div class="stat-box"><span>Nguồn</span><strong>Walker-Delta</strong></div>
        </div>
      </div>

      <div class="info-table">
        <h3>THÔNG TIN VỆ TINH</h3>
        <div class="info-row"><span class="lbl">Vị trí</span><span class="val">{sat.lat}°, {sat.lng}°</span></div>
        <div class="info-row"><span class="lbl">Elevation (Hà Nội)</span><span class="val">{sat.elevation}°</span></div>
        <div class="info-row"><span class="lbl">Azimuth (Hà Nội)</span><span class="val">{sat.azimuth}°</span></div>
        <div class="info-row"><span class="lbl">Elevation (Đà Nẵng)</span><span class="val">{sat.elevation_danang ?? '--'}°</span></div>
        <div class="info-row"><span class="lbl">Azimuth (Đà Nẵng)</span><span class="val">{sat.azimuth_danang ?? '--'}°</span></div>
        <div class="info-row"><span class="lbl">Elevation (TP.HCM)</span><span class="val">{sat.elevation_hcm ?? '--'}°</span></div>
        <div class="info-row"><span class="lbl">Azimuth (TP.HCM)</span><span class="val">{sat.azimuth_hcm ?? '--'}°</span></div>
        <div class="info-row"><span class="lbl">C/N</span><span class="val highlight">{sat.status === 'NO SIGNAL' ? 'Không liên kết' : `${sat.cn} dB-Hz`}</span></div>
        <div class="info-row"><span class="lbl">FSPL</span><span class="val">{sat.status === 'NO SIGNAL' ? '—' : `${sat.fspl} dB`}</span></div>
        <div class="info-row"><span class="lbl">Trễ một chiều</span><span class="val">{sat.status === 'NO SIGNAL' ? '—' : `${sat.delay} ms`}</span></div>
        <div class="info-row"><span class="lbl">Khoảng cách</span><span class="val">{sat.distance ?? '--'} km</span></div>
      </div>
    </div>

  {:else if activeTab === 'quy_dao'}
    <div class="detail-content" style="flex-direction: column; gap: 2rem; overflow-y: auto;">
      <div class="info-table" style="width: 100%;">
        <h3>ĐỘNG LỰC HỌC QUỸ ĐẠO</h3>
        <div class="info-row"><span class="lbl">Độ cao (Altitude)</span><span class="val">{sat.alt_km ?? '--'} km (LEO)</span></div>
        <div class="info-row"><span class="lbl">Vận tốc di chuyển</span><span class="val">{sat.velocityKms ?? '--'} km/s</span></div>
        <div class="info-row"><span class="lbl">Chu kỳ vòng quay</span><span class="val">{sat.periodMin ?? '--'} phút</span></div>
      </div>

      <div class="info-table" style="width: 100%;">
        <h3>THAM SỐ CẤU HÌNH WALKER</h3>
        <div class="info-row"><span class="lbl">Góc nghiêng (Inclination - i)</span><span class="val">{sat.inclinationDeg ?? '--'}°</span></div>
        <div class="info-row"><span class="lbl">Điểm nút lên (RAAN - Ω)</span><span class="val highlight" style="font-family: monospace;">{sat.raan ?? '--'}°</span></div>
        <div class="info-row"><span class="lbl">Dị thường thực (True Anomaly - ν)</span><span class="val" style="color: #34d399; font-family: monospace;">{sat.trueAnomaly ?? '--'}°</span></div>
      </div>

      <div style="background: rgba(15, 23, 42, 0.5); border-left: 3px solid #3b82f6; padding: 0.75rem; border-radius: 4px; font-size: 0.75rem; color: #94a3b8; line-height: 1.5;">
        <strong style="color: #cbd5e1;">Mô phỏng quỹ đạo:</strong> Vị trí được tính toán theo thời gian thực dựa trên cơ học thiên thể Kepler. 
        Mô hình chưa bao gồm tác động nhiễu loạn từ sức cản khí quyển hoặc độ dẹt của Trái Đất (J2).
      </div>
    </div>

  {:else if activeTab === 'lien_ket'}
    <div class="detail-content" style="flex-direction: column; gap: 2rem; overflow-y: auto;">
      
      <div class="info-table" style="width: 100%;">
        <h3>TRẠNG THÁI LIÊN KẾT (LINK STATUS)</h3>
        <div class="info-row">
          <span class="lbl">Tình trạng</span>
          <span class="val" style="color: {sat.status === 'NO SIGNAL' ? '#ef4444' : (sat.status === 'HANDOVER' ? '#f59e0b' : '#10b981')}; font-weight: bold;">
            {sat.linkStatus ?? '--'}
          </span>
        </div>
        <div class="info-row"><span class="lbl">Băng tần hoạt động (Band)</span><span class="val">{sat.band ?? '--'}</span></div>
      </div>

      <div class="info-table" style="width: 100%;">
        <h3>CHẤT LƯỢNG DỊCH VỤ (QoS)</h3>
        <div class="info-row">
          <span class="lbl">Tỷ số tín hiệu/nhiễu (C/N)</span>
          <span class="val highlight">{sat.status === 'NO SIGNAL' ? '--' : `${sat.cn} dB-Hz`}</span>
        </div>
        <div class="info-row">
          <span class="lbl">Suy hao không gian tự do (FSPL)</span>
          <span class="val">{sat.status === 'NO SIGNAL' ? '--' : `${sat.fspl} dB`}</span>
        </div>
        <div class="info-row">
          <span class="lbl">Độ trễ truyền dẫn 1 chiều</span>
          <span class="val" style="color: #fbbf24;">{sat.status === 'NO SIGNAL' ? '--' : `${sat.delay} ms`}</span>
        </div>
      </div>

    </div>
  {/if}
{/if}

<style>
  /* CSS của bạn được giữ nguyên hoàn toàn */
  .empty { color: #64748b; font-size: 0.85rem; text-align: center; margin-top: 2rem; }
  .detail-header { display: flex; align-items: center; gap: 1rem; border-bottom: 1px solid #1e293b; padding-bottom: 0.75rem; margin-bottom: 1rem; }
  .detail-header h2 { margin: 0; font-size: 1.1rem; color: #f8fafc; display: flex; align-items: center; gap: 0.5rem; }
  .status-badge { font-size: 0.65rem; padding: 0.2rem 0.5rem; border-radius: 12px; background: rgba(16, 185, 129, 0.1); border: 1px solid; }

  .tabs { display: flex; gap: 1rem; font-size: 0.8rem; color: #64748b; margin-left: auto; }
  .tabs span { cursor: pointer; padding-bottom: 0.75rem; margin-bottom: -0.75rem; transition: color 0.2s ease; }
  .tabs span:hover { color: #94a3b8; }
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