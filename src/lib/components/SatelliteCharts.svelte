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

  const MAX_POINTS = 20;

  let labels = $state<string[]>([]);
  let cnSeries = $state<number[]>([]);
  let delaySeries = $state<number[]>([]);

  let satellites = $derived($leoDetailData);
  let selectedId = $derived($selectedLeoId);
  let sat = $derived(satellites.find((s) => s.id === selectedId) ?? null);

  let lastTrackedId = $state<string | null>(null);

  $effect(() => {
    if (!sat) return;
    const cn = sat.cn ?? 0;
    const delay = sat.delay ?? 0;
    const label = new Date().toLocaleTimeString('vi-VN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });

    if (labels.length > 0 && labels[labels.length - 1] === label) {
      cnSeries = [...cnSeries.slice(0, -1), cn];
      delaySeries = [...delaySeries.slice(0, -1), delay];
      return;
    }

    labels = [...labels, label].slice(-MAX_POINTS);
    cnSeries = [...cnSeries, cn].slice(-MAX_POINTS);
    delaySeries = [...delaySeries, delay].slice(-MAX_POINTS);
  });

  $effect(() => {
    if (selectedId !== lastTrackedId) {
      lastTrackedId = selectedId;
      labels = [];
      cnSeries = [];
      delaySeries = [];
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

  const cnData = $derived({
    labels,
    datasets: [{
      label: 'C/N',
      data: cnSeries,
      borderColor: '#10b981',
      backgroundColor: 'rgba(16, 185, 129, 0.2)',
      borderWidth: 2,
      tension: 0.3,
      pointRadius: 0,
    }],
  });

  const delayData = $derived({
    labels,
    datasets: [{
      label: 'Delay',
      data: delaySeries,
      borderColor: '#f59e0b',
      backgroundColor: 'rgba(245, 158, 11, 0.15)',
      borderWidth: 2,
      tension: 0.3,
      pointRadius: 0,
    }],
  });
</script>

<div class="charts-container">
  <h3>BIỂU ĐỒ (WALKER-DELTA → HÀ NỘI)</h3>
  {#if sat}
    <p class="hint">
      {sat.id} · elev {sat.elevation}° · Hà Nội
      {#if sat.status === 'NO SIGNAL'}
        <span class="warn">(dưới 15°, C/N &amp; delay = 0)</span>
      {/if}
    </p>
  {:else}
    <p class="hint">Chọn vệ tinh trong danh sách</p>
  {/if}

  <div class="chart-block">
    <div class="chart-title">C/N (dB-Hz)</div>
    <div class="chart-wrapper line-green">
      {#if labels.length > 0}
        <Line data={cnData} options={chartOptions} />
      {:else}
        <span class="placeholder">Đang thu mẫu (1 giây/lần)...</span>
      {/if}
    </div>
  </div>

  <div class="chart-block">
    <div class="chart-title">Độ trễ (ms)</div>
    <div class="chart-wrapper line-yellow">
      {#if labels.length > 0}
        <Line data={delayData} options={chartOptions} />
      {:else}
        <span class="placeholder">Đang thu mẫu (1 giây/lần)...</span>
      {/if}
    </div>
  </div>
</div>

<style>
  .charts-container { display: flex; flex-direction: column; gap: 1rem; height: 100%; }
  h3 { font-size: 0.8rem; color: #cbd5e1; margin: 0; font-weight: 600; }
  .hint { font-size: 0.7rem; color: #64748b; margin: 0; }
  .warn { color: #f59e0b; }
  .chart-block { flex: 1; display: flex; flex-direction: column; gap: 0.5rem; background: #0d1424; border: 1px solid #1e293b; padding: 0.75rem; border-radius: 6px; min-height: 0; }
  .chart-title { font-size: 0.75rem; color: #94a3b8; }
  .chart-wrapper { flex: 1; position: relative; min-height: 100px; border-radius: 4px; background: rgba(15, 23, 42, 0.4); }
  .placeholder { display: flex; align-items: center; justify-content: center; height: 100%; font-size: 0.7rem; color: #475569; font-style: italic; }
  .line-green { border-bottom: 2px solid #10b981; }
  .line-yellow { border-bottom: 2px solid #f59e0b; }
</style>
