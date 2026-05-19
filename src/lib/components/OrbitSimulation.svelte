<script lang="ts">
  import { onMount } from 'svelte';
  import { Button } from 'flowbite-svelte';

  // Quản lý khung chứa địa cầu
  let globeContainer: HTMLElement;
  let globeInstance: any = null;

  // Khai báo các biến cấu hình chuẩn Svelte 5 (Rune $state)
  let satCount = $state(120);
  let altitude = $state(550);
  let inclination = $state(0);
  let gatewayCount = $state(3);

  onMount(async () => {
    // Tải động thư viện để tránh lỗi render phía Server
    const Globe = (await import('globe.gl')).default;

    globeInstance = Globe()(globeContainer)
      .globeImageUrl('//unpkg.com/three-globe/example/img/earth-blue-marble.jpg')
      .backgroundColor('#111827') 
      .pointOfView({ lat: 16.0, lng: 108.0, altitude: 2.2 }); // Tập trung nhìn vào Việt Nam

    // Hàm sinh vùng phủ sóng vệ tinh
    const generateSatellites = () => {
      const sats = [...Array(satCount).keys()].map(() => ({
        lat: (Math.random() - 0.5) * 180,
        lng: (Math.random() - 0.5) * 360,
        alt: altitude / 2000, 
        radius: 6 + Math.random() * 4 
      }));

      globeInstance
        .ringsData(sats)
        .ringLat('lat')
        .ringLng('lng')
        .ringAltitude('alt')
        .ringColor(() => 'rgba(34, 197, 94, 0.4)') // Đổi sang màu xanh lá phủ sóng như ảnh gốc
        .ringMaxRadius('radius')
        .ringPropagationSpeed(0.8)
        .ringRepeatPeriod(800);
    };

    generateSatellites();

    // Lắng nghe sự kiện co giãn màn hình để tính lại kích thước quả cầu
    const resizeObserver = new ResizeObserver(() => {
      if (globeContainer && globeInstance) {
        globeInstance
          .width(globeContainer.clientWidth)
          .height(globeContainer.clientHeight);
      }
    });
    resizeObserver.observe(globeContainer);

    return () => resizeObserver.disconnect();
  });
</script>

