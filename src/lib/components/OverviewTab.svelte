<script lang="ts">
  import LeftStats from './LeftStats.svelte';
  import EarthMap from './EarthMap.svelte';
  import GatewayPanel from './GatewayPanel.svelte';
</script>

<div class="overview-container">
  <aside class="left-panel">
    <LeftStats />
  </aside>

  <main class="center-map">
    <EarthMap />
  </main>

  <aside class="right-panel">
    <GatewayPanel />
  </aside>
</div>

<style>
  .overview-container {
    display: grid;
    /* Thu hẹp cột trái còn 230px, mở rộng cột phải lên 380px */
    grid-template-columns: 230px 1fr 380px; 
    gap: 1rem; /* Giảm gap giữa các cột xuống một chút */
    height: 100%;
    width: 100%;
    padding: 1rem;
    box-sizing: border-box;
    min-height: 0;
    overflow: hidden;
  }

  .left-panel, .right-panel {
    background-color: rgba(15, 23, 42, 0.6); /* Nền tối, trong suốt nhẹ */
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    min-height: 0;
    overflow: hidden;
  }

  .center-map {
    border-radius: 8px;
    position: relative;
    overflow: hidden;
    /* Đổ viền nhẹ cho khu vực bản đồ */
    border: 1px solid #1e293b; 
    min-height: 0;
    overflow: hidden;
  }
</style>