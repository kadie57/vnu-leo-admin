<script lang="ts">
  import { leoDetailData, selectedLeoId, type LeoSatellite } from '$lib/leoStore';

  let satellites = $derived(
    [...$leoDetailData].sort((a, b) => b.elevation - a.elevation)
  );
  let selectedId = $derived($selectedLeoId);

  function selectSatellite(sat: LeoSatellite) {
    selectedLeoId.set(sat.id);
  }
</script>

<div class="list-header">
  <h3>DANH SÁCH VỆ TINH ({satellites.length})</h3>
  <div class="search-box">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="search-icon"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
    <input type="text" placeholder="Tìm kiếm vệ tinh..." />
  </div>
</div>

<div class="sat-list">
  {#if satellites.length === 0}
    <div class="loading-msg">Chưa có dữ liệu — chạy main.py cổng 8001</div>
  {:else}
    <div class="ws-ok">Walker-Delta · {satellites.length} vệ tinh · main.py:8001</div>
  {/if}

  {#each satellites as sat (sat.id)}
    <button
      type="button"
      class="sat-item"
      class:active={selectedId === sat.id}
      onclick={() => selectSatellite(sat)}
    >
      <span class="sat-id">{sat.id}</span>
      <span class="sat-status" style:color={sat.color}>{sat.status}</span>
      <span class="sat-alt">{sat.elevation}° · {sat.alt_km} km</span>
    </button>
  {/each}
</div>

<style>
  .list-header h3 { font-size: 0.8rem; color: #cbd5e1; margin: 0 0 0.75rem 0; font-weight: 600; }
  .search-box { position: relative; margin-bottom: 1rem; }
  .search-icon { position: absolute; left: 8px; top: 50%; transform: translateY(-50%); width: 14px; height: 14px; color: #64748b; }
  .search-box input { width: 100%; background: #0d1424; border: 1px solid #334155; border-radius: 4px; padding: 0.4rem 0.4rem 0.4rem 1.75rem; color: #e2e8f0; font-size: 0.75rem; box-sizing: border-box; }
  .search-box input:focus { outline: none; border-color: #2563eb; }

  .sat-list { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 4px; scrollbar-width: thin; scrollbar-color: #334155 transparent; }
  .sat-item {
    display: grid;
    grid-template-columns: 70px 1fr 90px;
    align-items: center;
    padding: 0.5rem;
    border-radius: 4px;
    font-size: 0.7rem;
    cursor: pointer;
    transition: background 0.2s;
    background: transparent;
    border: none;
    width: 100%;
    text-align: left;
    color: inherit;
  }
  .sat-item:hover { background: rgba(51, 65, 85, 0.5); }
  .sat-item.active { background: rgba(37, 99, 235, 0.2); border-left: 2px solid #3b82f6; }

  .sat-id { color: #e2e8f0; font-weight: 500; }
  .sat-status { font-weight: 600; font-size: 0.65rem; text-align: center; }
  .sat-alt { color: #64748b; text-align: right; }

  .loading-msg { text-align: center; color: #64748b; margin-top: 2rem; font-size: 0.8rem; font-style: italic; animation: pulse 1.5s infinite; }
  .ws-ok { font-size: 0.65rem; color: #10b981; margin-bottom: 0.5rem; }
  @keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }
</style>