<div class="relative w-full h-[calc(100vh-8rem)] overflow-hidden rounded-xl bg-gray-900 border border-gray-800">
  
  <div bind:this={globeContainer} class="absolute top-0 left-0 w-[calc(100%-23rem)] h-full z-0"></div>

  <div class="absolute top-0 right-0 w-86 h-full z-10 p-4 border-l border-gray-800 bg-gray-900/80 backdrop-blur-md flex flex-col justify-between">
    <div class="space-y-6">
      <div class="space-y-2">
        <div class="flex justify-between items-center">
          <label for="satCount" class="text-sm font-medium text-gray-300">Số lượng Vệ tinh</label>
          <span class="bg-gray-800/80 border border-gray-700 text-gray-300 px-2 py-0.5 rounded text-xs font-mono w-12 text-center">{satCount}</span>
        </div>
        <input id="satCount" type="range" min="6" max="120" bind:value={satCount} class="w-full h-1 bg-gray-700 rounded-lg cursor-pointer accent-amber-500" />
        <div class="flex justify-between text-[10px] text-gray-500 font-mono">
          <span>6</span>
          <span>120</span>
        </div>
      </div>

      <div class="space-y-2">
        <div class="flex justify-between items-center">
          <label for="altitude" class="text-sm font-medium text-gray-300">Độ cao Quỹ đạo</label>
          <span class="bg-gray-800/80 border border-gray-700 text-gray-300 px-2 py-0.5 rounded text-xs font-mono w-12 text-center">{altitude}</span>
        </div>
        <input id="altitude" type="range" min="300" max="1200" bind:value={altitude} class="w-full h-1 bg-gray-700 rounded-lg cursor-pointer accent-amber-500"/>
        <div class="flex justify-between text-[10px] text-gray-500 font-mono">
          <span>550</span>
          <span>550 km</span>
        </div>
      </div>

      <div class="space-y-2">
        <div class="flex justify-between items-center">
          <label for="inclination" class="text-sm font-medium text-gray-300">Độ nghiêng</label>
          <span class="bg-gray-800/80 border border-gray-700 text-gray-300 px-2 py-0.5 rounded text-xs font-mono w-12 text-center">{inclination}</span>
        </div>
        <input id="inclination" type="range" min="-20" max="70" bind:value={inclination} class="w-full h-1 bg-gray-700 rounded-lg cursor-pointer accent-amber-500" />
        <div class="flex justify-between text-[10px] text-gray-500 font-mono">
          <span>-20°</span>
          <span>70°</span>
        </div>
      </div>

      <div class="space-y-2">
        <div class="flex justify-between items-center">
          <label for="gatewayCount" class="text-sm font-medium text-gray-300">Số lượng Trạm Gateway</label>
          <span class="bg-gray-800/80 border border-gray-700 text-gray-300 px-2 py-0.5 rounded text-xs font-mono w-12 text-center">{gatewayCount}</span>
        </div>
        <input id="gatewayCount" type="range" min="1" max="10" bind:value={gatewayCount} class="w-full h-1 bg-gray-700 rounded-lg cursor-pointer accent-amber-500" />
        <div class="flex justify-between text-[10px] text-gray-500 font-mono">
          <span>1</span>
          <span>10</span>
        </div>
      </div>
    </div>

    <div class="space-y-2 pt-4 border-t border-gray-800">
      <Button class="w-full bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-500 hover:to-amber-600 text-gray-900 font-semibold text-sm py-2 rounded-lg shadow-md transition duration-200">
        Bắt đầu Mô phỏng
      </Button>
      <button class="w-full bg-transparent border border-gray-700 text-gray-300 hover:bg-gray-800/50 hover:text-white font-medium text-sm py-2 rounded-lg transition duration-200">
        Tạm dừng
      </button>
      <button class="w-full bg-transparent border border-gray-700 text-gray-300 hover:bg-gray-800/50 hover:text-white font-medium text-sm py-2 rounded-lg transition duration-200">
        Đặt lại
      </button>
      <button class="w-full bg-transparent border border-gray-700 text-gray-300 hover:bg-gray-800/50 hover:text-white font-medium text-sm py-2 rounded-lg transition duration-200">
        Đề xuất Cấu hình
      </button>
    </div>
  </div>

  <div class="absolute bottom-4 left-4 w-[calc(100%-25rem)] z-10">
    <div class="grid grid-cols-4 gap-4">
      <div class="bg-gray-800/60 backdrop-blur-sm border border-gray-700 p-3 rounded-xl text-center">
        <p class="text-[11px] text-gray-400 uppercase tracking-wider">Tỷ lệ Phủ sóng (Việt Nam)</p>
        <p class="text-2xl font-bold text-white mt-1">99.8%</p>
      </div>
      <div class="bg-gray-800/60 backdrop-blur-sm border border-gray-700 p-3 rounded-xl text-center">
        <p class="text-[11px] text-gray-400 uppercase tracking-wider">Độ trễ Trung bình</p>
        <p class="text-2xl font-bold text-amber-400 mt-1">25ms</p>
      </div>
      <div class="bg-gray-800/60 backdrop-blur-sm border border-gray-700 p-3 rounded-xl text-center">
        <p class="text-[11px] text-gray-400 uppercase tracking-wider">Số lượng Vệ tinh Tối thiểu</p>
        <p class="text-2xl font-bold text-white mt-1">120</p>
      </div>
      <div class="bg-gray-800/60 backdrop-blur-sm border border-gray-700 p-3 rounded-xl text-center">
        <p class="text-[11px] text-gray-400 uppercase tracking-wider">Băng thông Ước tính</p>
        <p class="text-2xl font-bold text-white mt-1">15 Gbps</p>
      </div>
    </div>
  </div>

</div>