# mini-AI-Cluster
Dưới đây là phần mô tả chi tiết của đề tài **STT 14: Nghiên cứu, triển khai và quản trị AI Cluster sử dụng DGX H200 SuperPOD và Base Command Manager** từ tài liệu của đơn vị:

> **Mô tả bài toán:**
> "Hiện nay các hệ thống AI Factory quy mô lớn yêu cầu hạ tầng GPU hiệu năng cao nhằm phục vụ huấn luyện và triển khai mô hình AI thế hệ mới. Hệ thống DGX H200 SuperPOD của NVIDIA kết hợp với Base Command Manager (BCM) cung cấp khả năng xây dựng và quản trị AI cluster ở quy mô enterprise.
> Tại phòng lab, sinh viên được tiếp cận trực tiếp hệ thống GPU server H200/B200, DGX SuperPOD và nền tảng BCM để nghiên cứu kiến trúc AI Infrastructure thực tế. Đề tài tập trung theo hướng nghiên cứu ứng dụng và thực hành triển khai AI cluster, giúp sinh viên hiểu quy trình vận hành AI Factory từ hạ tầng phần cứng đến orchestration và monitoring."

---

### 📊 Phương pháp đánh giá & Sản phẩm đầu ra bạn cần hoàn thành:

* **Tiêu chí đánh giá:** Hệ thống sẽ đo lường các chỉ số về *throughput*, *GPU utilization*, *scalability* (khả năng mở rộng), *communication overhead* (chi phí truyền thông mạng) và năng lực quản trị cluster của công cụ BCM.
* **Sản phẩm/Demo yêu cầu:**
* Demo quá trình provisioning (cấp phát/triển khai hệ thống) và monitoring GPU cluster bằng BCM.
* Demo chạy thử nghiệm huấn luyện phân tán (distributed training) trên cụm H200/B200 hoặc cụm DGX SuperPOD.
* Xây dựng Dashboard trực quan hóa trạng thái sử dụng GPU (GPU usage), trạng thái các job (job status) và tiến trình huấn luyện (training progress).
* Biên soạn bộ tài liệu hướng dẫn triển khai AI workload trên hệ thống cluster này.


* **Tài liệu báo cáo:** 01 poster trình bày kiến trúc và kết quả đánh giá; 01 báo cáo kỹ thuật dài khoảng 4 trang trình bày chi tiết về kiến trúc, quá trình triển khai thực tế kèm phân tích hiệu năng hệ thống.