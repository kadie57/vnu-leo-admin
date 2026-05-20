<div class="stats-box">
  <h3>TỔNG QUAN HỆ THỐNG</h3>
  <div class="stat-item"><span>Tổng số vệ tinh:</span> <strong>40</strong></div>
  <div class="stat-item"><span>Đang phủ Việt Nam:</span> <strong style="color: #10b981;">12</strong></div>
  <div class="stat-item"><span>Sắp handover:</span> <strong style="color: #f59e0b;">2</strong></div>
</div>

<div class="stats-box">
  <h3>TRẠNG THÁI HỆ THỐNG</h3>
  <div class="stat-item"><span>Tình trạng:</span> <span style="color: #10b981;">Hoạt động bình thường</span></div>
  <div class="stat-item"><span>Độ trễ trung bình:</span> <strong>24 ms</strong></div>
</div>

<style>
  .stats-box {
    background: rgba(30, 41, 59, 0.4);
    border-radius: 6px;
    padding: 0.65rem; /* Vắt kiệt padding để lấy không gian cho chữ */
    border: 1px solid #334155;
    margin-bottom: 1rem;
  }
  
  h3 {
    font-size: 0.7rem; /* Thu nhỏ tiêu đề */
    color: #94a3b8;
    margin-top: 0;
    margin-bottom: 0.75rem;
    border-bottom: 1px solid #334155;
    padding-bottom: 0.4rem;
    white-space: nowrap; /* Cấm rớt dòng */
  }
  
  .stat-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.6rem;
    font-size: 0.7rem; /* Thu nhỏ thông số */
  }

  .stat-item span:first-child {
    white-space: nowrap; /* Cấm rớt dòng phần nhãn (Tình trạng, Độ trễ...) */
  }

  .stat-item strong, 
  .stat-item span:last-child {
    text-align: right;
    white-space: nowrap;
  }
</style>