<script lang="ts">
  import { Card, Badge, Table, TableHead, TableHeadCell, TableBody, TableBodyRow, TableBodyCell } from 'flowbite-svelte';
  import { ArrowRightOutline } from 'flowbite-svelte-icons';

  // Dữ liệu giả lập (Sau này bạn dùng WebSocket đẩy từ Backend lên)
  let gateways = [
    { name: 'Hà Nội Node', status: 'ALIVE', traffic: '120 Gbps', color: 'green' },
    { name: 'Đà Nẵng Node', status: 'HANDOVER', traffic: '85 Gbps', color: 'yellow' },
    { name: 'TP.HCM Node', status: 'ALIVE', traffic: '150 Gbps', color: 'green' }
  ];

  let handoverLogs = [
    { time: '10:45:02', sat: 'LEO-12', from: 'Đà Nẵng', to: 'TP.HCM', status: 'Thành công' },
    { time: '10:42:15', sat: 'LEO-08', from: 'Hà Nội', to: 'Đà Nẵng', status: 'Đang xử lý...' },
  ];
</script>

<div class="space-y-6">
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
    {#each gateways as gw}
      <Card class="bg-gray-800 border-gray-700 max-w-none">
        <div class="flex justify-between items-center mb-4">
          <h5 class="text-xl font-bold leading-none text-white">{gw.name}</h5>
          {#if gw.status === 'ALIVE'}
            <Badge color="green" class="animate-pulse">ALIVE</Badge>
          {:else}
            <Badge color="yellow">HANDOVER</Badge>
          {/if}
        </div>
        <p class="text-gray-400 text-sm">Lưu lượng hiện tại</p>
        <p class="text-3xl font-bold text-white">{gw.traffic}</p>
      </Card>
    {/each}
  </div>

  <Card class="bg-gray-800 border-gray-700 max-w-none">
    <h5 class="text-lg font-bold text-white mb-4">Lịch sử Chuyển giao (Handover Log)</h5>
    <Table hoverable={true} class="text-gray-400">
      <TableHead class="bg-gray-700 text-gray-300">
        <TableHeadCell>Thời gian</TableHeadCell>
        <TableHeadCell>Vệ tinh</TableHeadCell>
        <TableHeadCell>Tiến trình</TableHeadCell>
        <TableHeadCell>Trạng thái</TableHeadCell>
      </TableHead>
      <TableBody>
        {#each handoverLogs as log}
          <TableBodyRow class="border-b border-gray-700 hover:bg-gray-600">
            <TableBodyCell>{log.time}</TableBodyCell>
            <TableBodyCell class="font-medium text-white">{log.sat}</TableBodyCell>
            <TableBodyCell>
              <div class="flex items-center gap-2">
                {log.from} <ArrowRightOutline class="w-4 h-4 text-primary-500" /> {log.to}
              </div>
            </TableBodyCell>
            <TableBodyCell>
              <span class={log.status === 'Thành công' ? 'text-green-400' : 'text-yellow-400'}>
                {log.status}
              </span>
            </TableBodyCell>
          </TableBodyRow>
        {/each}
      </TableBody>
    </Table>
  </Card>
</div>