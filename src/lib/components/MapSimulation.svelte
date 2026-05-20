<svelte:options runes={false} />

<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';

  type HandoverPhase = 'idle' | 'running' | 'error' | 'success';

  type SatelliteSpec = {
    id: string;
    orbitX: number;
    orbitY: number;
    phase: number;
    rate: number;
    driftX: number;
    driftY: number;
  };

  type SatellitePosition = SatelliteSpec & {
    x: number;
    y: number;
  };

  type GatewaySpec = {
    id: string;
    name: string;
    x: number;
    y: number;
    coverageRadius: number;
  };

  type Connection = {
    from: string;
    to: string;
    type: 'directed' | 'dashed' | 'handover';
  };

  export let selectedSatelliteId = 'LEO-3';
  export let handoverPhase: HandoverPhase = 'idle';
  export let zoom = 1;
  export let paused = false;
  export let speed = 1;
  export let handoverTargetSatelliteId = 'LEO-3';

  const dispatch = createEventDispatcher<{
    satelliteSelect: { satelliteId: string };
    autoHandover: { satelliteId: string };
  }>();

  const gateways: GatewaySpec[] = [
    { id: 'hn', name: 'Gateway Hà Nội', x: 380, y: 130, coverageRadius: 62 },
    { id: 'dn', name: 'Gateway Đà Nẵng', x: 420, y: 280, coverageRadius: 70 },
    { id: 'hcm', name: 'Gateway TP.HCM', x: 360, y: 440, coverageRadius: 64 }
  ];

  const satelliteSpecs: SatelliteSpec[] = [
    { id: 'LEO-1', orbitX: 150, orbitY: 200, phase: 0.2, rate: 0.9, driftX: 34, driftY: 18 },
    { id: 'LEO-2', orbitX: 300, orbitY: 100, phase: 1.4, rate: 1.15, driftX: 28, driftY: 22 },
    { id: 'LEO-3', orbitX: 320, orbitY: 250, phase: 2.2, rate: 0.8, driftX: 64, driftY: 42 },
    { id: 'LEO-4', orbitX: 650, orbitY: 120, phase: 0.7, rate: 1.05, driftX: 30, driftY: 20 },
    { id: 'LEO-5', orbitX: 750, orbitY: 220, phase: 1.9, rate: 0.88, driftX: 26, driftY: 16 }
  ];

  const connections: Connection[] = [
    { from: 'LEO-1', to: 'LEO-2', type: 'directed' },
    { from: 'LEO-1', to: 'LEO-3', type: 'directed' },
    { from: 'LEO-2', to: 'hn', type: 'directed' },
    { from: 'LEO-3', to: 'dn', type: 'handover' },
    { from: 'LEO-3', to: 'hcm', type: 'dashed' },
    { from: 'LEO-2', to: 'LEO-4', type: 'directed' },
    { from: 'LEO-4', to: 'LEO-5', type: 'directed' }
  ];

  let animationTime = 0;
  let currentPositions: SatellitePosition[] = [];
  let frameId = 0;
  let lastFrameTime = 0;
  let autoHandoverLatched = false;

  function getOrbitPosition(spec: SatelliteSpec, time: number) {
    const angularTime = time * spec.rate;
    return {
      x: spec.orbitX + Math.cos(angularTime + spec.phase) * spec.driftX,
      y: spec.orbitY + Math.sin(angularTime * 1.18 + spec.phase) * spec.driftY
    };
  }

  function updatePositions() {
    currentPositions = satelliteSpecs.map((spec) => ({
      ...spec,
      ...getOrbitPosition(spec, animationTime)
    }));
  }

  function distance(x1: number, y1: number, x2: number, y2: number) {
    return Math.hypot(x1 - x2, y1 - y2);
  }

  function getNodeCoords(id: string) {
    const satellite = currentPositions.find((item) => item.id === id);
    if (satellite) return { x: satellite.x, y: satellite.y };

    const gateway = gateways.find((item) => item.id === id);
    if (gateway) return { x: gateway.x, y: gateway.y };

    return { x: 0, y: 0 };
  }

  function getGateway(id: string) {
    return gateways.find((gateway) => gateway.id === id);
  }

  function getSelectedSatellite() {
    return currentPositions.find((satellite) => satellite.id === selectedSatelliteId) ?? currentPositions[0];
  }

  let selectedSatellite: SatellitePosition | undefined;
  let selectedTelemetry: { signalDb: string; latencyMs: string; elevationAngle: string } | null = null;

  function getTelemetry(position: SatellitePosition) {
    const dnGateway = getGateway('dn');
    const distanceToDn = dnGateway ? distance(position.x, position.y, dnGateway.x, dnGateway.y) : 0;
    const signalDb = Math.max(-121, -52 - distanceToDn / 4.1 + Math.sin(animationTime * 2.2 + position.phase) * 4.5);
    const latencyMs = Math.max(18, 28 + distanceToDn / 16 + Math.cos(animationTime * 1.7 + position.phase) * 3.2);
    const elevationAngle = Math.max(4, 90 - distanceToDn / 9.5);

    return {
      signalDb: signalDb.toFixed(1),
      latencyMs: latencyMs.toFixed(0),
      elevationAngle: elevationAngle.toFixed(0)
    };
  }

  function isHandoverGateway(id: string) {
    return id === 'dn';
  }

  function selectSatellite(satelliteId: string) {
    selectedSatelliteId = satelliteId;
    dispatch('satelliteSelect', { satelliteId });
  }

  function isHandingOver() {
    return handoverPhase === 'running' || handoverPhase === 'error' || handoverPhase === 'success';
  }

  function checkAutoHandover() {
    const target = currentPositions.find((satellite) => satellite.id === handoverTargetSatelliteId);
    const dnGateway = getGateway('dn');

    if (!target || !dnGateway) return;

    const insideCoverage = distance(target.x, target.y, dnGateway.x, dnGateway.y) <= dnGateway.coverageRadius;

    if (insideCoverage && !autoHandoverLatched) {
      autoHandoverLatched = true;
      dispatch('autoHandover', { satelliteId: target.id });
    }

    if (!insideCoverage) {
      autoHandoverLatched = false;
    }
  }

  $: updatePositions();
  $: if (selectedSatelliteId && currentPositions.length) {
    selectedSatelliteId = currentPositions.some((satellite) => satellite.id === selectedSatelliteId)
      ? selectedSatelliteId
      : currentPositions[0].id;
  }

  $: selectedSatellite = getSelectedSatellite();
  $: selectedTelemetry = selectedSatellite ? getTelemetry(selectedSatellite) : null;

  onMount(() => {
    const tick = (timestamp: number) => {
      if (!lastFrameTime) {
        lastFrameTime = timestamp;
      }

      const deltaSeconds = (timestamp - lastFrameTime) / 1000;
      lastFrameTime = timestamp;

      if (!paused) {
        animationTime += deltaSeconds * speed;
        updatePositions();
        checkAutoHandover();
      }

      frameId = requestAnimationFrame(tick);
    };

    frameId = requestAnimationFrame(tick);

    return () => {
      cancelAnimationFrame(frameId);
    };
  });
