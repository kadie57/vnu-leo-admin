<script lang="ts">
  import SatelliteList from './SatelliteList.svelte';
  import SatelliteDetail from './SatelliteDetail.svelte';
  import SatelliteCharts from './SatelliteCharts.svelte';
</script>

<div class="analytics-container">
  <aside class="left-panel">
    <SatelliteList />
  </aside>

  <main class="center-panel">
    <SatelliteDetail />
  </main>

  <aside class="right-panel">
    <SatelliteCharts />
  </aside>
</div>

<style>
  .analytics-container {
    display: grid;
    /* Cột trái 250px, Cột giữa linh hoạt, Cột phải 350px */
    grid-template-columns: 250px 1fr 350px;
    gap: 1rem;
    height: 100%;
    width: 100%;
    padding: 1rem;
    box-sizing: border-box;
    min-height: 0;
    overflow: hidden;
  }

  .left-panel, .center-panel, .right-panel {
    background-color: rgba(15, 23, 42, 0.6);
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    min-height: 0;
    overflow: hidden;
  }
</style>