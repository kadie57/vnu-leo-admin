<script lang="ts">
  import { satelliteData } from '$lib/store';

  // Lấy danh sách Gateway panel từ WebSocket (nếu chưa có API đổ về thì dùng mảng rỗng)
  let gateways = $derived($satelliteData.gateways || []);
</script>

<div class="panel-header">
  <h3>GATEWAY STATIONS</h3>
</div>

<div class="gateway-list">
  {#if gateways.length === 0}
    <div style="color: #64748b; font-size: 0.8rem; text-align: center; margin-top: 1rem;">Đang chờ dữ liệu từ Server...</div>
  {/if}
  {#each gateways as gw}
    <div class="gateway-card">
      
      <div class="card-header">
        <h4 style:color={gw.titleColor}>Gateway {gw.city}</h4>
        <div class="status-indicator">
          <span class="status-dot" style:background-color={gw.statusColor} style:box-shadow="0 0 5px {gw.statusColor}"></span>
          <span style:color={gw.statusColor} style:font-weight="600" style:font-size="0.75rem">{gw.status}</span>
        </div>
      </div>

      <div class="card-body">
        
        <div class="dish-container">
          <img src={gw.imgSrc} alt="Satellite Dish {gw.city}" class="dish-image" />
        </div>

        <div class="gw-details">
          <div class="detail-row">
            <span class="label">Đang theo dõi</span>
            <span class="value">{gw.tracking}</span>
          </div>
          <div class="detail-row">
            <span class="label">Vị trí</span>
            <span class="value">{gw.lat}</span>
          </div>
          <div class="detail-row">
            <span class="label">Elevation</span>
            <span class="value">{gw.elevation}</span>
          </div>
          <div class="detail-row">
            <span class="label">C/N</span>
            <div class="cn-value-group">
              <span class="value" style="width: 70px;">{gw.cn !== '0' ? gw.cn + ' dB-Hz' : '—'}</span>
              {#if gw.cn !== '0'}
                <div class="progress-bg">
                  <div class="progress-fill" style:width="{(parseFloat(gw.cn) / 30) * 100}%" style:background-color={gw.statusColor}></div>
                </div>
              {/if}
            </div>
          </div>
          <div class="detail-row">
            <span class="label">Trạng thái link</span>
            <span class="value" style:color={gw.statusColor}>{gw.linkStatus}</span>
          </div>
          <div class="detail-row">
            <span class="label">Phiên phục vụ</span>
            <span class="value" style:color={gw.sessionColor}>{gw.session}</span>
          </div>
        </div>

      </div>
    </div>
  {/each}
</div>

<style>
  .panel-header h3 {
    font-size: 0.75rem; /* Thu nhỏ tiêu đề panel */
    color: #cbd5e1;
    margin: 0 0 0.2rem 0; /* Đẩy sát danh sách lên trên */
    font-weight: 600;
    letter-spacing: 0.5px;
  }

  .gateway-list {
    display: flex;
    flex-direction: column;
    gap: 0.3rem; /* Thu nhỏ tối đa khoảng cách giữa các card */
    overflow-y: hidden;
    height: 100%;
  }

  .gateway-card {
    background-color: #0d1424;
    border: 1px solid #1e293b;
    border-radius: 6px;
    padding: 0.3rem 0.5rem; /* Giảm padding bên trong card xuống mức tối thiểu */
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.15rem; /* Ép sát phần đầu và phần thân card */
  }

  .card-header h4 {
    margin: 0;
    font-size: 0.75rem; /* Hạ size chữ tên trạm */
    font-weight: 500;
  }

  .status-indicator {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .status-dot {
    width: 5px;
    height: 5px;
    border-radius: 50%;
  }

  .card-body {
    display: flex;
    gap: 0.5rem; /* Thu hẹp khoảng cách giữa ảnh và text thông số */
    align-items: center;
  }

  /* Thu nhỏ hẳn ảnh chảo để giải phóng không gian chiều dọc */
  .dish-container {
    width: 100px;
    height: 100px;
    flex-shrink: 0;
  }

  .dish-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 4px;
  }

  /* Cấu hình lại Grid để phần thông tin vẫn nằm gọn bên cạnh */
  .gw-details {
    flex: 1;
    display: grid;
    /* Cột label tăng lên 85px để chữ không bị ngắt quãng */
    grid-template-columns: 85px 1fr; 
    column-gap: 8px;
    row-gap: 2px;
    font-size: 0.65rem; /* Tăng nhẹ font size để dễ đọc hơn */
    align-items: center;
    min-width: 0; 
  }

  .label {
    color: #94a3b8;
    white-space: nowrap;
    /* Căn phải cho nhãn để tạo "khoảng trống" tự nhiên với giá trị */
    text-align: right; 
  }

  .value {
    color: #e2e8f0;
    text-align: left;
    white-space: nowrap; 
    overflow: hidden;
    text-overflow: ellipsis;
    /* Thêm một chút padding trái để giá trị không dính sát nhãn */
    padding-left: 5px; 
  }

  .detail-row {
    display: contents;
  }

  .label {
    color: #94a3b8;
    white-space: nowrap;
  }

  .value {
    color: #e2e8f0;
    text-align: left;
    white-space: nowrap; 
    overflow: hidden;
    text-overflow: ellipsis; /* Nếu tọa độ quá dài vẫn sẽ tự cắt bằng dấu ... thay vì làm tràn khung */
  }

  .cn-value-group {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .progress-bg {
    width: 35px; /* Thu hẹp thanh tiến trình */
    height: 3px; /* Làm thanh mảnh hơn */
    background-color: #334155;
    border-radius: 1.5px;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    border-radius: 1.5px;
  }
</style>