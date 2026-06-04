<script lang="ts">
  import {
    Chart as ChartJS,
    Title,
    Tooltip,
    Legend,
    LineElement,
    LinearScale,
    PointElement,
    CategoryScale,
  } from 'chart.js';
  import { Line } from 'svelte-chartjs';
  import { leoDetailData, selectedLeoId } from '$lib/leoStore';

  ChartJS.register(Title, Tooltip, Legend, LineElement, LinearScale, PointElement, CategoryScale);

  type Location = 'HANOI' | 'DANANG' | 'HCM';

  const MAX_POINTS = 20;

  let activeTab = $state<Location>('HANOI');

  let labels = $state<string[]>([]);
  
  let cnSeries = $state<number[]>([]);
  let delaySeries = $state<number[]>([]);

  let cnSeries_danang = $state<number[]>([]);
  let delaySeries_danang = $state<number[]>([]);

  let cnSeries_hcm = $state<number[]>([]);
  let delaySeries_hcm = $state<number[]>([]);

  let satellites = $derived($leoDetailData);
  let selectedId = $derived($selectedLeoId);
  let sat = $derived(satellites.find((s) => s.id === selectedId) ?? null);

  let lastTrackedId = $state<string | null>(null);

  $effect(() => {
    if (!sat) return;

    const timeLabel = new Date().toLocaleTimeString('vi-VN', { second: '2-digit' });

    if (labels[labels.length - 1] !== timeLabel) {
      labels = [...labels.slice(-MAX_POINTS + 1), timeLabel];
      
      cnSeries = [...cnSeries.slice(-MAX_POINTS + 1), sat.cn ?? 0];
      delaySeries = [...delaySeries.slice(-MAX_POINTS + 1), sat.delay ?? 0];

      cnSeries_danang = [...cnSeries_danang.slice(-MAX_POINTS + 1), sat.cn_danang ?? 0];
      delaySeries_danang = [...delaySeries_danang.slice(-MAX_POINTS + 1), sat.delay_danang ?? 0];

      cnSeries_hcm = [...cnSeries_hcm.slice(-MAX_POINTS + 1), sat.cn_hcm ?? 0];
      delaySeries_hcm = [...delaySeries_hcm.slice(-MAX_POINTS + 1), sat.delay_hcm ?? 0];
    }
  });

  $effect(() => {
    if (selectedId !== lastTrackedId) {
      lastTrackedId = selectedId;
      labels = [];
      cnSeries = [];
      delaySeries = [];
      cnSeries_danang = [];
      delaySeries_danang = [];
      cnSeries_hcm = [];
      delaySeries_hcm = [];
    }
  });

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    plugins: { legend: { display: false } },
    scales: {
      x: { grid: { color: '#1e293b' }, ticks: { color: '#64748b', font: { size: 10 }, maxTicksLimit: 6 } },
      y: { grid: { color: '#1e293b' }, ticks: { color: '#64748b', font: { size: 10 } } },
    },
  };

  function createChartData(series: number[], label: string, color: string) {
    return {
      labels,
      datasets: [{
        label,
        data: series,
        borderColor: color,
        backgroundColor: `${color}33`, // 20% opacity
        borderWidth: 2,
        tension: 0.3,
        pointRadius: 0,
      }],
    };
  }

  const cnData = $derived(createChartData(cnSeries, 'C/N Hà Nội', '#10b981'));
  const delayData = $derived(createChartData(delaySeries, 'Delay Hà Nội', '#f59e0b'));

  const cnData_danang = $derived(createChartData(cnSeries_danang, 'C/N Đà Nẵng', '#38bdf8'));
  const delayData_danang = $derived(createChartData(delaySeries_danang, 'Delay Đà Nẵng', '#e11d48'));

  const cnData_hcm = $derived(createChartData(cnSeries_hcm, 'C/N TP.HCM', '#a78bfa'));
  const delayData_hcm = $derived(createChartData(delaySeries_hcm, 'Delay TP.HCM', '#facc15'));

  const locationData = $derived({
    HANOI: {
      elevation: sat?.elevation ?? 0,
      cnData: cnData,
      delayData: delayData,
      cnLineClass: 'line-green',
      delayLineClass: 'line-yellow'
    },
    DANANG: {
      elevation: sat?.elevation_danang ?? 0,
      cnData: cnData_danang,
      delayData: delayData_danang,
      cnLineClass: 'line-sky',
      delayLineClass: 'line-rose'
    },
    HCM: {
      elevation: sat?.elevation_hcm ?? 0,
      cnData: cnData_hcm,
      delayData: delayData_hcm,
      cnLineClass: 'line-violet',
      delayLineClass: 'line-amber'
    }
  });

  let currentView = $derived(locationData[activeTab]);

