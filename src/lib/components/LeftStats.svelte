<script lang="ts">
  import { satelliteData } from '$lib/store';

  let overview = $derived($satelliteData.overview);
</script>

{#if !overview}
  <div class="stats-box">
    <p class="loading">Đang chờ dữ liệu từ Server...</p>
  </div>
{:else}
  <div class="stats-box">
    <h3>TỔNG QUAN HỆ THỐNG</h3>
    <div class="stat-item"><span>Tổng số vệ tinh:</span> <strong>{overview.totalSatellites}</strong></div>
    <div class="stat-item"><span>Đang phủ Việt Nam:</span> <strong style="color: #10b981;">{overview.coveringVietnam}</strong></div>
    <div class="stat-item"><span>Sắp handover:</span> <strong style="color: #f59e0b;">{overview.upcomingHandover}</strong></div>
  </div>

  <div class="stats-box">
    <h3>TRẠNG THÁI HỆ THỐNG</h3>
    <div class="stat-item">
      <span>Tình trạng:</span>
      <span style:color={overview.systemStatusColor}>{overview.systemStatus}</span>
    </div>
    <div class="stat-item">
      <span>Độ trễ trung bình:</span>
      <strong>{overview.avgLatencyMs} ms</strong>
    </div>
  </div>
{/if}

<style>
  .stats-box {
    background: rgba(30, 41, 59, 0.4);
    border-radius: 6px;
    padding: 0.65rem;
    border: 1px solid #334155;
    margin-bottom: 1rem;
  }

  .loading {
    color: #64748b;
    font-size: 0.7rem;
    text-align: center;
    margin: 0;
  }
  
  h3 {
    font-size: 0.7rem;
    color: #94a3b8;
    margin-top: 0;
    margin-bottom: 0.75rem;
    border-bottom: 1px solid #334155;
    padding-bottom: 0.4rem;
    white-space: nowrap;
  }
  
  .stat-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.6rem;
    font-size: 0.7rem;
  }

  .stat-item span:first-child {
    white-space: nowrap;
  }

  .stat-item strong, 
  .stat-item span:last-child {
    text-align: right;
    white-space: nowrap;
  }
</style>
