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

  // Đăng ký các thành phần của Chart.js
  ChartJS.register(Title, Tooltip, Legend, LineElement, LinearScale, PointElement, CategoryScale);

  // Dữ liệu giả lập cho biểu đồ C/N
  const cnData = {
    labels: ['10:20', '10:21', '10:22', '10:23', '10:24', '10:25'],
    datasets: [
      {
        label: 'C/N (dB-Hz)',
        data: [18, 19.5, 20.1, 19.8, 18.5, 20.2],
        borderColor: '#10b981', // Màu xanh lá giống viền
        backgroundColor: 'rgba(16, 185, 129, 0.2)',
        borderWidth: 2,
        tension: 0.4, // Làm cong đường line
        pointRadius: 0, // Ẩn các chấm tròn cho mượt
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
    },
    scales: {
      x: { grid: { color: '#1e293b' }, ticks: { color: '#64748b', font: { size: 10 } } },
      y: { grid: { color: '#1e293b' }, ticks: { color: '#64748b', font: { size: 10 } }, min: 10, max: 30 },
    },
  };
</script>

<div class="charts-container">
  <h3>BIỂU ĐỒ HIỆU SUẤT (TỚI GATEWAY HÀ NỘI)</h3>
  
  <div class="chart-block">
    <div class="chart-title">C/N (dB-Hz)</div>
    <div class="chart-wrapper line-green">
      <Line data={cnData} options={chartOptions} />
    </div>
  </div>

  <div class="chart-block">
    <div class="chart-title">Độ trễ (ms)</div>
    <div class="chart-wrapper line-yellow">
      <span class="mock-text">[ Đang tải dữ liệu Độ trễ... ]</span>
    </div>
  </div>

  <div class="chart-block">
    <div class="chart-title">Throughput (Mbps)</div>
    <div class="chart-wrapper line-blue">
      <span class="mock-text">[ Đang tải dữ liệu Throughput... ]</span>
    </div>
  </div>
</div>

<style>
  .charts-container { display: flex; flex-direction: column; gap: 1rem; height: 100%; }
  h3 { font-size: 0.8rem; color: #cbd5e1; margin: 0; font-weight: 600; }
  
  .chart-block { flex: 1; display: flex; flex-direction: column; gap: 0.5rem; background: #0d1424; border: 1px solid #1e293b; padding: 0.75rem; border-radius: 6px; }
  .chart-title { font-size: 0.75rem; color: #94a3b8; }
  
  .chart-wrapper { 
    flex: 1; 
    position: relative; /* Bắt buộc để Chart.js scale đúng */
    border-radius: 4px; 
    background: rgba(15, 23, 42, 0.4); 
  }
  
  .mock-text { display: flex; justify-content: center; align-items: center; height: 100%; font-size: 0.7rem; color: #475569; font-style: italic; }
  
  .line-green { border-bottom: 2px solid #10b981; }
  .line-yellow { border-bottom: 2px solid #f59e0b; }
  .line-blue { border-bottom: 2px solid #3b82f6; }
</style>