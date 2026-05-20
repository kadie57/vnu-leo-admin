<script lang="ts">
  import { Sidebar, SidebarGroup, SidebarItem, SidebarWrapper } from 'flowbite-svelte';
  import { GlobeSolid, GridSolid } from 'flowbite-svelte-icons';
  
  // Import 2 Component
  import OrbitSimulation from '$lib/components/OrbitSimulation.svelte';
  // Thay dòng import cũ thành dòng này
  import NetworkMonitoring from '$lib/components/NetworkMonitoring.svelte';

  let spanClass = 'flex-1 ms-3 whitespace-nowrap';
  
  // Mặc định mở Tab Quỹ đạo (orbit) đầu tiên
  let activeTab = $state('orbit'); 
</script>

<div class="flex h-screen bg-gray-900 text-white overflow-hidden">
  <aside class="w-52 border-r border-gray-700 bg-gray-800 shrink-0">
    <SidebarWrapper class="bg-gray-800">
      <div class="flex items-center justify-center py-4 mb-4 border-b border-gray-700">
        <h2 class="text-xl font-bold text-primary-500">VNU-LEO ADMIN</h2>
      </div>
      <SidebarGroup>
        <SidebarItem label="Quỹ đạo & Phủ sóng" onclick={(any) => activeTab = 'orbit'} class="text-gray-300 hover:text-white cursor-pointer hover:bg-gray-700 {activeTab === 'orbit' ? 'bg-gray-700 text-white' : ''}">
          <svelte:fragment slot="icon">
            <GlobeSolid class="w-5 h-5 transition duration-75 {activeTab === 'orbit' ? 'text-primary-500' : 'text-gray-400'}" />
          </svelte:fragment>
        </SidebarItem>

        <SidebarItem label="Giám sát Core Network" onclick={(any) => activeTab = 'network'} class="text-gray-300 hover:text-white cursor-pointer hover:bg-gray-700 {activeTab === 'network' ? 'bg-gray-700 text-white' : ''}">
          <svelte:fragment slot="icon">
            <GridSolid class="w-5 h-5 transition duration-75 {activeTab === 'network' ? 'text-primary-500' : 'text-gray-400'}" />
          </svelte:fragment>
        </SidebarItem>
      </SidebarGroup>
    </SidebarWrapper>
  </aside>

  <main class="flex-1 p-2 overflow-y-auto">
    <header class="mb-4">
      <h1 class="text-3xl font-bold">
        {#if activeTab === 'orbit'}  Quỹ đạo & Phủ sóng VNU-LEO
        {:else if activeTab === 'network'}  Chuyển giao Gateway (Handover)
        {/if}
      </h1>
    </header>

    {#if activeTab === 'orbit'}
      <OrbitSimulation />
    {:else if activeTab === 'network'}
      <NetworkMonitoring />
    {/if}
  </main>
</div>