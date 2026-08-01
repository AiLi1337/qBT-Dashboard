/* ============================================
   qBittorrent Auto Reannounce - App JS v2
   ============================================ */

// Toast Notification System
function showToast(message, type) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  toast.className = 'toast-msg ' + (type || '');
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.classList.add('toast-exit');
    toast.addEventListener('animationend', () => toast.remove(), { once: true });
  }, 3500);
}

// API Request Helper
async function apiRequest(url, options = {}) {
  const headers = new Headers(options.headers || {});
  const csrfToken = window.APP_CSRF_TOKEN || (document.querySelector('meta[name="csrf-token"]') || {}).content;
  if (csrfToken) {
    headers.set('X-CSRF-Token', csrfToken);
  }
  if (!headers.has('Content-Type') && options.body && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }
  const response = await fetch(url, {
    credentials: 'same-origin',
    ...options,
    headers,
  });
  if (response.status === 204 || response.status === 205) return null;
  const contentType = response.headers.get('content-type') || '';
  const data = contentType.includes('application/json') ? await response.json() : await response.text();
  if (!response.ok) {
    const detail = typeof data === 'object' && data !== null ? data.detail : data;
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail || '请求失败'));
  }
  return data;
}

// Message Helper
function setMessage(element, text, type) {
  if (!element) return;
  element.textContent = text;
  element.className = 'form-message ' + (type || '');
}

// Loading State
function showLoading(button) {
  if (!button) return;
  button.disabled = true;
  button.dataset.originalHtml = button.innerHTML;
  var isIcon = button.classList.contains('btn-icon');
  var label = button.dataset.loadingText || '处理中...';
  var spinner = '<svg class="spinner" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10" stroke-opacity="0.25"/><path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round"/></svg>';
  button.classList.add('is-loading');
  if (isIcon) {
    button.dataset.originalAriaLabel = button.getAttribute('aria-label') || '';
    button.setAttribute('aria-label', label);
    button.innerHTML = spinner;
  } else {
    button.innerHTML = spinner + ' ' + label;
  }
}
function hideLoading(button) {
  if (!button) return;
  button.disabled = false;
  if (button.dataset.originalHtml) {
    button.innerHTML = button.dataset.originalHtml;
    delete button.dataset.originalHtml;
  }
  button.classList.remove('is-loading');
  if (button.dataset.originalAriaLabel !== undefined) {
    button.setAttribute('aria-label', button.dataset.originalAriaLabel);
    delete button.dataset.originalAriaLabel;
  }
}

// Build Instance Payload
function buildInstancePayload(formData, includePassword) {
  var payload = {
    name: formData.get('name'),
    base_url: formData.get('base_url'),
    username: formData.get('username'),
    interval_minutes: Number(formData.get('interval_minutes')),
    request_timeout_seconds: Number(formData.get('request_timeout_seconds')),
    retry_count: Number(formData.get('retry_count')),
    verify_tls: formData.get('verify_tls') === 'on',
    enabled: formData.get('enabled') === 'on',
    reannounce_enabled: formData.get('reannounce_enabled') === 'on',
  };
  var password = formData.get('password');
  if (includePassword || password) {
    payload.password = password;
  }
  return payload;
}

