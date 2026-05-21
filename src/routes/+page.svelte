<script lang="ts">
  import OverviewTab from '$lib/components/OverviewTab.svelte';

  type AnalyticsComponent = typeof import('$lib/components/AnalyticsTab.svelte').default;
  let AnalyticsTab = $state<AnalyticsComponent | null>(null);

  let activeTab = $state<'overview' | 'analytics'>('overview');

  async function openAnalytics() {
    activeTab = 'analytics';
    if (!AnalyticsTab) {
      const mod = await import('$lib/components/AnalyticsTab.svelte');
      AnalyticsTab = mod.default;
    }
  }

  function openOverview() {
    activeTab = 'overview';
  }
</script>

<div class="app-layout">
  <header class="top-bar">
    <div class="brand">
      <span class="status-dot"></span>
      <h1>GIÁM SÁT MẠNG VỆ TINH VNU-LEO</h1>
    </div>

    <div class="tab-controls">
      <button
        class:active={activeTab === 'overview'}
        onclick={openOverview}
      >
        Lớp 2: Overview
      </button>
      <button
        class:active={activeTab === 'analytics'}
        onclick={openAnalytics}
      >
        Lớp 3: Chi tiết vệ tinh
      </button>
    </div>
  </header>

  <section class="content-area">
    {#if activeTab === 'overview'}
      <OverviewTab />
    {:else if AnalyticsTab}
      <AnalyticsTab />
    {:else}
      <div class="tab-loading">Đang tải tab Lớp 3...</div>
    {/if}
  </section>
</div>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    background-color: #0b1120;
    color: #e2e8f0;
    font-family: 'Inter', sans-serif;
  }

  .app-layout {
    display: flex;
    flex-direction: column;
    height: 100vh;
  }

  .top-bar {
    height: 60px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 1.5rem;
    background-color: #0f172a;
    border-bottom: 1px solid #1e293b;
  }

  .brand {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .brand h1 {
    font-size: 1.1rem;
    font-weight: 600;
    margin: 0;
    letter-spacing: 0.5px;
  }

  .status-dot {
    width: 12px;
    height: 12px;
    background-color: #10b981;
    border-radius: 50%;
  }

  .tab-controls button {
    background: transparent;
    border: 1px solid #334155;
    color: #94a3b8;
    padding: 0.5rem 1rem;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s ease;
  }

  .tab-controls button:first-child {
    border-radius: 6px 0 0 6px;
  }

  .tab-controls button:last-child {
    border-radius: 0 6px 6px 0;
  }

  .tab-controls button.active {
    background-color: #2563eb;
    color: white;
    border-color: #2563eb;
  }

  .content-area {
    flex: 1;
    overflow: hidden;
  }

  .tab-loading {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #94a3b8;
    font-size: 0.9rem;
  }
</style>
