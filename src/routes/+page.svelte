<script lang="ts">
  import OverviewTab from '$lib/components/OverviewTab.svelte';
  
  // 1. Bỏ dấu // ở dòng này để import file bạn vừa tạo
  import AnalyticsTab from '$lib/components/AnalyticsTab.svelte';

  let activeTab = $state<'overview' | 'analytics'>('overview');
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
        onclick={() => activeTab = 'overview'}
      >
        Lớp 2: Overview
      </button>
      <button 
        class:active={activeTab === 'analytics'} 
        onclick={() => activeTab = 'analytics'}
      >
        Lớp 3: Chi tiết vệ tinh
      </button>
    </div>
  </header>

  <section class="content-area">
    {#if activeTab === 'overview'}
      <OverviewTab />
    {:else if activeTab === 'analytics'}
      
      <AnalyticsTab />
      
    {/if}
  </section>
</div>

<style>
  /* Base style cho toàn bộ trang Dashboard */
  :global(body) {
    margin: 0;
    padding: 0;
    background-color: #0b1120; /* Màu nền xanh đen đặc trưng của NOC */
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
</style>