// DOM Ready
document.addEventListener('DOMContentLoaded', function () {
  // ============================================================
  //  SIDEBAR DRAWER TOGGLE (mobile)
  // ============================================================
  (function () {
    var toggle = document.getElementById('sidebar-toggle');
    var sidebar = document.getElementById('sidebar');
    var overlay = document.getElementById('sidebar-overlay');
    if (!toggle || !sidebar || !overlay) return;
    function closeSidebar() {
      sidebar.classList.remove('sidebar--open');
      overlay.classList.remove('active');
      toggle.setAttribute('aria-expanded', 'false');
      document.body.classList.remove('sidebar-open');
    }
    function openSidebar() {
      sidebar.classList.add('sidebar--open');
      overlay.classList.add('active');
      toggle.setAttribute('aria-expanded', 'true');
      document.body.classList.add('sidebar-open');
    }
    toggle.addEventListener('click', function () {
      if (sidebar.classList.contains('sidebar--open')) {
        closeSidebar();
      } else {
        openSidebar();
      }
    });
    overlay.addEventListener('click', closeSidebar);
    // Close on Escape
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && sidebar.classList.contains('sidebar--open')) {
        closeSidebar();
      }
    });
    // Clean up on resize to desktop
    var mql = window.matchMedia('(min-width: 769px)');
    mql.addEventListener('change', function (e) {
      if (e.matches && sidebar.classList.contains('sidebar--open')) {
        closeSidebar();
      }
    });
  })();

  // ============================================================
  //  NAV ACTIVE STATE HIGHLIGHT
  // ============================================================
  (function () {
    var currentPath = window.location.pathname;
    var links = document.querySelectorAll('.nav-link');
    links.forEach(function (link) {
      var href = link.getAttribute('href');
      if (href === currentPath || (href === '/' && currentPath === '/')) {
        link.classList.add('active');
      } else if (href !== '/' && currentPath.startsWith(href)) {
        link.classList.add('active');
      }
    });
  })();

  // ============================================================
  //  PASSWORD TOGGLE
  // ============================================================
  document.querySelectorAll('input[type="password"]').forEach(function (input) {
    var wrapper = input.closest('.form-field') || input.parentElement;
    if (!wrapper) return;
    var toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'pw-toggle';
    toggle.textContent = '显示';
    toggle.addEventListener('click', function () {
      if (input.type === 'password') {
        input.type = 'text';
        toggle.textContent = '隐藏';
      } else {
        input.type = 'password';
        toggle.textContent = '显示';
      }
    });
    // Only add to login page password fields
    if (input.closest('.login-card')) {
      var field = input.closest('.form-field');
      if (field) field.classList.add('has-pw-toggle');
      input.parentElement.classList.add('has-pw-toggle');
      input.parentElement.appendChild(toggle);
    }
  });

  // ============================================================
  //  INSTANCE SEARCH/FILTER
  // ============================================================
  (function () {
    var cards = document.querySelectorAll('.instance-card-details');
    if (!cards.length) return;
    var panel = cards[0].closest('.panel');
    if (!panel) return;
    var head = panel.querySelector('.panel-head');
    if (!head) return;

    var searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.placeholder = '搜索实例...';
    searchInput.className = 'search-input';
    searchInput.addEventListener('input', function () {
      var query = this.value.toLowerCase().trim();
      cards.forEach(function (card) {
        var title = card.querySelector('.instance-title h4');
        var url = card.querySelector('.instance-title p');
        var text = ((title ? title.textContent : '') + ' ' + (url ? url.textContent : '')).toLowerCase();
        card.classList.toggle('is-hidden', query !== '' && !text.includes(query));
      });
    });
    head.appendChild(searchInput);
  })();

  // ============================================================
  //  CREATE INSTANCE FORM
  // ============================================================
  var createForm = document.getElementById('create-instance-form');
  var createMessage = document.getElementById('create-instance-message');
  var createSubmitBtn = createForm ? createForm.querySelector('button[type="submit"]') : null;

  if (createForm) {
    createForm.addEventListener('submit', async function (event) {
      event.preventDefault();
      var payload = buildInstancePayload(new FormData(createForm), true);
      if (createSubmitBtn) showLoading(createSubmitBtn);
      setMessage(createMessage, '', '');

      try {
        await apiRequest('/api/v1/instances', {
          method: 'POST',
          body: JSON.stringify(payload),
        });
        setMessage(createMessage, '实例已创建，页面即将刷新。', 'success');
        showToast('实例创建成功', 'success');
        setTimeout(function () { window.location.reload(); }, 800);
      } catch (error) {
        setMessage(createMessage, error.message, 'error');
        showToast(error.message, 'error');
      } finally {
        if (createSubmitBtn) hideLoading(createSubmitBtn);
      }
    });
  }

  // ============================================================
  //  UPDATE INSTANCE FORMS
  // ============================================================
  document.querySelectorAll('[data-update-instance-form]').forEach(function (form) {
    form.addEventListener('submit', async function (event) {
      event.preventDefault();
      var instanceId = form.dataset.updateInstanceForm;
      var target = document.querySelector('[data-instance-message="' + instanceId + '"]');
      var submitBtn = form.querySelector('button[type="submit"]');
      var payload = buildInstancePayload(new FormData(form), false);

      if (submitBtn) showLoading(submitBtn);
      setMessage(target, '', '');

      try {
        await apiRequest('/api/v1/instances/' + instanceId, {
          method: 'PATCH',
          body: JSON.stringify(payload),
        });
        setMessage(target, '配置已保存，页面即将刷新。', 'success');
        showToast('实例配置已更新', 'success');
        setTimeout(function () { window.location.reload(); }, 800);
      } catch (error) {
        setMessage(target, error.message, 'error');
        showToast(error.message, 'error');
      } finally {
        if (submitBtn) hideLoading(submitBtn);
      }
    });
  });

  // ============================================================
  //  TEST CONNECTION
  // ============================================================
  document.querySelectorAll('[data-action="test"]').forEach(function (button) {
    button.addEventListener('click', async function () {
      var id = button.dataset.instanceId;
      var target = document.querySelector('[data-instance-message="' + id + '"]');
      showLoading(button);
      setMessage(target, '正在测试连接...', '');

      try {
        var data = await apiRequest('/api/v1/instances/' + id + '/test-connection', { method: 'POST' });
        var ok = data.reachable && data.authenticated && data.app_version;
        var card = button.closest('.instance-card') || button.closest('details');
        var badge = card ? card.querySelector('.badge') : null;
        if (ok) {
          setMessage(target, data.message + (data.app_version ? ' (版本: ' + data.app_version + ')' : ''), 'success');
          showToast('连接成功', 'success');
          if (badge) { badge.className = 'badge badge-ok'; badge.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg>正常'; }
        } else {
          var message = data.message || '连接失败';
          setMessage(target, message, 'error');
          showToast('连接失败: ' + message, 'error');
          if (badge) { badge.className = 'badge badge-error'; badge.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>异常'; }
        }
      } catch (error) {
        setMessage(target, error.message, 'error');
        showToast('连接失败: ' + error.message, 'error');
      } finally {
        hideLoading(button);
      }
    });
  });

  // ============================================================
  //  RUN NOW
  // ============================================================
  document.querySelectorAll('[data-action="run"]').forEach(function (button) {
    button.addEventListener('click', async function () {
      var id = button.dataset.instanceId;
      var target = document.querySelector('[data-instance-message="' + id + '"]');
      showLoading(button);
      button.dataset.loadingText = '执行中...';
      setMessage(target, '正在执行重新做种...', '');

      try {
        var data = await apiRequest('/api/v1/instances/' + id + '/run-now', { method: 'POST' });
        setMessage(target, '已完成，本次处理 ' + data.torrent_count + ' 个种子。', 'success');
        showToast('强制汇报完成: ' + data.torrent_count + ' 个种子', 'success');
      } catch (error) {
        setMessage(target, error.message, 'error');
        showToast(error.message, 'error');
      } finally {
        hideLoading(button);
      }
    });
  });

  // ============================================================
  //  RECHECK ALL
  // ============================================================
  document.querySelectorAll('[data-action="recheck"]').forEach(function (button) {
    button.addEventListener('click', async function () {
      var id = button.dataset.instanceId;
      var target = document.querySelector('[data-instance-message="' + id + '"]');
      showLoading(button);
      setMessage(target, '正在重新校验种子...', '');

      try {
        var data = await apiRequest('/api/v1/instances/' + id + '/recheck', { method: 'POST' });
        setMessage(target, '校验完成，共 ' + data.torrent_count + ' 个种子。', 'success');
        showToast('强制校验完成', 'success');
      } catch (error) {
        setMessage(target, error.message, 'error');
        showToast(error.message, 'error');
      } finally {
        hideLoading(button);
      }
    });
  });

  // ============================================================
  //  DELETE INSTANCE
  // ============================================================
  document.querySelectorAll('[data-action="delete"]').forEach(function (button) {
    button.addEventListener('click', async function () {
      var id = button.dataset.instanceId;
      var name = button.dataset.instanceName;
      var target = document.querySelector('[data-instance-message="' + id + '"]');

      if (!confirm('确定要删除实例 "' + name + '" 吗？此操作不可恢复。')) return;

      showLoading(button);
      button.dataset.loadingText = '删除中...';
      setMessage(target, '正在删除...', '');

      try {
        await apiRequest('/api/v1/instances/' + id, { method: 'DELETE' });
        setMessage(target, '实例已删除。', 'success');
        showToast('实例已删除', 'success');
        setTimeout(function () { window.location.reload(); }, 1000);
      } catch (error) {
        setMessage(target, error.message, 'error');
        showToast(error.message, 'error');
        hideLoading(button);
      }
    });
  });

  // ============================================================
  //  SINGLE TORRENT ACTIONS
  // ============================================================
  document.querySelectorAll('[data-action="reannounce-one"]').forEach(function (btn) {
    btn.addEventListener('click', async function () {
      var hash = this.getAttribute('data-hash');
      var instanceId = this.getAttribute('data-instance');
      this.disabled = true;
      try {
        await apiRequest('/api/v1/instances/' + instanceId + '/torrents/' + hash + '/reannounce', { method: 'POST' });
        showToast('强制重新汇报成功', 'success');
      } catch (err) {
        showToast('操作失败: ' + err.message, 'error');
      } finally {
        this.disabled = false;
      }
    });
  });

  document.querySelectorAll('[data-action="recheck-one"]').forEach(function (btn) {
    btn.addEventListener('click', async function () {
      var hash = this.getAttribute('data-hash');
      var instanceId = this.getAttribute('data-instance');
      this.disabled = true;
      try {
        await apiRequest('/api/v1/instances/' + instanceId + '/torrents/' + hash + '/recheck', { method: 'POST' });
        showToast('强制重新校验成功', 'success');
      } catch (err) {
        showToast('操作失败: ' + err.message, 'error');
      } finally {
        this.disabled = false;
      }
    });
  });

  // ============================================================
  //  LOGOUT
  // ============================================================
  document.querySelectorAll('[data-csrf-form]').forEach(function (form) {
    form.addEventListener('submit', function (event) {
      event.preventDefault();
      var token = window.APP_CSRF_TOKEN || (document.querySelector('meta[name="csrf-token"]') || {}).content || '';
      var body = new URLSearchParams();
      body.set('csrf_token', token);
      fetch(form.action, {
        method: form.method || 'POST',
        credentials: 'same-origin',
        headers: {
          'X-CSRF-Token': token,
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: body.toString(),
      }).then(function () {
        window.location.href = '/login';
      }).catch(function () {
        window.location.href = '/login';
      });
    });
  });

  // Traffic stats polling — immediate first call, then every 60s
  if (window.location.pathname.includes('/instances') || window.location.pathname === '/') {
    if (typeof window.updateTrafficStats === 'function') {
      window.updateTrafficStats();
      setInterval(function () {
        window.updateTrafficStats();
      }, 60000);
    }
  }

  // ============================================================
  //  THEME TOGGLE
  // ============================================================
  (function () {
    var btn = document.getElementById('theme-toggle');
    if (!btn) return;
    btn.addEventListener('click', function () {
      var isDark = document.documentElement.getAttribute('data-theme') !== 'light';
      if (isDark) {
        document.documentElement.setAttribute('data-theme', 'light');
        localStorage.setItem('qb-theme', 'light');
      } else {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('qb-theme', 'dark');
      }
    });
  })();

  // ============================================================
  //  RUNS PAGE — INSTANCE FILTER (server-side pagination)
  // ============================================================
  document.getElementById('filter-instance')?.addEventListener('change', function () {
    var params = new URLSearchParams(window.location.search);
    params.set('page', '1');
    params.delete('page_size');
    if (this.value) {
      params.set('instance_id', this.value);
    } else {
      params.delete('instance_id');
    }
    window.location.search = params.toString();
  });
});


// ============================================================
// Sidebar Torrent Panel
// ============================================================
(function () {
  var REFRESH_INTERVAL_MS = 10000;
  var panelList = null;
  var panelContainer = null;
  var refreshBtn = null;
  var refreshTimer = null;
  var expandedInstances = {};
  var instanceCache = {};
  var scrollPositions = {};
  var toggleGeneration = 0;

  function formatSeedPeer(connected, total) {
    var unconnected = Math.max(0, total - connected);
    return connected + '(' + unconnected + ')';
  }

  function formatSpeed(bytesPerSec) {
    if (bytesPerSec === 0) return "0 B/s";
    var units = ["B/s", "KiB/s", "MiB/s", "GiB/s", "TiB/s"];
    var i = 0;
    var val = bytesPerSec;
    while (val >= 1024 && i < units.length - 1) { val /= 1024; i++; }
    return val.toFixed(val >= 10 ? 1 : 2) + " " + units[i];
  }

  function formatData(bytes) {
    if (bytes === 0) return "0 B";
    var units = ["B", "KiB", "MiB", "GiB", "TiB"];
    var i = 0;
    var val = bytes;
    while (val >= 1024 && i < units.length - 1) { val /= 1024; i++; }
    return val.toFixed(val >= 10 ? 1 : 2) + " " + units[i];
  }

  async function fetchTransferInfo(instanceId) {
    return await apiRequest("/api/v1/instances/" + instanceId + "/transfer-info");
  }

  async function updateTrafficStats() {
    var containers = document.querySelectorAll('[id^="traffic-"]');
    if (containers.length === 0) return;
    for (var i = 0; i < containers.length; i++) {
      var el = containers[i];
      var id = el.id.replace("traffic-", "");
      if (!id) continue;
      try {
        var info = await fetchTransferInfo(parseInt(id, 10));
        var dlTotal = el.querySelector(".traffic-dl .traffic-total");
        var upTotal = el.querySelector(".traffic-up .traffic-total");
        if (dlTotal) dlTotal.textContent = formatData(info.dl_info_data || 0);
        if (upTotal) upTotal.textContent = formatData(info.up_info_data || 0);
      } catch (e) { console.error("Traffic stats error:", e); }
    }
  }

  function ratioClass(ratio) {
    if (ratio >= 2) return 'ratio-high';
    if (ratio >= 1) return 'ratio-mid';
    return 'ratio-low';
  }

  function stateClass(state) {
    var s = (state || '').toLowerCase();
    if (s === 'downloading' || s === 'stalleddl' || s === 'forceddl' || s === 'metadl') return 'state-downloading';
    if (s === 'uploading' || s === 'stalledup' || s === 'forcedup' || s === 'seeding') return 'state-seeding';
    if (s === 'pausedup' || s === 'pauseddl' || s === 'paused') return 'state-paused';
    if (s.indexOf('error') >= 0 || s === 'missingfiles' || s === 'unknown') return 'state-error';
    return '';
  }

  function expandIcon() {
    return '<svg class="expand-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>';
  }

  function spinnerSvg(cls) {
    return '<svg class="' + (cls || '') + '" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10" stroke-opacity="0.25"/><path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round"/></svg>';
  }

  async function fetchInstances() {
    return await apiRequest('/api/v1/instances');
  }

  async function fetchTorrents(instanceId) {
    return await apiRequest('/api/v1/instances/' + instanceId + '/torrents');
  }

  function renderSkeleton(count) {
    count = Math.min(count || 5, 8);
    var html = '<div class="sidebar-torrents-inner">';
    for (var i = 0; i < count; i++) {
      html +=
        '<div class="sidebar-skeleton-row">' +
          '<div class="sidebar-skeleton-line name"></div>' +
          '<div class="sidebar-skeleton-line stats"></div>' +
          '<div class="sidebar-skeleton-line ratio"></div>' +
        '</div>';
    }
    html += '</div>';
    return html;
  }

  function renderTorrentRow(t, index) {
    var seeds = formatSeedPeer(t.num_seeds || 0, t.num_complete || 0);
    var peers = formatSeedPeer(t.num_leechs || 0, t.num_incomplete || 0);
    var dls = formatSpeed(t.dlspeed || 0);
    var uls = formatSpeed(t.upspeed || 0);
    var ratio = parseFloat(t.ratio) || 0;
    var name = (t.name || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

    return (
      '<div class="sidebar-torrent-row ' + stateClass(t.state) + '" ' +
        'style="--stagger: ' + (index || 0) + '" ' +
        'title="' + name + '">' +
        '<span class="sidebar-torrent-name">' + name + '</span>' +
        '<span class="sidebar-torrent-stats">' +
          '<span class="seed-count" title="Seeds (connected/total)">S ' + seeds + '</span>' +
          '<span class="peer-count" title="Peers (connected/total)">P ' + peers + '</span>' +
          '<span class="dl-speed">' + dls + '</span>' +
          '<span class="ul-speed">' + uls + '</span>' +
        '</span>' +
        '<span class="sidebar-torrent-ratio ' + ratioClass(ratio) + '">' + ratio.toFixed(2) + '</span>' +
      '</div>'
    );
  }

  function renderInstanceItem(inst) {
    var expanded = expandedInstances[inst.id];
    var cached = instanceCache[inst.id];
    var cachedCount = cached && cached.torrent_count !== undefined ? cached.torrent_count : null;
    var objectCount = inst._torrents ? inst._torrents.length : (inst.torrent_count_cache !== undefined ? inst.torrent_count_cache : null);
    var torrentCount = cachedCount !== null ? cachedCount : objectCount;
    var isLoading = expanded && inst._loading;
    var hasTorrents = expanded && inst._torrents && inst._torrents.length > 0;
    var hasError = expanded && inst._torrentError;

    var html = '<div class="sidebar-instance' + (expanded ? ' expanded' : '') + '" data-instance-id="' + inst.id + '">';
    html += '<div class="sidebar-instance-header" data-action="toggle-instance" data-instance-id="' + inst.id + '" role="button" tabindex="0" aria-expanded="' + (expanded ? 'true' : 'false') + '">';
    html += expandIcon();
    html += '<span class="instance-name">' + inst.name.replace(/&/g, '&amp;').replace(/</g, '&lt;') + '</span>';
    if (isLoading) {
      html += '<span class="spinner-mini">' + spinnerSvg() + '</span>';
    } else {
      html += '<span class="instance-torrent-count">' + (torrentCount === null ? '--' : (torrentCount > 0 ? torrentCount : '\u65e0')) + '</span>';
    }
    html += '</div>';

    html += '<div class="sidebar-torrents" data-instance-torrents="' + inst.id + '">';
    if (isLoading) {
      html += renderSkeleton(cached ? cached.torrent_count || 5 : 5);
    } else if (hasError) {
      html += '<div class="sidebar-torrents-inner"><div class="sidebar-empty" style="color:var(--err-deep);">\u52a0\u8f7d\u79cd\u5b50\u5217\u8868\u5931\u8d25</div></div>';
    } else if (hasTorrents) {
      html += '<div class="sidebar-torrents-inner">';
      for (var i = 0; i < inst._torrents.length; i++) {
        html += renderTorrentRow(inst._torrents[i], i);
      }
      html += '</div>';
    } else if (expanded && inst._torrents && inst._torrents.length === 0) {
      html += '<div class="sidebar-torrents-inner"><div class="sidebar-empty">暂无种子</div></div>'; 
    }
    html += '</div>';
    html += '</div>';
    return html;
  }

  function renderPanel(instances) {
    if (!panelList) return;
    var html = '';
    for (var i = 0; i < instances.length; i++) {
      html += renderInstanceItem(instances[i]);
    }
    panelList.innerHTML = html || '<div class="sidebar-empty">No instances configured</div>';
  }

  async function toggleInstance(instanceId) {
    var wasExpanded = expandedInstances[instanceId];
    expandedInstances[instanceId] = !wasExpanded;

    // Save scroll before refresh
    if (panelList) scrollPositions._panel = panelList.scrollTop;

    if (!instanceCache[instanceId]) {
      instanceCache[instanceId] = {};
    }

    if (!wasExpanded) {
      // Expanding: load torrents
      var instances = instanceCache._instances || [];
      for (var i = 0; i < instances.length; i++) {
        if (instances[i].id === instanceId) {
          instances[i]._loading = true;
          break;
        }
      }
      renderPanel(instanceCache._instances || []);
      var gen = ++toggleGeneration;

      try {
        var torrents = await fetchTorrents(instanceId);
        if (gen !== toggleGeneration) return;
        instances = instanceCache._instances || [];
        for (var i = 0; i < instances.length; i++) {
          if (instances[i].id === instanceId) {
            instances[i]._loading = false;
            if (expandedInstances[instanceId]) {
              instances[i]._torrents = torrents;
              instances[i]._torrentError = false;
              instanceCache[instanceId].torrent_count = torrents.length;
            }
            break;
          }
        }
      } catch (err) {
        if (gen !== toggleGeneration) return;
        instances = instanceCache._instances || [];
        for (var i = 0; i < instances.length; i++) {
          if (instances[i].id === instanceId) {
            instances[i]._loading = false;
            instances[i]._torrents = null;
            instances[i]._torrentError = true;
            break;
          }
        }
      }
    }

    renderPanel(instanceCache._instances || []);
    requestAnimationFrame(function () {
      if (panelList && scrollPositions._panel !== undefined) {
        panelList.scrollTop = scrollPositions._panel;
      }
    });
  }

  async function refreshExpanded(forceAll) {
    var instances = forceAll ? await fetchInstances() : (instanceCache._instances || await fetchInstances());
    instanceCache._instances = instances;
    var expandedIds = Object.keys(expandedInstances).map(Number).filter(function (id) { return expandedInstances[id]; });
    var idsToRefresh = forceAll ? instances.map(function (inst) { return inst.id; }) : expandedIds;

    if (idsToRefresh.length === 0) {
      renderPanel(instances);
      return { refreshedCount: 0, totalCount: 0, failedCount: 0 };
    }

    var promises = [];
    var failures = [];
    for (var i = 0; i < idsToRefresh.length; i++) {
      var instId = idsToRefresh[i];
      promises.push(
        fetchTorrents(instId).then((function (id) { return function (torrents) {
          instanceCache[id] = instanceCache[id] || {};
          instanceCache[id].torrent_count = torrents.length;
          for (var j = 0; j < instances.length; j++) {
            if (instances[j].id === id) {
              if (expandedInstances[id]) {
                instances[j]._torrents = torrents;
                instances[j]._torrentError = false;
              }
              break;
            }
          }
          return torrents.length;
        }; })(instId)).catch((function (id) { return function (err) {
          failures.push({ id: id, message: err && err.message ? err.message : '未知错误' });
          for (var j = 0; j < instances.length; j++) {
            if (instances[j].id === id) {
              instances[j]._torrents = null;
              instances[j]._torrentError = true;
              break;
            }
          }
          return null;
        }; })(instId))
      );
    }
    var results = await Promise.all(promises);
    var totalCount = 0;
    for (var k = 0; k < results.length; k++) {
      if (typeof results[k] === 'number') totalCount += results[k];
    }
    renderPanel(instances);
    if (failures.length && forceAll) {
      throw new Error('刷新失败：' + failures.length + ' 台实例未响应（' + failures[0].message + '）');
    }
    return { refreshedCount: idsToRefresh.length - failures.length, totalCount: totalCount, failedCount: failures.length };
  }

  async function loadInstances() {
    try {
      var instances = await fetchInstances();
      instanceCache._instances = instances;
      // Restore cached torrent counts
      for (var i = 0; i < instances.length; i++) {
        var c = instanceCache[instances[i].id];
        if (c && c.torrent_count !== undefined) {
          instances[i].torrent_count_cache = c.torrent_count;
        }
      }
      renderPanel(instances);
    } catch (err) {
      if (panelList) panelList.innerHTML = '<div class="sidebar-empty">Failed to load instances</div>';
    }
  }

  var REFRESH_ICON_SVG = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>';
  var LOADING_ICON_SVG = '<svg class="spinner" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10" stroke-opacity="0.25"/><path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round"/></svg>';

  function setRefreshLoading(isLoading) {
    if (!refreshBtn) return;
    refreshBtn.disabled = !!isLoading;
    refreshBtn.classList.toggle('spinning', !!isLoading);
    refreshBtn.setAttribute('aria-busy', isLoading ? 'true' : 'false');
    refreshBtn.innerHTML = isLoading ? LOADING_ICON_SVG : REFRESH_ICON_SVG;
  }

  function setupEvents() {
    if (refreshBtn) {
      refreshBtn.addEventListener('click', async function () {
        if (refreshBtn.disabled) return;
        stopAutoRefresh();
        setRefreshLoading(true);
        try {
          var result = await refreshExpanded(true);
          showToast('种子列表已刷新，共 ' + result.totalCount + ' 个种子', 'success');
        } catch (err) {
          showToast(err.message || '刷新种子列表失败', 'error');
        } finally {
          setRefreshLoading(false);
          startAutoRefresh();
        }
      });
    }
    if (panelList) {
      panelList.addEventListener('click', function (e) {
        var header = e.target.closest('[data-action="toggle-instance"]');
        if (header) {
          e.preventDefault();
          var id = parseInt(header.getAttribute('data-instance-id'), 10);
          if (!isNaN(id)) toggleInstance(id);
        }
      });
      panelList.addEventListener('keydown', function (e) {
        if (e.key !== 'Enter' && e.key !== ' ') return;
        var header = e.target.closest('[data-action="toggle-instance"]');
        if (header) {
          e.preventDefault();
          var id = parseInt(header.getAttribute('data-instance-id'), 10);
          if (!isNaN(id)) toggleInstance(id);
        }
      });
    }
  }

  function startAutoRefresh() {
    stopAutoRefresh();
    refreshTimer = setInterval(function () {
      refreshExpanded(false).catch(function () {});
    }, REFRESH_INTERVAL_MS);
  }

  function stopAutoRefresh() {
    if (refreshTimer) {
      clearInterval(refreshTimer);
      refreshTimer = null;
    }
  }

  function init() {
    panelContainer = document.getElementById('sidebar-torrent-panel');
    panelList = document.getElementById('sidebar-torrent-panel-list');
    refreshBtn = document.getElementById('sidebar-refresh-btn');
    if (!panelList || !refreshBtn) return;

    setupEvents();
    loadInstances();
    startAutoRefresh();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }


  async function addTorrent(instanceId, payload) {
    return await apiRequest('/api/v1/instances/' + instanceId + '/torrents/add', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  // Add Torrent Form (supports multiple per-instance embedded forms + standalone page)
  document.querySelectorAll('.add-torrent-form').forEach(function (atForm) {
    var msgEl = atForm.querySelector('[data-at-message]');
    var btn = atForm.querySelector('[data-at-submit]');
    var showMsg = function (t, type) {
      if (!msgEl) return;
      msgEl.textContent = t;
      msgEl.className = 'form-message ' + (type === 'error' ? 'at-msg-error' : type === 'success' ? 'at-msg-success' : 'at-msg-info');
      msgEl.style.color = type === 'error' ? 'var(--err)' : 'var(--ink-soft)';
    };
    atForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var fd = new FormData(atForm);
      var id = parseInt(atForm.dataset.instance || fd.get('instance_id'), 10);
      if (!id) { showMsg('请选择实例', 'error'); return; }
      var url = fd.get('urls').trim();
      if (!url) { showMsg('请输入种子链接', 'error'); return; }
      if (btn) btn.disabled = true;
      showMsg('正在添加...', 'info');
      var ul = parseFloat(fd.get('upload_limit_speed'));
      var dl = parseFloat(fd.get('download_limit_speed'));
      addTorrent(id, {
        urls: url,
        savepath: fd.get('savepath') || '',
        upload_limit_speed: isNaN(ul) ? 80.0 : ul,
        download_limit_speed: isNaN(dl) ? 80.0 : dl
      }).then(function () {
        showMsg('添加成功', 'success');
        atForm.querySelector('[name="urls"]').value = '';
      }).catch(function (err) {
        showMsg(err.message || '添加失败', 'error');
      }).finally(function () {
        if (btn) btn.disabled = false;
      });
    });
  });

  // Expose for external usage
  window.updateTrafficStats = updateTrafficStats;
  window.formatSpeed = formatSpeed;
  window.fetchTransferInfo = fetchTransferInfo;
})();

// Staggered entrance animations for data-animate elements
function initStaggerAnimations() {
  document.querySelectorAll('[data-animate]').forEach((el, i) => {
    el.style.setProperty('--stagger', Math.min(i, 20));
  });
}
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initStaggerAnimations);
} else {
  initStaggerAnimations();
}
