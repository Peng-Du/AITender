async function fetchMe() {
  try {
    const res = await fetch('/api/auth/me');
    if (res.ok) return res.json();
  } catch (_) {}
  return null;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

async function initUserInfo() {
  const user = await fetchMe();
  const el = document.getElementById('userInfo');
  if (!el) return;
  if (user) {
    el.innerHTML = `<span class="me-2">欢迎，${escapeHtml(user.full_name || user.username)}</span>
      <button id="logoutBtn" class="btn btn-outline-danger btn-sm">退出</button>`;
    document.getElementById('logoutBtn').addEventListener('click', async () => {
      await fetch('/api/auth/logout', { method: 'POST' });
      location.reload();
    });
  }
}

async function initUploadForm() {
  const form = document.getElementById('uploadForm');
  const msg = document.getElementById('uploadMessage');
  if (!form) return;
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    msg.textContent = '正在上传...';
    const fd = new FormData(form);
    try {
      const res = await fetch('/api/upload/file', { method: 'POST', body: fd });
      const json = await res.json();
      if (!res.ok) throw new Error(json.error || '上传失败');
      msg.textContent = '上传成功';
    } catch (err) {
      msg.textContent = err.message;
    }
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initUserInfo();
  initUploadForm();
});