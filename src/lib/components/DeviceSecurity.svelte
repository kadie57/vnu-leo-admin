<script lang="ts">
  import { Card, Table, TableHead, TableHeadCell, TableBody, TableBodyRow, TableBodyCell, Badge, Button } from 'flowbite-svelte';
  import { ExclamationCircleOutline, CheckCircleOutline } from 'flowbite-svelte-icons';

  let devices = [
    { id: 'R-VNU-001', mac: '00:1B:44:11:3A:B7', type: 'Chính hãng', status: 'Đã cấp phép' },
    { id: 'R-VNU-002', mac: '00:1B:44:22:9C:F1', type: 'Chính hãng', status: 'Đã cấp phép' },
    { id: 'UNKNOWN', mac: 'FA:3C:22:11:00:99', type: 'Nghi ngờ giả mạo', status: 'Từ chối (MAC Spoofing)' },
  ];
</script>

<Card class="bg-gray-800 border-gray-700 max-w-none">
  <div class="flex justify-between items-center mb-6">
    <h5 class="text-xl font-bold text-white flex items-center gap-2">
      <ExclamationCircleOutline class="w-6 h-6 text-red-500" /> Cảnh báo Định danh & Bảo mật
    </h5>
    <Button color="dark" size="sm" class="border border-gray-600">Quét lại mạng</Button>
  </div>

  <Table hoverable={true} class="text-gray-400">
    <TableHead class="bg-gray-700 text-gray-300">
      <TableHeadCell>Device ID</TableHeadCell>
      <TableHeadCell>MAC Address</TableHeadCell>
      <TableHeadCell>Phân loại</TableHeadCell>
      <TableHeadCell>Trạng thái (Provisioning)</TableHeadCell>
      <TableHeadCell>Hành động</TableHeadCell>
    </TableHead>
    <TableBody>
      {#each devices as dev}
        <TableBodyRow class="border-b border-gray-700 hover:bg-gray-600">
          <TableBodyCell class="font-medium text-white">{dev.id}</TableBodyCell>
          <TableBodyCell class="font-mono">{dev.mac}</TableBodyCell>
          <TableBodyCell>
            {#if dev.type === 'Chính hãng'}
              <Badge color="green"><CheckCircleOutline class="w-3 h-3 me-1" /> Hợp lệ</Badge>
            {:else}
              <Badge color="red">Nguy cơ cao</Badge>
            {/if}
          </TableBodyCell>
          <TableBodyCell>
            <span class={dev.status.includes('Từ chối') ? 'text-red-400 font-bold' : 'text-green-400'}>
              {dev.status}
            </span>
          </TableBodyCell>
          <TableBodyCell>
            {#if dev.status.includes('Từ chối')}
              <Button color="red" size="xs">Khóa IP</Button>
            {:else}
              <Button color="light" size="xs" disabled>Đã duyệt</Button>
            {/if}
          </TableBodyCell>
        </TableBodyRow>
      {/each}
    </TableBody>
  </Table>
</Card>