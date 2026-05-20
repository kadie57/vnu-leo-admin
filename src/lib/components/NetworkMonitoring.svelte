<svelte:options runes={false} />

<script lang="ts">
  import { onDestroy, onMount, tick } from 'svelte';
  import MapSimulation from '$lib/components/MapSimulation.svelte';

  type HandoverPhase = 'idle' | 'running' | 'error' | 'success';
  type StepStatus = 'idle' | 'active' | 'done' | 'error';

  const satelliteBaseRows = [
    { id: 'LEO-1', status: 'online', state: 'Đang giám sát' },
    { id: 'LEO-2', status: 'warning', state: 'Chờ handover' },
    { id: 'LEO-3', status: 'online', state: 'Được theo dõi' },
    { id: 'LEO-4', status: 'online', state: 'Đang giám sát' },
    { id: 'LEO-5', status: 'warning', state: 'Chờ handover' },
    { id: 'LEO-6', status: 'warning', state: 'Dự phòng' }
  ];

  const scenarios = ['Kịch bản Chuyển giao 1', 'Kịch bản Chuyển giao 2', 'Kịch bản Chuyển giao 3'];
  let activeScenarioIndex = 0;
  const processStepNames = ['Đánh giá tín hiệu', 'Bắt đầu Chuyển giao', 'Chuẩn bị Gateway', 'Xác nhận Chuyển giao', 'Hoàn tất'];

  let selectedSatelliteId = 'LEO-3';
  let handoverPhase: HandoverPhase = 'idle';
  let mapZoom = 1;
  let simulationSpeed = 1;
  let isPaused = false;

  let processSteps = processStepNames.map((name, index) => ({
    name,
    status: index === 0 ? 'active' : 'idle'
  })) as Array<{ name: string; status: StepStatus }>;

  let successHistory = Array.from({ length: 12 }, () => 97.5);
  let currentSuccessRate = 97.5;
  let successPenalty = 0;
  let failureStepIndex: number | null = null;
  let sequenceActive = false;
  let shouldFailCurrentRun = true;
  let rowRefs: Array<HTMLTableRowElement | null> = [];
  let processTimers: ReturnType<typeof setTimeout>[] = [];
  let chartTimer: ReturnType<typeof setInterval> | undefined;

  function clearProcessTimers() {
    for (const timer of processTimers) {
      clearTimeout(timer);
    }

    processTimers = [];
  }

  function setProcessStep(index: number, status: StepStatus) {
    processSteps = processSteps.map((step, stepIndex) => (stepIndex === index ? { ...step, status } : step));
  }

  function setAllSteps(status: StepStatus) {
    processSteps = processSteps.map((step) => ({ ...step, status }));
  }

  function startMetricLoop() {
    if (chartTimer) {
      clearInterval(chartTimer);
    }

    chartTimer = setInterval(() => {
      const oscillation = Math.sin(Date.now() / 1800) * 0.45 + Math.cos(Date.now() / 4200) * 0.2;
      successPenalty = Math.max(0, successPenalty - 0.22);
      currentSuccessRate = Math.max(92.5, Math.min(99.9, 97.5 + oscillation - successPenalty));
      successHistory = [...successHistory.slice(1), currentSuccessRate];
    }, 1000);
  }

  function beginStep(index: number) {
    if (index >= processStepNames.length) {
      handoverPhase = 'success';
      sequenceActive = false;
      failureStepIndex = null;
      setAllSteps('done');
      successPenalty = Math.min(successPenalty, 0.25);
      return;
    }

    setProcessStep(index, 'active');

    const timeout = setTimeout(() => {
      if (handoverPhase !== 'running') {
        return;
      }

      if (index === 2 && shouldFailCurrentRun) {
        setProcessStep(index, 'error');
        handoverPhase = 'error';
        sequenceActive = false;
        failureStepIndex = index;
        successPenalty = Math.max(successPenalty, 2.9);
        return;
      }

      setProcessStep(index, 'done');
      beginStep(index + 1);
    }, index === 0 ? 900 : 1100);

    processTimers.push(timeout);
  }

  function startHandoverSequence(source: 'auto' | 'manual') {
    if (sequenceActive && handoverPhase === 'running') {
      return;
    }

    clearProcessTimers();
    selectedSatelliteId = 'LEO-3';
    handoverPhase = 'running';
    sequenceActive = true;
    failureStepIndex = null;
    shouldFailCurrentRun = source === 'manual';
    processSteps = processStepNames.map((name, index) => ({
      name,
      status: index === 0 ? 'active' : 'idle'
    }));
    beginStep(0);
  }

  function retryCurrentStep() {
    if (failureStepIndex === null) {
      return;
    }

    clearProcessTimers();
    shouldFailCurrentRun = false;
    handoverPhase = 'running';
    sequenceActive = true;
    setProcessStep(failureStepIndex, 'active');
    beginStep(failureStepIndex);
  }

  function scrollToSelectedSatellite() {
    void tick().then(() => {
      const index = satelliteBaseRows.findIndex((satellite) => satellite.id === selectedSatelliteId);

      if (index >= 0) {
        rowRefs[index]?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    });
  }

  function focusSatellite(id: string) {
    selectedSatelliteId = id;
    scrollToSelectedSatellite();
  }

  function handleSatelliteSelect(event: CustomEvent<{ satelliteId: string }>) {
    selectedSatelliteId = event.detail.satelliteId;
    scrollToSelectedSatellite();
  }

  function handleAutoHandover(event: CustomEvent<{ satelliteId: string }>) {
    selectedSatelliteId = event.detail.satelliteId;
    scrollToSelectedSatellite();
    startHandoverSequence('auto');
  }

  function zoomIn() {
    mapZoom = Math.min(1.8, Number((mapZoom + 0.1).toFixed(2)));
  }

  function zoomOut() {
    mapZoom = Math.max(0.7, Number((mapZoom - 0.1).toFixed(2)));
  }

  function startSimulation() {
    isPaused = false;
  }

  function togglePause() {
    isPaused = !isPaused;
  }

  function exportStatistics() {
    const payload = {
      selectedSatelliteId,
      handoverPhase,
      currentSuccessRate: Number(currentSuccessRate.toFixed(1))
    };

    console.log('Export statistics', payload);
  }

  onMount(() => {
    startMetricLoop();
    scrollToSelectedSatellite();

    return () => {
      if (chartTimer) {
        clearInterval(chartTimer);
      }

      clearProcessTimers();
    };
  });

  onDestroy(() => {
    if (chartTimer) {
      clearInterval(chartTimer);
    }

    clearProcessTimers();
  });
</script>

<div class="dashboard">
  <aside class="sidebar">
    <div class="panel list-panel">
      <div class="panel-header">
        <h2>Danh sách Vệ tinh</h2>
        <span class="focus-pill">Focus: {selectedSatelliteId}</span>
      </div>
      <table>
        <thead>
          <tr><th>Name</th><th>Status</th><th>Trạng thái</th></tr>
        </thead>
        <tbody>
          {#each satelliteBaseRows as sat, index}
            <tr
              bind:this={rowRefs[index]}
              class:active={sat.id === selectedSatelliteId}
              on:click={() => focusSatellite(sat.id)}
            >
              <td>
                <span class="sat-icon">🛰️</span> {sat.id}
              </td>
              <td><span class={`status-dot ${sat.status}`}></span></td>
              <td>{sat.id === selectedSatelliteId ? (handoverPhase === 'running' ? 'Đang handover' : handoverPhase === 'error' ? 'Cần retry' : 'Đang được focus') : sat.state}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>

    <div class="panel scenario-panel">
      <h2>Kịch bản Chuyển giao</h2>
      <p class="subtitle">Chọn kịch bản test cụm với quy trình chuyển giao:</p>
      <ul>
        {#each scenarios as sc, index}
          <li 
            class:active={activeScenarioIndex === index}
            on:click={() => activeScenarioIndex = index}
          >
            {sc}
          </li>
        {/each}
      </ul>
    </div>
  </aside>

  <div class="main-area">
    <div class="panel map-panel">
      <MapSimulation
        bind:selectedSatelliteId
        bind:handoverPhase
        bind:zoom={mapZoom}
        paused={isPaused}
        speed={simulationSpeed}
        handoverTargetSatelliteId="LEO-3"
        on:satelliteSelect={handleSatelliteSelect}
        on:autoHandover={handleAutoHandover}
      />

      <div class="map-controls">
        <div class="control-group left-group">
          <button class="btn btn-simulation" on:click={startSimulation}>{isPaused ? 'Tiếp tục Mô phỏng' : 'Bắt đầu Mô phỏng'}</button>
          <button class="btn btn-toggle" on:click={togglePause}>{isPaused ? 'Resume' : 'Pause'}</button>
          <button class="btn btn-handover" on:click={() => startHandoverSequence('manual')}>Giả lập Chuyển giao</button>
        </div>

        <div class="control-group center-group">
          <button class="zoom-btn" on:click={zoomOut}>−</button>
          <span class="zoom-label">{Math.round(mapZoom * 100)}%</span>
          <button class="zoom-btn" on:click={zoomIn}>+</button>
          <label class="speed-control">
            <span>Tốc độ: {simulationSpeed.toFixed(2)}x</span>
            <input type="range" min="0.25" max="2.5" step="0.05" bind:value={simulationSpeed} />
          </label>
        </div>

        <div class="control-group right-group">
          <button class="btn btn-export" on:click={exportStatistics}>Xuất Thống kê</button>
        </div>
      </div>
    </div>

    <div class="bottom-row">
      <div class="panel chart-panel">
        <div class="panel-header">
          <h2>Tỷ lệ chuyển giao thành công</h2>
          <span class="focus-pill success-pill">{currentSuccessRate.toFixed(1)}%</span>
        </div>
        <div class="chart-container">
          <div class="y-axis">
            <span>100</span><span>95</span><span>90</span><span>85</span><span>80</span><span>75</span>
          </div>
          <div class="chart-area">
            <div class="grid-lines">
              <div class="line"></div><div class="line"></div><div class="line"></div>
              <div class="line"></div><div class="line"></div><div class="line-bottom"></div>
            </div>
            <div class="bars">
              {#each successHistory as point, index}
                <div class="mini-bar" style={`height: ${Math.max(18, point)}%; opacity: ${index === successHistory.length - 1 ? 1 : 0.72};`}>
                  <span>{point.toFixed(1)}%</span>
                </div>
              {/each}
            </div>
          </div>
        </div>
        <div class="x-axis-label">Tỷ lệ chuyển giao thành công thay đổi theo thời gian thực</div>
      </div>

      <div class="panel process-panel">
        <div class="panel-header">
          <h2>Quá trình Chuyển giao Chi tiết: LEO-3 ➔ TP.HCM</h2>
          <span class={`phase-pill phase-${handoverPhase}`}>{handoverPhase === 'idle' ? 'Sẵn sàng' : handoverPhase === 'running' ? 'Đang chạy' : handoverPhase === 'error' ? 'Lỗi' : 'Hoàn tất'}</span>
        </div>
        <div class="flow-wrapper">
          {#each processSteps as step, i}
            <div class={`step-card ${step.status}`}>
              <div class="step-title">{step.name}</div>
              <div class="step-state">
                {step.status === 'idle' ? 'Chờ' : step.status === 'active' ? 'Đang xử lý' : step.status === 'done' ? 'Hoàn tất' : 'Thất bại'}
              </div>
              {#if step.status === 'error'}
                <button class="retry-btn" on:click={retryCurrentStep}>Retry</button>
              {/if}
            </div>
            {#if i < processSteps.length - 1}
              <div class="flow-arrow">➔</div>
            {/if}
          {/each}
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  .dashboard {
    display: flex;
    gap: 16px; /* Nới rộng khoảng cách giữa các cột từ 8px lên 16px */
    padding: 8px; 
    height: 100%;
    overflow: hidden;
    background:
      radial-gradient(circle at top left, rgba(59, 130, 246, 0.12), transparent 28%),
      radial-gradient(circle at bottom right, rgba(249, 115, 22, 0.12), transparent 26%),
      #030712;
  }

  .sidebar {
    width: 250px; /* Bóp nhỏ Sidebar từ 290px xuống 250px để nhường chỗ cho Map */
    display: flex;
    flex-direction: column;
    gap: 16px; /* Nới rộng khoảng cách giữa 2 bảng bên trái */
    overflow: hidden; 
  }

  .main-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 16px; /* Nới rộng khoảng cách giữa Bản đồ và Biểu đồ bên dưới */
    overflow: hidden; 
    min-width: 0; 
  }

  .bottom-row {
    display: flex;
    gap: 16px; /* Khoảng cách giữa Biểu đồ và Flowchart */
    height: 180px; /* Tăng chiều cao thêm 10px để flowchart rộng rãi hơn */
    flex-shrink: 0;
    min-width: 0; 
  }

  .panel {
    background: linear-gradient(180deg, rgba(11, 21, 40, 0.98), rgba(7, 13, 24, 0.98));
    border: 1px solid #1e293b;
    border-radius: 14px;
    padding: 16px; /* Tăng lề bên trong các khối từ 12px lên 16px cho thoáng */
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.28);
  }

  .step-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px; /* Tăng khoảng cách giữa chữ và trạng thái trong flowchart */
    flex: 1; 
    min-width: 90px;
    padding: 14px 10px; /* Nới rộng chiều dọc của các nút Flowchart */
    border-radius: 12px;
    font-size: 11px;
    text-align: center;
    border: 1px solid #334155;
    background: #0f172a;
    color: #cbd5e1;
    transition: all 0.25s ease;
  }

  .panel {
    background: linear-gradient(180deg, rgba(11, 21, 40, 0.98), rgba(7, 13, 24, 0.98));
    border: 1px solid #1e293b;
    border-radius: 14px;
    padding: 12px;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.28);
  }

  .panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    margin-bottom: 10px;
  }

  h2 {
    font-size: 13px;
    margin: 0;
    color: #f8fafc;
    font-weight: 600;
    letter-spacing: 0.2px;
  }

  .focus-pill,
  .phase-pill {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 4px 8px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 700;
    white-space: nowrap;
  }

  .focus-pill {
    background: rgba(15, 23, 42, 0.92);
    color: #cbd5e1;
    border: 1px solid rgba(148, 163, 184, 0.18);
  }

  .success-pill {
    color: #bbf7d0;
    background: rgba(22, 101, 52, 0.34);
    border-color: rgba(34, 197, 94, 0.28);
  }

  .phase-idle {
    color: #cbd5e1;
    background: rgba(51, 65, 85, 0.6);
  }

  .phase-running {
    color: #fde047;
    background: rgba(120, 53, 15, 0.65);
  }

  .phase-error {
    color: #fee2e2;
    background: rgba(127, 29, 29, 0.7);
  }

  .phase-success {
    color: #dcfce7;
    background: rgba(22, 101, 52, 0.7);
  }

  .list-panel {
    flex: 1.8;
    overflow-y: auto;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 11px;
  }

  th {
    background-color: #0f172a;
    padding: 8px 6px;
    text-align: left;
    color: #94a3b8;
    font-weight: 600;
    position: sticky;
    top: 0;
    z-index: 1;
  }

  td {
    padding: 8px 6px;
    border-bottom: 1px solid #1e293b;
    color: #cbd5e1;
  }

  tr {
    cursor: pointer;
    transition: background-color 0.18s ease, transform 0.18s ease;
  }

  tr:hover {
    background-color: rgba(30, 41, 59, 0.5);
  }

  tr.active {
    background: linear-gradient(90deg, rgba(249, 115, 22, 0.2), rgba(30, 41, 59, 0.75));
    color: #f97316;
  }

  .sat-icon {
    font-size: 12px;
  }

  .status-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }

  .status-dot.online {
    background-color: #22c55e;
  }

  .status-dot.warning {
    background-color: #eab308;
  }

  .scenario-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
  }
  
  .scenario-panel ul {
    flex: 1;
    overflow-y: auto;
  }

  .subtitle {
    font-size: 11px;
    color: #94a3b8;
    margin: 0 0 8px 0;
  }

  ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  li {
    padding: 8px;
    margin-bottom: 6px;
    background: #0f172a;
    border-radius: 8px;
    font-size: 11px;
    color: #cbd5e1;
    border: 1px solid #1e293b;
    cursor: pointer; /* Biến con trỏ thành hình bàn tay */
    transition: all 0.2s ease; /* Hiệu ứng chuyển màu mượt mà */
  }

  /* Thêm class này để khi di chuột qua nó hơi sáng lên */
  li:hover:not(.active) {
    background-color: #1e293b;
    border-color: #475569;
  }

  li.active {
    background-color: #78350f;
    border-color: #d97706;
    color: #fde047;
  }

  .map-panel {
    flex: 1;
    position: relative;
    padding: 0;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    min-height: 0px;
  }

  .map-controls {
    position: absolute;
    left: 12px;
    right: 12px;
    bottom: 12px;
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    gap: 10px;
    pointer-events: none;
  }

  .control-group {
    display: flex;
    align-items: center;
    gap: 8px;
    pointer-events: auto;
    background: rgba(15, 23, 42, 0.82);
    border: 1px solid rgba(51, 65, 85, 0.72);
    border-radius: 999px;
    padding: 8px 10px;
    backdrop-filter: blur(8px);
  }

  .left-group,
  .right-group {
    flex-wrap: wrap;
  }

  .center-group {
    min-width: 320px;
    justify-content: center;
    flex: 1;
  }

  .btn,
  .zoom-btn,
  .retry-btn {
    border: none;
    padding: 7px 12px;
    font-size: 11px;
    border-radius: 999px;
    color: white;
    cursor: pointer;
    font-weight: 600;
    transition: transform 0.18s ease, filter 0.18s ease, background-color 0.18s ease;
  }

  .btn:hover,
  .zoom-btn:hover,
  .retry-btn:hover {
    transform: translateY(-1px);
    filter: brightness(1.06);
  }

  .btn-simulation {
    background-color: #15803d;
  }

  .btn-toggle {
    background-color: #334155;
  }

  .btn-handover {
    background-color: #c2410c;
  }

  .btn-export {
    background-color: #1d4ed8;
  }

  .zoom-btn {
    width: 30px;
    height: 30px;
    padding: 0;
    background: #334155;
  }

  .zoom-label {
    font-size: 11px;
    color: #e2e8f0;
    min-width: 44px;
    text-align: center;
  }

  .speed-control {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #cbd5e1;
    font-size: 11px;
    margin-left: 6px;
  }

  .speed-control input {
    width: 160px;
    accent-color: #f97316;
  }

  .chart-panel {
    flex: 1;
    min-width: 300px; /* Đảm bảo đồ thị tối thiểu hiển thị được chữ */
    max-width: 380px; 
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .chart-container {
    display: flex;
    flex: 1;
    min-height: 0; /* Let it shrink if needed */
    position: relative;
    gap: 8px;
  }

  .y-axis {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    font-size: 9px;
    color: #94a3b8;
    text-align: right;
    width: 24px;
    padding-right: 2px;
  }

  .chart-area {
    flex: 1;
    position: relative;
    border-left: 1px solid #475569;
    margin-top: 15px; 
  }

  .grid-lines {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    pointer-events: none;
  }

  .line {
    border-top: 1px dashed rgba(71, 85, 105, 0.3);
    width: 100%;
    height: 0;
  }

  .line-bottom {
    border-top: 1px solid #475569;
    width: 100%;
    height: 0;
  }

  .bars {
    position: absolute;
    inset: 0;
    display: grid;
    grid-template-columns: repeat(12, minmax(0, 1fr));
    align-items: end;
    gap: 6px; 
    padding: 0 6px;
  }

  /* Bo góc cột mềm mại và giảm độ chói */
  .mini-bar {
    position: relative;
    background: linear-gradient(to top, #ea580c, #f97316);
    border-radius: 4px 4px 0 0;
    min-height: 18px;
    transition: height 0.55s ease;
    opacity: 0.7; /* Làm mờ nhẹ các cột cũ */
  }

  /* Làm nổi bật cột cuối cùng (dữ liệu mới nhất) */
  .mini-bar:last-child {
    opacity: 1;
    background: linear-gradient(to top, #ea580c, #fb923c);
    box-shadow: 0 0 8px rgba(249, 115, 22, 0.4);
  }

  /* XOAY NGHIÊNG CHỮ ĐỂ KHÔNG BỊ ĐÈ NHAU */
  .mini-bar span {
    position: absolute;
    top: -20px;
    left: 50%;
    /* Xoay nghiêng góc 60 độ */
    transform: translateX(-50%) rotate(-60deg);
    transform-origin: bottom left;
    font-size: 8.5px;
    color: #94a3b8; /* Chữ màu xám cho các cột cũ đỡ rối */
    white-space: nowrap;
    letter-spacing: 0.5px;
  }

  /* Chữ của cột cuối cùng cho màu xanh sáng để nhấn mạnh */
  .mini-bar:last-child span {
    color: #bbf7d0;
    font-weight: 700;
    font-size: 9.5px;
  }

  .x-axis-label {
    font-size: 10px;
    color: #cbd5e1;
    text-align: center;
    margin-top: 6px;
  }

  .process-panel {
    flex: 2; /* Gấp đôi diện tích tỷ lệ để đủ không gian nằm ngang cho các step */
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .flow-wrapper {
    flex: 1;
    display: flex;
    align-items: center; /* Center items instead of stretch to prevent vertical overflow/distortion */
    justify-content: center;
    gap: 8px;
    padding: 0 10px;
    overflow-x: auto; /* Prevent overflowing out of the frame horizontally */
    min-width: 0; 
  }

  .step-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 6px;
    flex: 1; /* Allow cards to resize equally */
    min-width: 90px;
    padding: 10px 8px;
    border-radius: 12px;
    font-size: 11px;
    text-align: center;
    border: 1px solid #334155;
    background: #0f172a;
    color: #cbd5e1;
    transition: background-color 0.25s ease, border-color 0.25s ease, color 0.25s ease, box-shadow 0.25s ease;
  }

  .step-title {
    font-weight: 700;
  }

  .step-state {
    font-size: 10px;
    color: inherit;
    opacity: 0.88;
  }

  .step-card.idle {
    background: #0f172a;
  }

  .step-card.active {
    background: linear-gradient(180deg, rgba(59, 130, 246, 0.18), rgba(15, 23, 42, 0.98));
    border-color: rgba(59, 130, 246, 0.48);
    color: #dbeafe;
    box-shadow: 0 0 0 1px rgba(59, 130, 246, 0.1), 0 0 24px rgba(59, 130, 246, 0.12);
    animation: glowStep 1.2s ease-in-out infinite;
  }

  .step-card.done {
    background: linear-gradient(180deg, rgba(34, 197, 94, 0.18), rgba(15, 23, 42, 0.98));
    border-color: rgba(34, 197, 94, 0.48);
    color: #dcfce7;
  }

  .step-card.error {
    background: linear-gradient(180deg, rgba(239, 68, 68, 0.2), rgba(15, 23, 42, 0.98));
    border-color: rgba(239, 68, 68, 0.65);
    color: #fee2e2;
    box-shadow: 0 0 0 1px rgba(239, 68, 68, 0.14), 0 0 24px rgba(239, 68, 68, 0.12);
  }

  .retry-btn {
    padding: 6px 10px;
    background: #dc2626;
  }

  .flow-arrow {
    display: flex;
    align-items: center;
    color: #64748b;
    font-size: 12px;
    font-weight: 700;
  }

  @keyframes glowStep {
    0%, 100% {
      filter: brightness(1);
    }
    50% {
      filter: brightness(1.12);
    }
  }
</style>