</script>

<div class="map-container">
  <svg
    viewBox="0 0 800 600"
    width="100%"
    height="100%"
    preserveAspectRatio="xMidYMid meet"
    style={`transform: scale(${zoom}); transform-origin: center center;`}
  >
    <defs>
      <marker id="arrow" viewBox="0 0 10 10" refX="18" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1 L 10 5 L 0 9 z" fill="#64748b" />
      </marker>
      <marker id="arrow-green" viewBox="0 0 10 10" refX="18" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
        <path d="M 0 1 L 10 5 L 0 9 z" fill="#22c55e" />
      </marker>
    </defs>

    <image href="/vietnam.svg" x="250" y="40" width="350" height="520" opacity="0.85" />

    {#each connections as conn}
      <line
        x1={getNodeCoords(conn.from).x}
        y1={getNodeCoords(conn.from).y}
        x2={getNodeCoords(conn.to).x}
        y2={getNodeCoords(conn.to).y}
        class="line-base"
        class:link-dashed={conn.type === 'dashed' || (conn.type === 'handover' && handoverPhase === 'idle')}
        class:link-handover={conn.type === 'handover' && handoverPhase === 'running'}
        class:link-error={conn.type === 'handover' && handoverPhase === 'error'}
        marker-end={conn.type === 'handover' && handoverPhase === 'running'
          ? 'url(#arrow-green)'
          : conn.type === 'directed'
            ? 'url(#arrow)'
            : ''}
      />
    {/each}

    {#each gateways as gw}
      <g>
        {#if isHandoverGateway(gw.id) && isHandingOver()}
          <circle cx={gw.x} cy={gw.y} r={gw.coverageRadius} class:coverage-circle-active={handoverPhase === 'running'} class:coverage-circle-error={handoverPhase === 'error'} class="coverage-circle" />
          <g class:handover-pulse={handoverPhase === 'running'} class:handover-pulse-error={handoverPhase === 'error'} transform={`translate(${gw.x + 14}, ${gw.y + 14})`}>
            <rect x="0" y="0" width="126" height="18" rx="3" fill={handoverPhase === 'error' ? '#ef4444' : '#fde047'} />
            <text x="6" y="12" fill={handoverPhase === 'error' ? '#ffffff' : '#000000'} font-size="9" font-weight="bold" font-family="sans-serif">
              {handoverPhase === 'error' ? 'Handover failed' : handoverPhase === 'success' ? 'Handover complete' : 'Handover in progress'}
            </text>
          </g>
        {/if}

        <g stroke="#cbd5e1" stroke-width="1.5" fill="none" transform={`translate(${gw.x - 10}, ${gw.y - 15})`}>
          <polygon points="10,0 3,25 17,25" stroke-width="1.5" />
          <line x1="10" y1="0" x2="10" y2="25" />
          <circle cx="10" cy="0" r="2" fill="#cbd5e1" />
          <path d="M 6,5 A 5,5 0 0,1 14,5" />
          <path d="M 3,9 A 9,9 0 0,1 17,9" />
        </g>

        <text x={gw.x} y={gw.y + 24} text-anchor="middle" class="label-text">{gw.name}</text>
      </g>
    {/each}

    {#each currentPositions as sat}
      <g
        class="satellite-node"
        role="button"
        tabindex="0"
        aria-label={`Chọn vệ tinh ${sat.id}`}
        on:click={() => selectSatellite(sat.id)}
        on:keydown={(event) => {
          if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            selectSatellite(sat.id);
          }
        }}
      >
        <g transform={`translate(${sat.x}, ${sat.y})`}>
          <polygon points="0,-6 7,0 0,6 -7,0" fill={sat.id === selectedSatelliteId ? '#f97316' : '#38bdf8'} stroke="#ffffff" stroke-width="1" />
          <rect x="-16" y="-2" width="8" height="4" fill="#cbd5e1" stroke="#64748b" stroke-width="0.5" />
          <rect x="8" y="-2" width="8" height="4" fill="#cbd5e1" stroke="#64748b" stroke-width="0.5" />
          <line x1="-8" y1="0" x2="-6" y2="0" stroke="#fff" />
          <line x1="6" y1="0" x2="8" y2="0" stroke="#fff" />
        </g>
        <circle cx={sat.x} cy={sat.y} r="12" class:node-ring={sat.id === selectedSatelliteId} />
        <text x={sat.x} y={sat.y + 18} text-anchor="middle" class="label-text">{sat.id}</text>

        {#if sat.id === selectedSatelliteId && selectedTelemetry}
          <g transform={`translate(${sat.x + 18}, ${sat.y - 66})`}>
            <rect x="0" y="0" width="148" height="76" rx="8" class="telemetry-card" />
            <text x="10" y="16" class="telemetry-title">Live Telemetry</text>
            <text x="10" y="34" class="telemetry-text">Signal: {selectedTelemetry.signalDb} dB</text>
            <text x="10" y="48" class="telemetry-text">Latency: {selectedTelemetry.latencyMs} ms</text>
            <text x="10" y="62" class="telemetry-text">Elevation: {selectedTelemetry.elevationAngle}°</text>
          </g>
        {/if}
      </g>
    {/each}
  </svg>
</div>

<style>
  .map-container {
    width: 100%;
    height: 100%;
    background: radial-gradient(circle at top, #0f2747 0%, #08111f 42%, #030712 100%);
    position: relative;
    overflow: hidden;
    max-width: 100%
  }

  .satellite-node {
    cursor: pointer;
  }

  .line-base {
    stroke-width: 1.2;
    fill: none;
  }

  .link-dashed {
    stroke: #475569;
    stroke-dasharray: 4;
  }

  .link-handover {
    stroke: #22c55e;
    stroke-width: 2.8;
    stroke-dasharray: 0;
    animation: linkPulse 1s ease-in-out infinite;
  }

  .link-error {
    stroke: #ef4444;
    stroke-width: 2.8;
    stroke-dasharray: 0;
  }

  .label-text {
    fill: #94a3b8;
    font-size: 10px;
    font-family: sans-serif;
  }

  .coverage-circle {
    fill: rgba(234, 179, 8, 0.1);
    stroke-width: 1;
    stroke-dasharray: 3;
  }

  .coverage-circle-active {
    stroke: #eab308;
    animation: circleGlow 1.2s ease-in-out infinite;
  }

  .coverage-circle-error {
    stroke: #ef4444;
  }

  .handover-pulse {
    animation: handoverPulse 1s ease-in-out infinite;
  }

  .handover-pulse-error {
    animation: handoverPulseError 0.9s ease-in-out infinite;
  }

  .node-ring {
    fill: rgba(249, 115, 22, 0.14);
    stroke: #f97316;
    stroke-dasharray: 2;
  }

  .telemetry-card {
    fill: rgba(15, 23, 42, 0.94);
    stroke: rgba(148, 163, 184, 0.35);
    stroke-width: 1;
    filter: drop-shadow(0 10px 24px rgba(0, 0, 0, 0.25));
  }

  .telemetry-title {
    fill: #f8fafc;
    font-size: 10px;
    font-weight: 700;
    font-family: sans-serif;
  }

  .telemetry-text {
    fill: #cbd5e1;
    font-size: 9px;
    font-family: sans-serif;
  }

  @keyframes linkPulse {
    0%, 100% {
      opacity: 0.5;
    }
    50% {
      opacity: 1;
    }
  }

  @keyframes circleGlow {
    0%, 100% {
      opacity: 0.5;
    }
    50% {
      opacity: 1;
    }
  }

  @keyframes handoverPulse {
    0%, 100% {
      transform: translate(0, 0);
      opacity: 0.78;
    }
    50% {
      transform: translate(0, -1px);
      opacity: 1;
    }
  }

  @keyframes handoverPulseError {
    0%, 100% {
      opacity: 0.8;
    }
    50% {
      opacity: 1;
    }
  }
</style>