</script>

<div class="charts-container">
  <div class="header">
    <h3>BIỂU ĐỒ (WALKER-DELTA)</h3>
    <div class="tabs">
      <button onclick={() => activeTab = 'HANOI'} class:active={activeTab === 'HANOI'}>Hà Nội</button>
      <button onclick={() => activeTab = 'DANANG'} class:active={activeTab === 'DANANG'}>Đà Nẵng</button>
      <button onclick={() => activeTab = 'HCM'} class:active={activeTab === 'HCM'}>TP. HCM</button>
    </div>
  </div>

  {#if sat}
    <p class="hint">
      {sat.id} · elev {currentView.elevation.toFixed(1)}° · {activeTab}
      {#if currentView.elevation < 15}
        <span class="warn">(dưới 15°, C/N &amp; delay = 0)</span>
      {/if}
    </p>
  {:else}
    <p class="hint">Chọn vệ tinh trong danh sách</p>
  {/if}

  <div class="chart-block">
    <div class="chart-title">C/N (dB-Hz)</div>
    <div class="chart-wrapper {currentView.cnLineClass}">
      {#if labels.length > 0}
        <Line data={currentView.cnData} options={chartOptions} />
      {:else}
        <span class="placeholder">Đang thu mẫu (1 giây/lần)...</span>
      {/if}
    </div>
  </div>

  <div class="chart-block">
    <div class="chart-title">Độ trễ (ms)</div>
    <div class="chart-wrapper {currentView.delayLineClass}">
      {#if labels.length > 0}
        <Line data={currentView.delayData} options={chartOptions} />
      {:else}
        <span class="placeholder">Đang thu mẫu (1 giây/lần)...</span>
      {/if}
    </div>
  </div>
</div>

<style>
  .charts-container { display: flex; flex-direction: column; gap: 0.5rem; height: 100%; }
  .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
  h3 { font-size: 0.8rem; color: #cbd5e1; margin: 0; font-weight: 600; }
  .tabs { display: flex; gap: 0.25rem; background: #1e293b; padding: 2px; border-radius: 6px; }
  .tabs button {
    background: transparent;
    border: none;
    color: #94a3b8;
    padding: 0.25rem 0.75rem;
    font-size: 0.7rem;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
  }
  .tabs button.active {
    background: #334155;
    color: #f1f5f9;
    font-weight: 600;
  }
  .hint { font-size: 0.7rem; color: #64748b; margin: 0; }
  .warn { color: #f59e0b; }
  .chart-block { flex: 1; display: flex; flex-direction: column; gap: 0.5rem; background: #0d1424; border: 1px solid #1e293b; padding: 0.75rem; border-radius: 6px; min-height: 0; }
  .chart-title { font-size: 0.75rem; color: #94a3b8; }
  .chart-wrapper { flex: 1; position: relative; min-height: 100px; border-radius: 4px; background: rgba(15, 23, 42, 0.4); }
  .placeholder { display: flex; align-items: center; justify-content: center; height: 100%; font-size: 0.7rem; color: #475569; font-style: italic; }
  
  .line-green { border-bottom: 2px solid #10b981; }
  .line-yellow { border-bottom: 2px solid #f59e0b; }
  .line-sky { border-bottom: 2px solid #38bdf8; }
  .line-rose { border-bottom: 2px solid #e11d48; }
  .line-violet { border-bottom: 2px solid #a78bfa; }
  .line-amber { border-bottom: 2px solid #facc15; }
</style>
