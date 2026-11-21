# ChatGPT UI compatibility / Tương thích giao diện

Applies to **Dreamscape v0.3.17** (21 November 2026).

## Tiếng Việt

### Cơ chế tương thích

Giao diện Chat/Work đôi khi có các lớp nền lớn che lên hình nền của Dreamscape. v0.3.17 nhận diện phần tử vùng nội dung theo kích thước/vị trí và gắn `.ds-stage`. Khi Dreamscape bật, CSS làm trong suốt nền các vùng này; nền ô nhập, menu, nút bấm và sidebar vẫn được giữ. Khi tắt, quy tắc Dreamscape không áp dụng.

### Trạng thái kiểm tra

| Giao diện | Bộ kiểm thử Chromium mô phỏng | Phiên ChatGPT đã đăng nhập |
| --- | --- | --- |
| Chat mới, nút Chat/Work, thanh bên | Có, 1024px và 1676px | Chưa xác nhận |
| Chuyển sang hội thoại, ô nhập và dock | Có regression | Chưa xác nhận |
| Work và cửa sổ phụ thực tế | Chỉ mô phỏng một phần | Chưa xác nhận |
| Bật/tắt Dreamscape | Có regression | Chưa xác nhận |

**PASS trên CI không có nghĩa mọi giao diện thật đều đã được kiểm chứng.** Bộ kiểm thử dựng lại cấu trúc trang từ ảnh chụp và fixture, không có phiên đăng nhập.

### Nếu hình nền vẫn bị che

1. Cài/cập nhật từ [bản mới trên main](https://github.com/ahtuan171/Chatgpt-Dreamscape/raw/refs/heads/main/dist/dreamscape.user.js); xác nhận phiên bản `0.3.17`, tắt script trùng và tải lại.
2. Trong **☾**, xác nhận **Enable Dreamscape** đang bật.
3. So sánh Chat mới, hội thoại đã có và Work (nếu tài khoản có) để xác định trạng thái lỗi.
4. Gửi issue với phiên bản trình duyệt, hệ điều hành, trạng thái trang, kích thước cửa sổ và ảnh đã che thông tin riêng tư. **Không** gửi tin nhắn, cookie, token hoặc toàn bộ HTML/DOM.

Có thể chạy kiểm tra **chỉ đọc** trong Developer Tools → Console:

```js
({
  dreamscapeLoaded: !!document.querySelector('#dreamscape-app'),
  active: document.documentElement.classList.contains('ds-active'),
  stageCount: document.querySelectorAll('.ds-stage').length,
  composerCount: document.querySelectorAll('.ds-composer').length
})
```

Kết quả chỉ gồm trạng thái và số lượng phần tử, không chứa nội dung chat. `stageCount: 0` không tự động xác nhận lỗi, vì một số bố cục đã được xử lý bởi CSS có sẵn.

## English

v0.3.17 conservatively identifies viewport-sized opaque Chat/Work content-stage containers and marks them with `.ds-stage`. Only their backgrounds are made transparent while Dreamscape is enabled; interactive surfaces are intended to stay opaque.

**Verification:** the build, syntax and Chromium fixture suite passed, including screenshot-inspired page layers and composer relocation. The fixtures are reconstructed, **not** collected from a signed-in ChatGPT session, so real Work views and dialogs still need manual verification.

**Troubleshooting:** verify the 0.3.17 script is enabled once, refresh, select a wallpaper from **☾**, and compare New Chat with existing conversations and Work (if available). For a persistent issue, report browser/version, OS, viewport, state and a **redacted** screenshot. Never post conversation text, tokens or full DOM.

See the [manual checklist](TESTING.md) and [security guidance](../SECURITY.md).
