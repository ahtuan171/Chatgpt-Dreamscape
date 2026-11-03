# ☾ ChatGPT Dreamscape

**Biến ChatGPT thành không gian của riêng bạn. · Make your ChatGPT feel like home.**

**Ngôn ngữ / Languages:** [🇻🇳 Tiếng Việt](#tieng-viet) · [🇬🇧 English](#english)

---

<a id="tieng-viet"></a>
## 🇻🇳 Tiếng Việt

**ChatGPT Dreamscape** là một userscript mã nguồn mở giúp bạn tùy chỉnh giao diện ChatGPT trên **trình duyệt máy tính** bằng những hình nền giàu cảm xúc và một người bạn pixel nhỏ tên **Victor**.

> **Bản xem trước v0.3.11.** Đây là dự án cộng đồng độc lập, không phải tính năng chính thức của OpenAI. Giao diện ChatGPT có thể thay đổi và ảnh hưởng đến userscript; nếu phát hiện lỗi, hãy [tạo issue](https://github.com/ahtuan171/Chatgpt-Dreamscape/issues).

### 🖼️ Thư viện hình nền

Bộ sưu tập có **5 hình nền gốc** với không khí riêng và vùng chữ dễ đọc.

![Năm hình nền ChatGPT Dreamscape](docs/images/wallpaper-gallery-v036.png)

| Hình nền | Xem trước | Phong cách | Độ dễ đọc |
| --- | --- | --- | --- |
| **Moonlit Castle** | <img src="assets/wallpapers/moonlit-castle.webp" alt="Moonlit Castle" width="190"> | Thần thoại dưới trăng | Lâu đài ở xa, nền trời tối giúp chữ dễ đọc |
| **Midnight Tulips** | <img src="assets/wallpapers/midnight-tulips.webp" alt="Midnight Tulips" width="190"> | Hoa đêm dịu nhẹ | Hoa tập trung ở rìa ảnh, vùng nội dung ít chi tiết |
| **Prince & Princess** | <img src="assets/wallpapers/moonlit-romance.webp" alt="Prince & Princess" width="190"> | Cổ tích lãng mạn | Nhân vật ở xa, giữ không gian thoáng cho hội thoại |
| **Arcane Library** | <img src="assets/wallpapers/arcane-library.webp" alt="Arcane Library" width="190"> | Pixel art · Dark Academia | Ánh đèn và kệ sách nằm về hai bên |
| **The Silent King** | <img src="assets/wallpapers/silent-king.webp" alt="The Silent King" width="190"> | Cờ vua · Tối giản | Quân cờ nằm phía phải; khoảng trống tối để đọc chữ |

Bạn cũng có thể nhập hình nền cá nhân từ menu **☾**.

### ✨ Tính năng

- **Đổi hình nền:** lựa chọn một trong năm hình nền có sẵn hoặc tải ảnh cá nhân (PNG, JPG, WebP). Khi đổi ảnh, hình nền mới lan rộng mềm mại từ một góc ngẫu nhiên; tắt chuyển động trong hệ điều hành sẽ bỏ qua hiệu ứng.
- **Tùy chỉnh từng ảnh:** xem trước, điều chỉnh độ tối và vị trí hiển thị theo chiều ngang (0% trái · 50% giữa · 100% phải khi ảnh bị cắt).
- **Lưu trữ trên thiết bị:** ảnh cá nhân được xử lý và lưu trong trình duyệt bằng IndexedDB; không tải lên máy chủ hình nền.
- **Victor — bạn mèo pixel:** đứng phía trên tùy chọn mức suy luận “High” trong ô nhập (hoặc vị trí gần đó nếu giao diện khác), lớn hơn 15% so với v0.3.1, đi lại một đoạn ngắn, quay đầu, chớp mắt và ngủ. Nhấp vào Victor để chú mèo nhảy lên và hiện trái tim; có thể bật/tắt và tôn trọng tùy chọn giảm chuyển động.
- **Giao diện dễ đọc:** ô nhập giữ nền tối đặc để đọc chữ rõ ràng. Có thể bật/tắt Victor, chuyển động và Dreamscape bằng ô đánh dấu.
- **Tôn trọng quyền riêng tư:** không có công cụ phân tích hành vi, không thu thập nội dung hội thoại.

### 🚀 Cài đặt (không cần terminal)

1. Cài trình quản lý userscript trên trình duyệt máy tính, chẳng hạn [Tampermonkey](https://www.tampermonkey.net/) hoặc [Violentmonkey](https://violentmonkey.github.io/).
2. Nhấn **[Cài đặt ChatGPT Dreamscape](https://github.com/ahtuan171/Chatgpt-Dreamscape/raw/refs/heads/main/dist/dreamscape.user.js)**, sau đó chọn **Install / Cài đặt** khi trình quản lý userscript mở ra.
3. Truy cập hoặc tải lại [ChatGPT](https://chatgpt.com/). Nhấn biểu tượng **☾** ở góc dưới bên phải để chọn hình nền, thêm ảnh và bật/tắt Victor.

Nếu trình duyệt tải tệp `.user.js` xuống thay vì mở trang cài đặt, hãy nhập tệp vào trình quản lý userscript. Một số trình duyệt dựa trên Chromium có thể yêu cầu bật quyền **Allow User Scripts** trong cài đặt tiện ích.

**Nền tảng mục tiêu:** Chrome, Firefox, Edge và Brave trên Windows, macOS và Linux (ưu tiên kiểm thử Chrome và Firefox). Chưa hỗ trợ chính thức trình duyệt di động hoặc ứng dụng ChatGPT desktop. Khả năng tương thích trên mọi trình duyệt vẫn cần kiểm chứng thực tế.

### 🔧 Khắc phục lỗi: Không thấy Dreamscape

Nếu hình nền, Victor hoặc nút **☾** không xuất hiện, Tampermonkey có thể chưa được phép chạy userscript. Với **Chrome 138 trở lên** và một số trình duyệt Chromium:

1. Mở `chrome://extensions/` → **Tampermonkey** → **Details** → bật **Allow User Scripts** (có thể cần bật **Developer mode** trước; tên tùy chọn có thể khác tùy trình duyệt).
2. Vào **Tampermonkey Dashboard**, kiểm tra **ChatGPT Dreamscape** đã được bật.
3. Tải lại [chatgpt.com](https://chatgpt.com/).

**Kiểm tra nhanh (không bắt buộc):** Nhấn `F12` → **Console** rồi chạy `!!document.querySelector("#dreamscape-app")`. Kết quả `true` nghĩa là giao diện Dreamscape đã được chèn vào trang; nếu hình nền vẫn không hiện, hãy kiểm tra nút bật giao diện trong phần cài đặt **☾**.


### 🐈 Gặp Victor

<img src="assets/pets/victor/idle-1.webp" alt="Victor — chú mèo pixel xám" width="65">

**Victor** là thú cưng mặc định và duy nhất đi kèm bản công khai. Bạn có thể nhấp vào Victor (hoặc nhấn Enter khi chọn chú mèo) để nhận một phản ứng vui nhộn. Bạn có thể tắt Victor nếu thích một giao diện yên tĩnh. Các sprite Spidey cá nhân không nằm trong dự án.

**Nếu từng cài phiên bản Dreamscape cũ**, hãy tắt các userscript Dreamscape trước đó trong Tampermonkey để tránh hiển thị trùng lặp.

### 🎨 Thêm hình nền cá nhân

Mở **☾ → Add wallpaper**, chọn ảnh PNG/JPEG/WebP dung lượng dưới **15 MB**. Dreamscape có thể thu nhỏ ảnh lớn (tối đa 2400 × 1600), chuyển sang WebP và lưu bằng IndexedDB trong trình duyệt.

Bạn có thể đổi ảnh, làm tối, chỉnh vị trí hoặc xóa hình nền đã nhập. Các hình nền này không tự đồng bộ giữa những trình duyệt, hồ sơ người dùng hay máy tính khác nhau; việc xóa dữ liệu trang web có thể làm mất ảnh đã lưu.

Nếu bạn đang dùng hình nền mặc định đã bị loại bỏ ở phiên bản mới, Dreamscape sẽ chuyển về **Moonlit Castle**; hình nền cá nhân vẫn được giữ lại.

### 🛠️ Dành cho người đóng góp

Người dùng thông thường **không cần tải mã nguồn hoặc sử dụng terminal**. Nếu muốn phát triển hoặc đóng góp:

~~~bash
git clone https://github.com/ahtuan171/Chatgpt-Dreamscape.git
cd Chatgpt-Dreamscape
node tools/build.mjs
python -m pip install playwright
python -m playwright install chromium
python tests/test_browser.py
~~~

Mã nguồn ở [`src/`](src/), ảnh ở [`assets/`](assets/), bộ công cụ build ở [`tools/`](tools/) và userscript cài đặt ở [`dist/dreamscape.user.js`](dist/dreamscape.user.js). Bài kiểm thử dùng giao diện ChatGPT mô phỏng, **không phải** tài khoản ChatGPT thật; xem [hướng dẫn kiểm thử](docs/TESTING.md).

### 🛡️ Lưu ý & giấy phép

- Dreamscape chỉ chạy trên `https://chatgpt.com/*`; hãy kiểm tra quyền userscript trước khi cài.
- Script chỉ nhận biết hoạt động gõ trong ô nhập để kích hoạt Victor, không lưu nội dung tin nhắn.
- Nếu cập nhật giao diện ChatGPT làm Dreamscape hoạt động sai, bạn có thể tắt script và [báo lỗi](https://github.com/ahtuan171/Chatgpt-Dreamscape/issues).
- **Mã nguồn** sử dụng [giấy phép MIT](LICENSE). **Hình nền và sprite Victor** có điều khoản riêng tại [ASSETS.md](ASSETS.md). Không đưa hình ảnh bên thứ ba vào bản phân phối khi chưa có quyền phù hợp.

---

<a id="english"></a>
## 🇬🇧 English

**ChatGPT Dreamscape** is an independent, open-source userscript that brings atmospheric wallpapers and **Victor**, a tiny gray pixel cat, to the **desktop ChatGPT web interface**.

> **Early public preview · v0.3.11.** This is a community customization, not an official OpenAI feature. Changes to ChatGPT's interface may affect compatibility. Please [open an issue](https://github.com/ahtuan171/Chatgpt-Dreamscape/issues) when something breaks.

### 🖼️ Built-in wallpapers

Dreamscape includes **5 original wallpapers**, designed to balance atmosphere and chat readability.

![Five ChatGPT Dreamscape wallpapers](docs/images/wallpaper-gallery-v036.png)

| Wallpaper | Preview | Mood | Readability |
| --- | --- | --- | --- |
| **Moonlit Castle** | <img src="assets/wallpapers/moonlit-castle.webp" alt="Moonlit Castle" width="190"> | Moonlit fantasy | Distant castle and dark sky leave room for text |
| **Midnight Tulips** | <img src="assets/wallpapers/midnight-tulips.webp" alt="Midnight Tulips" width="190"> | Nocturnal florals | Flowers frame the edges, leaving a quiet center |
| **Prince & Princess** | <img src="assets/wallpapers/moonlit-romance.webp" alt="Prince & Princess" width="190"> | Poetic romance | Distant silhouettes keep the conversation area clear |
| **Arcane Library** | <img src="assets/wallpapers/arcane-library.webp" alt="Arcane Library" width="190"> | Pixel art · Dark academia | Bookshelves and lamp frame a calm dark center |
| **The Silent King** | <img src="assets/wallpapers/silent-king.webp" alt="The Silent King" width="190"> | Minimalist chess | Chess pieces on the right preserve dark text-friendly space |

You can also import your own wallpapers from the **☾** menu.

### ✨ Features

- **Custom wallpapers:** choose a built-in image or import a PNG, JPEG or WebP file. New selections reveal smoothly from a random corner; reduced-motion preferences disable the effect.
- **Per-wallpaper controls:** preview images, adjust darkness, and change horizontal cropping (0% left · 50% center · 100% right when cropped).
- **Local storage:** your personal images are processed and saved in your browser with IndexedDB, not uploaded to a wallpaper server.
- **Victor:** an optional gray pixel cat perched above the composer's “High” effort control (or nearby if unavailable), 15% larger than v0.3.1. He walks a short distance, turns to face the return direction, blinks and sleeps. Click Victor for a little hop and heart; reduced-motion preferences are respected.
- **Readable interface:** the composer keeps a solid dark background for legible text. Visible checkboxes control Victor, gentle animations, and Dreamscape.
- **Privacy-first:** no analytics and no collection of conversation text.

### 🚀 Install (desktop only; no terminal)

1. Install a userscript manager, such as [Tampermonkey](https://www.tampermonkey.net/) or [Violentmonkey](https://violentmonkey.github.io/), in your desktop browser.
2. Click **[Install ChatGPT Dreamscape](https://github.com/ahtuan171/Chatgpt-Dreamscape/raw/refs/heads/main/dist/dreamscape.user.js)** and confirm **Install** in the userscript manager.
3. Open or refresh [ChatGPT](https://chatgpt.com/). Click **☾** at the bottom-right to switch wallpapers, upload an image, or toggle Victor.

If the browser downloads the `.user.js` instead of showing an installer, import that file through your userscript manager. Some Chromium-based browsers require enabling **Allow User Scripts** in extension settings.

**Compatibility targets:** Chrome, Firefox, Edge and Brave on Windows, macOS and Linux, with Chrome and Firefox receiving priority testing. Mobile browsers and desktop-app integration are out of scope. Broad desktop compatibility is a goal, not a guarantee for every release.

### 🔧 Troubleshooting: Dreamscape not showing

If the wallpaper, Victor or the **☾** button is missing, your browser may be blocking Tampermonkey userscripts. On **Chrome 138+** and some Chromium-based browsers:

1. Open `chrome://extensions/` → **Tampermonkey** → **Details** → enable **Allow User Scripts** (you may need **Developer mode** first; labels vary by browser).
2. Check that **ChatGPT Dreamscape** is enabled in the **Tampermonkey Dashboard**.
3. Reload [chatgpt.com](https://chatgpt.com/).

**Optional check:** Press `F12` → **Console** and run `!!document.querySelector("#dreamscape-app")`. `true` means the Dreamscape interface was inserted; if the wallpaper is still missing, check whether the theme is enabled in **☾** settings.


### 🐈 Meet Victor

<img src="assets/pets/victor/idle-1.webp" alt="Victor, the gray pixel cat" width="65">

Victor is the **only bundled pet**. He stays above the effort selector, makes small walks, turns around and rests. Click him (or focus and press Enter) to pet him. You can disable him at any time. The personal red Spidey sprite is **not included** in the public release.

If you have an older Dreamscape installation, disable previous Dreamscape scripts before enabling the current one to prevent duplicate pets or conflicting styles.

### 🎨 Bring your own wallpaper

Choose **☾ → Add wallpaper**. Images must be PNG/JPEG/WebP and under **15 MB**. Dreamscape resizes large images (up to 2400 × 1600), converts them to optimized WebP locally, and saves them through IndexedDB.

You can select, dim, reposition or delete imported wallpapers. Images and settings belong to your browser profile and website origin; they do **not** automatically sync to other devices, and clearing browser data may remove them.

If a retired built-in wallpaper was selected, the updated script falls back to **Moonlit Castle** without deleting imported images.

### 🛠️ For contributors

Ordinary users **do not need a terminal, Node.js or a source checkout**. To work on the project:

~~~bash
git clone https://github.com/ahtuan171/Chatgpt-Dreamscape.git
cd Chatgpt-Dreamscape
node tools/build.mjs
python -m pip install playwright
python -m playwright install chromium
python tests/test_browser.py
~~~

Source files live in [`src/`](src/), assets in [`assets/`](assets/), build tooling in [`tools/`](tools/), and the installable userscript in [`dist/dreamscape.user.js`](dist/dreamscape.user.js). Bundled images are embedded into the build, so installed users do not need external wallpaper requests.

Browser tests use a **simulated ChatGPT page**, not a real signed-in ChatGPT session. See [Testing](docs/TESTING.md).

### 🛡️ Safety, limitations & licensing

- Dreamscape is restricted to `https://chatgpt.com/*`. Review userscript permissions before installing.
- It detects typing activity only to animate Victor; it does not store or transmit message content.
- ChatGPT UI changes may temporarily break appearance or pet positioning. Disable the script if needed and [report a bug](https://github.com/ahtuan171/Chatgpt-Dreamscape/issues).
- **Code:** [MIT License](LICENSE). **Bundled artwork and Victor sprites:** separate terms in [ASSETS.md](ASSETS.md). Do not redistribute unlicensed third-party imagery.
