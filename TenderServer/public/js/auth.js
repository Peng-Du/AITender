document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('loginForm');
  const messageEl = document.getElementById('loginMessage');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    messageEl.textContent = '';
    const fd = new FormData(form);
    const body = { username: fd.get('username'), password: fd.get('password') };
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.error || '登录失败');
      location.href = '/';
    } catch (err) {
      messageEl.textContent = err.message;
    }
  });
});