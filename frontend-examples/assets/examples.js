(function () {
  var examples = [
    { id: '01', slug: 'glass-air', title: '澄空', note: '轻盈毛玻璃与缓慢光晕，适合需要呼吸感的控制台。', page: '总览', family: 'glass', tags: ['Glassmorphism', 'Airy', 'Overview'] },
    { id: '02', slug: 'swiss-ledger', title: '瑞士账本', note: '严格网格与黑色规则线，把实例表排成一份账本。', page: '实例', family: 'editorial', tags: ['Swiss', 'Ledger', 'Table'] },
    { id: '03', slug: 'oled-terminal', title: '暗夜终端', note: 'OLED 黑、等宽字体与扫描线，调度器像一段启动日志。', page: '调度', family: 'terminal', tags: ['Terminal', 'OLED', 'Console'] },
    { id: '04', slug: 'paper-issue', title: '纸面周报', note: '报纸排版、衬线正文与首字下沉，把数据写成一份简报。', page: '报告', family: 'editorial', tags: ['Newspaper', 'Report', 'Serif'] },
    { id: '05', slug: 'studio-warm', title: '暖光工作室', note: '陶土色与奶油底，把节点详情做成一件产品。', page: '详情', family: 'minimal', tags: ['Studio', 'Warm', 'Detail'] },
    { id: '06', slug: 'bento-ops', title: '方块总览', note: '模块化 Bento 网格，一眼看完编队、队列与活动。', page: '总览', family: 'minimal', tags: ['Bento', 'Modular', 'Ops'] },
    { id: '07', slug: 'constellation', title: '星图', note: '深空节点网络，用光点与连线表达连接状态。', page: '网络', family: 'dark', tags: ['Network', 'Constellation', 'Dark'] },
    { id: '08', slug: 'brutal-signal', title: '信号', note: '粗边、硬阴影与高饱和色，把异常信号摆上桌面。', page: '警报', family: 'editorial', tags: ['Brutalist', 'Signals', 'Alert'] },
    { id: '09', slug: 'neu-touch', title: '触感', note: '柔和立体与内凹输入，设置页有真实的按压反馈。', page: '设置', family: 'minimal', tags: ['Neumorphism', 'Tactile', 'Settings'] },
    { id: '10', slug: 'command-deck', title: '命令台', note: '居中命令面板，键盘优先，适合高频操作者。', page: '命令', family: 'dark', tags: ['Command', 'Keyboard', 'Dark'] },
    { id: '11', slug: 'archive-room', title: '档案室', note: '文件树与日志卡片，像整理一间安静的档案室。', page: '日志', family: 'data', tags: ['Archive', 'Files', 'Logs'] },
    { id: '12', slug: 'week-field', title: '周历', note: '纸张周历与彩色计划块，调度时间变得可以触摸。', page: '排程', family: 'minimal', tags: ['Calendar', 'Week', 'Plan'] },
    { id: '13', slug: 'heat-room', title: '热力', note: '按小时铺开的执行热力图，密集时段一眼可见。', page: '分析', family: 'data', tags: ['Heatmap', 'Matrix', 'Analytics'] },
    { id: '14', slug: 'field-notes', title: '现场笔记', note: '横线纸、手写体与便利贴，像巡线时留下的记录。', page: '巡检', family: 'editorial', tags: ['Notebook', 'Checklist', 'Hand'] },
    { id: '15', slug: 'magazine-lux', title: '大刊', note: '黑金衬线与超大标题，把健康度写成一张封面。', page: '摘要', family: 'editorial', tags: ['Magazine', 'Luxury', 'Cover'] },
    { id: '16', slug: 'inbox-light', title: '收件箱', note: '极简邮件式队列，把需要处理的事按轻重排好。', page: '队列', family: 'minimal', tags: ['Inbox', 'Queue', 'Light'] },
    { id: '17', slug: 'split-ink', title: '双面', note: '一半计划、一半执行，中间的线把节奏分开。', page: '对比', family: 'minimal', tags: ['Split', 'Compare', 'Dual'] },
    { id: '18', slug: 'dense-grid', title: '仪表舱', note: '高密度表格与状态芯片，适合专业操作者快速扫读。', page: '清单', family: 'data', tags: ['Dense', 'Table', 'Ops'] },
    { id: '19', slug: 'blueprint', title: '蓝图', note: '技术图纸、细线与标注，把调度架构画成一张施工图。', page: '架构', family: 'data', tags: ['Blueprint', 'Diagram', 'Tech'] },
    { id: '20', slug: 'liquid-dark', title: '液态暗面', note: '暗色玻璃与流动光斑，保留毛玻璃的轻盈也增加夜感。', page: '总览', family: 'glass', tags: ['Liquid', 'Dark Glass', 'Cinema'] }
  ];

  var nodes = [
    ['家用 NAS', 'nas.local:8080', '在线', 'good', 78, 42],
    ['远程存储 A', 'qb-a.example.net', '在线', 'good', 61, 36],
    ['影音服务器', 'media.example.net', '等待', 'warn', 34, 21],
    ['远程存储 B', 'qb-b.example.net', '异常', 'bad', 12, 0],
    ['测试节点', 'test-node.local:8080', '在线', 'good', 48, 128]
  ];

  var events = [
    ['远程存储 A', '强制做种完成', '36 个种子 · 延迟 43 ms', 'good', '刚刚'],
    ['家用 NAS', '连接测试通过', 'WebUI 响应稳定', 'good', '12 分钟前'],
    ['远程存储 B', '连接失败', '请求超时，需要检查证书', 'bad', '28 分钟前'],
    ['影音服务器', '调度已暂停', '等待手动开启策略', 'warn', '1 小时前']
  ];

  function icon(name) {
    var p = {
      arrow: '<path d="M5 12h14M13 6l6 6-6 6"/>',
      plus: '<path d="M12 5v14M5 12h14"/>',
      refresh: '<path d="M20 11a8 8 0 1 0 1 4"/><path d="M20 4v7h-7"/>',
      check: '<path d="m5 12 4 4L19 6"/>',
      search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',
      server: '<rect x="3" y="4" width="18" height="6" rx="1"/><rect x="3" y="14" width="18" height="6" rx="1"/><path d="M7 7h.01M7 17h.01"/>',
      folder: '<path d="M3 6a2 2 0 0 1 2-2h5l2 2h7a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
      clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
      alert: '<path d="M12 3 2 20h20L12 3z"/><path d="M12 10v4"/><path d="M12 17h.01"/>',
      play: '<path d="m7 4 13 8-13 8z"/>',
      pause: '<path d="M8 5v14M16 5v14"/>',
      settings: '<circle cx="12" cy="12" r="3"/><path d="M19 12a7 7 0 0 0-.1-1.2l2-1.5-2-3.4-2.4 1a7 7 0 0 0-2-1.2L14 3h-4l-.5 2.7a7 7 0 0 0-2 1.2l-2.4-1-2 3.4 2 1.5a7 7 0 0 0 0 2.4l-2 1.5 2 3.4 2.4-1a7 7 0 0 0 2 1.2L10 21h4l.5-2.7a7 7 0 0 0 2-1.2l2.4 1 2-3.4-2-1.5c.1-.4.1-.8.1-1.2z"/>',
      send: '<path d="m4 4 16 8-16 8 3-8zM7 12h13"/>',
      download: '<path d="M12 3v12m0 0 4-4m-4 4-4-4"/><path d="M4 21h16"/>',
      dots: '<circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/>',
      grid: '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>'
    };
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + p[name] + '</svg>';
  }

  function miniBrand(e) {
    return '<a class="mini-brand" href="index.html"><span>QB</span><b>qBT / ' + e.id + '</b></a>';
  }

  function backLink() {
    return '<a class="back-link" href="index.html">' + icon('arrow') + ' 20 个方向</a>';
  }

  function shell(cls, content) {
    return '<div class="stage ' + cls + '">' + content + '<div class="toast" role="status"></div></div>';
  }

  function eventList() {
    return events.map(function (x) {
      return '<li class="g1-event reveal"><i class="' + x[3] + '"></i><div><b>' + x[0] + '</b><span>' + x[1] + ' · ' + x[2] + '</span></div><time>' + x[4] + '</time></li>';
    }).join('');
  }

  function nodeRows() {
    return nodes.map(function (n, i) {
      return '<div class="g1-node"><i class="node-pulse ' + n[3] + '"></i><div><b>' + n[0] + '</b><small>' + n[1] + '</small></div><em>' + n[2] + '</em><span class="g1-load"><i style="width:' + n[4] + '%"></i></span></div>';
    }).join('');
  }

  function glassAir(e) {
    return shell('stage-01', `
      <div class="ambient a1"></div><div class="ambient a2"></div><div class="ambient a3"></div>
      <header class="g1-nav glass">${miniBrand(e)}<nav><a class="active">总览</a><a>实例</a><a>调度</a><a>日志</a></nav><div class="g1-actions"><button class="icon-btn" data-refresh aria-label="刷新状态">${icon('refresh')}</button><button class="btn-primary" data-toast="已开始全量做种">${icon('play')} 立即做种</button></div></header>
      <main class="g1-main">
        <section class="g1-hero glass reveal">
          <div><span class="kicker">FLEET OVERVIEW / 2026.08.01</span><h1>一切正常，<em>但仍有 1 个节点需要确认。</em></h1><p>五个节点中四个在线。远程存储 B 已连续两次超时，建议先核对 WebUI 地址。</p><div class="g1-actions-row"><button class="btn-ghost" data-toast="已打开节点详情">查看远程存储 B ${icon('arrow')}</button><button class="btn-primary" data-toast="连接测试已加入队列">测试连接</button></div></div>
          <div class="g1-health tilt"><span>FLEET HEALTH</span><b><i data-count="82">0</i><small>%</small></b><i class="meter"><em style="width:82%"></em></i><small>4 在线 / 5 总计</small></div>
        </section>
        <section class="g1-kpis">
          <article class="glass reveal"><span>在线实例</span><b data-count="04">0</b><small>of 05 discovered</small><i class="mini-bar"><em style="width:80%"></em></i></article>
          <article class="glass reveal"><span>今日执行</span><b data-count="18">0</b><small>次调度动作</small><i class="mini-bar"><em style="width:66%"></em></i></article>
          <article class="glass reveal"><span>平均延迟</span><b>43<small>ms</small></b><small>最近一次连接测试</small><i class="mini-bar"><em style="width:43%"></em></i></article>
          <article class="glass reveal"><span>需要关注</span><b>01</b><small>远程存储 B</small><i class="mini-bar warn"><em style="width:18%"></em></i></article>
        </section>
        <section class="g1-lower">
          <article class="glass panel reveal"><header><b>最近活动</b><button data-toast="已打开全部活动">全部 ${icon('arrow')}</button></header><ul class="g1-events">${eventList()}</ul></article>
          <aside class="glass panel reveal"><header><b>节点负载</b><span>LIVE</span></header>${nodeRows()}</aside>
        </section>
      </main>
    `);
  }

  function swissLedger(e) {
    var rows = nodes.map(function (n, i) {
      return '<tr class="reveal"><td><b>0' + (i + 1) + '</b></td><td><strong>' + n[0] + '</strong><small>' + n[1] + '</small></td><td><span class="s2-status ' + n[3] + '">' + n[2] + '</span></td><td>' + (15 + i * 10) + ' 分钟</td><td>' + n[4] + '%</td><td>' + n[5] + ' 个</td><td><button data-toast="已打开 ' + n[0] + '">' + icon('arrow') + '</button></td></tr>';
    }).join('');
    return shell('stage-02', `
      <header class="s2-top"><div class="s2-brand"><b>QB</b><span>LEDGER / ${e.id}</span></div><nav><a class="active">实例</a><a>调度</a><a>日志</a></nav>${backLink()}</header>
      <main class="s2-main">
        <section class="s2-title"><div><span>INSTANCES / 05</span><h1>编队账本</h1><p>每一行都是一台 qBittorrent，每一列都可以被排序。</p></div><button class="s2-button" data-toast="CSV 已导出">${icon('download')} 导出 CSV</button></section>
        <table class="s2-table"><thead><tr><th>No.</th><th>实例</th><th>状态</th><th>间隔</th><th>负载</th><th>种子</th><th></th></tr></thead><tbody>${rows}</tbody></table>
        <footer class="s2-foot"><span>SUMMARY / 04 ONLINE · 01 WARNING</span><span>LEDGER UPDATED 09:42</span></footer>
      </main>
    `);
  }

  function oledTerminal(e) {
    return shell('stage-03', `
      <div class="t3-scan" aria-hidden="true"></div>
      <header class="t3-top"><span>qbt@control</span><span>SESSION 01 / LOCAL</span>${backLink()}</header>
      <main class="t3-main">
        <section class="t3-window">
          <div class="t3-bar"><i></i><i></i><i></i><b>qbt@control: ~</b><span>bash</span></div>
          <div class="t3-body">
            <p class="t3-muted">qBT reannounce scheduler / boot sequence 2026.08.01</p>
            <p data-type="connect --fleet default"></p>
            <p class="t3-ok">✓ 5 nodes discovered / 4 online / 1 warning</p>
            <p data-type="status --verbose"></p>
            <pre class="t3-art">  ██████╗ ██████╗ ████████╗
  ██╔═══██╗██╔══██╗╚══██╔══╝
  ██║   ██║██████╔╝   ██║
  ╚██████╔╝██║  ██║   ██║</pre>
            <dl><div><dt>fleet.health</dt><dd>82%</dd></div><div><dt>scheduler</dt><dd class="t3-ok">running</dd></div><div><dt>seed.count</dt><dd>128</dd></div><div><dt>last.run</dt><dd>00:14:32</dd></div></dl>
            <p data-type="inspect remote-storage-b"></p>
            <p class="t3-warn">! timeout after 3000ms / retry suggested</p>
            <form class="t3-prompt"><span>❯</span><input aria-label="终端命令" placeholder="输入命令，例如 run --all" autocomplete="off"><button type="submit">↵</button><i class="t3-cursor"></i></form>
          </div>
        </section>
        <aside class="t3-side"><span>COMMANDS</span><button data-command="status --verbose">status --verbose</button><button data-command="nodes --watch">nodes --watch</button><button data-command="run --all">run --all</button><button data-command="help">help</button><div><small>EXIT CODE</small><b>0</b><small>last command completed</small></div></aside>
      </main>
    `);
  }

  function paperIssue(e) {
    return shell('stage-04', `
      <header class="p4-mast"><div><span>SATURDAY / AUGUST 01, 2026</span><h1>THE qB DAILY</h1><span>NODE EDITION · VOL. ${e.id}</span></div>${backLink()}</header>
      <main class="p4-main">
        <div class="p4-kicker">A QUIET REPORT ON A NOISY FLEET</div>
        <article class="p4-hero reveal">
          <div><h2>五个节点，<em>一个安静的早晨。</em></h2><p class="p4-drop">调度器在 09:42 开始今天的第一轮巡检。四个节点在线，一个节点等待确认。远程存储 B 的请求在 3000ms 后超时，其余节点保持稳定。</p></div>
          <aside><span>“</span><blockquote>稳定不是没有变化，而是每个变化都有自己的位置。</blockquote><small>CONTROL ROOM OBSERVATION</small></aside>
        </article>
        <section class="p4-cols">
          <article class="reveal"><span>DISPATCHES / 01</span><ul>${events.map(function (x) { return '<li><i class="' + x[3] + '"></i><b>' + x[1] + '</b><small>' + x[0] + ' · ' + x[4] + '</small></li>'; }).join('')}</ul></article>
          <article class="reveal"><span>THE NUMBERS</span><div class="p4-numbers"><b>18</b><b>128</b><b>43<small>ms</small></b></div><p>今日执行、当前种子与平均延迟，本周都保持在合理区间。</p></article>
          <article class="reveal"><span>MARGIN NOTE</span><blockquote>“每个异常都值得一个清楚的句子。”</blockquote><button data-toast="已打开完整运行报告">阅读完整报告 ${icon('arrow')}</button></article>
        </section>
        <footer class="p4-foot">PAGE 01 / STATIC STUDY / 2026.08</footer>
      </main>
    `);
  }

  function studioWarm(e) {
    return shell('stage-05', `
      <header class="s5-nav"><div class="s5-brand">QB<span> / STUDIO</span></div><nav><a class="active">实例</a><a>运行</a><a>报告</a></nav>${backLink()}</header>
      <main class="s5-main">
        <section class="s5-visual"><div class="s5-frame tilt"><span class="s5-sun"></span><span class="s5-orbit o1"></span><span class="s5-orbit o2"></span><b>42</b><small>ACTIVE SEEDS</small></div><span class="s5-tag">LIVE / NAS</span></section>
        <section class="s5-detail reveal"><span class="kicker">INSTANCE / 01</span><h1>家用 NAS</h1><p>这台节点负责本地媒体库的做种保持。过去 24 小时连接稳定，平均响应 43ms。</p><dl><div><dt>地址</dt><dd>nas.local:8080</dd></div><div><dt>状态</dt><dd class="good">在线</dd></div><div><dt>间隔</dt><dd>15 分钟</dd></div><div><dt>种子</dt><dd>42 active</dd></div></dl><div class="s5-actions"><button class="s5-primary" data-toast="强制做种已开始">${icon('play')} 立即做种</button><button class="s5-ghost" data-toast="连接测试已排队">测试连接</button></div></section>
      </main>
    `);
  }

  function bentoOps(e) {
    return shell('stage-06', `
      <header class="b6-top"><div class="b6-brand">QB<span> / OPS</span></div><nav><a class="active">总览</a><a>实例</a><a>活动</a></nav>${backLink()}</header>
      <main class="b6-main">
        <header class="b6-head"><div><span class="kicker">OPERATIONS / ${e.id}</span><h1>今天的编队，<em>一眼看完。</em></h1></div><button class="b6-button" data-toast="节点表单已打开">${icon('plus')} 添加节点</button></header>
        <section class="b6-grid">
          <article class="b6-tile b6-health reveal"><span>Fleet health</span><b><i data-count="82">0</i><small>%</small></b><p>较昨日稳定 <b>+8.4%</b></p></article>
          <article class="b6-tile b6-online reveal"><span>Online nodes</span><b>04</b><p>of 05 discovered</p></article>
          <article class="b6-tile b6-queue reveal"><span>Queue depth / today</span><div class="b6-bars"><i style="height:36%"></i><i style="height:64%"></i><i style="height:48%"></i><i style="height:84%"></i><i style="height:59%"></i><i style="height:92%"></i></div><footer><small>06:00</small><b>128 seeds</b><small>21:00</small></footer></article>
          <article class="b6-tile b6-activity reveal"><span>Recent activity</span><ul>${events.slice(0, 3).map(function (x) { return '<li><i class="' + x[3] + '"></i><b>' + x[1] + '</b><small>' + x[0] + ' · ' + x[4] + '</small></li>'; }).join('')}</ul></article>
          <article class="b6-tile b6-nodes reveal"><span>Instance load</span>${nodes.slice(0, 4).map(function (n) { return '<div><i class="node-pulse ' + n[3] + '"></i><b>' + n[0] + '</b><em>' + n[2] + '</em></div>'; }).join('')}</article>
          <article class="b6-tile b6-add reveal" data-toast="快速添加面板已打开"><b>+</b><span>添加一个节点</span><small>从这里开始连接</small></article>
        </section>
      </main>
    `);
  }

  function constellation(e) {
    var positions = [[130, 130], [620, 90], [620, 380], [120, 390], [390, 70]];
    var buttons = nodes.map(function (n, i) {
      return '<button class="s7-node n' + (i + 1) + (i === 0 ? ' active' : '') + '" style="left:' + positions[i][0] + 'px;top:' + positions[i][1] + 'px" data-node="' + i + '" aria-label="' + n[0] + '"><i></i><span>' + (n[0].slice(0, 3)) + '</span></button>';
    }).join('');
    var lines = positions.map(function (p, i) {
      return '<path d="M380 260 L' + p[0] + ' ' + p[1] + '"></path>';
    }).join('');
    return shell('stage-07', `
      <header class="s7-top"><span>NODE CONSTELLATION / ${e.title}</span>${backLink()}</header>
      <main class="s7-main">
        <section class="s7-map reveal"><svg class="s7-lines" viewBox="0 0 760 520" preserveAspectRatio="none" aria-hidden="true">${lines}</svg>${buttons}<div class="s7-core"><b data-count="82">0</b><small>%</small><span>FLEET HEALTH</span></div><span class="s7-label l1">43 ms</span><span class="s7-label l2">36 seeds</span><span class="s7-label l3">timeout</span></section>
        <aside class="s7-detail reveal"><span>SELECTED NODE</span><h2 data-node-name>家用 NAS</h2><p data-node-note>本地媒体库节点，连接稳定。</p><dl data-node-meta></dl><button data-toast="连接测试已开始">测试连接 ${icon('arrow')}</button></aside>
      </main>
    `);
  }

  function brutalSignal(e) {
    return shell('stage-08', `
      <header class="s8-top"><span>ALERT DESK / ${e.id}</span>${backLink()}</header>
      <main class="s8-main">
        <div class="s8-title"><span>OPEN SIGNALS</span><h1>需要处理<br><b>01</b> 个信号</h1></div>
        <section class="s8-cards">
          <article class="s8-card critical reveal"><span>CRITICAL</span><h2>远程存储 B</h2><p>连续两次请求超时，WebUI 地址需要核对。</p><button data-toast="已创建处理任务">处理任务 →</button></article>
          <article class="s8-card warning reveal"><span>WARNING</span><h2>影音服务器</h2><p>调度策略处于暂停状态，等待手动恢复。</p><button data-toast="已打开调度设置">恢复调度 →</button></article>
          <article class="s8-card ok reveal"><span>RESOLVED</span><h2>家用 NAS</h2><p>连接测试已通过，响应 43ms。</p><button data-toast="已打开运行记录">查看记录 →</button></article>
        </section>
      </main>
    `);
  }

  function neuTouch(e) {
    return shell('stage-09', `
      <header class="s9-top"><div class="s9-brand">QB<span> / SETTINGS</span></div>${backLink()}</header>
      <main class="s9-main">
        <div class="s9-head reveal"><span class="kicker">SETTINGS / ${e.id}</span><h1>实例设置</h1><p>连接参数与调度策略，放在同一个安静的抽屉里。</p></div>
        <form class="s9-form" data-neu-form>
          <section class="neu-card reveal"><header><b>连接</b><span>01</span></header><label><span>实例名称</span><input type="text" value="家用 NAS"></label><label><span>WebUI 地址</span><input type="text" value="http://nas.local:8080"></label><label><span>做种间隔</span><div class="neu-range"><input type="range" min="5" max="120" value="15"><b class="range-value">15 分钟</b></div></label></section>
          <section class="neu-card reveal"><header><b>策略</b><span>02</span></header><label class="neu-toggle"><input type="checkbox" checked><i></i><span>启用定时做种</span></label><label class="neu-toggle"><input type="checkbox" checked><i></i><span>失败后自动重试</span></label><label class="neu-toggle"><input type="checkbox"><i></i><span>忽略 TLS 证书</span></label></section>
          <section class="neu-card reveal"><header><b>通知</b><span>03</span></header><label class="neu-toggle"><input type="checkbox" checked><i></i><span>失败时发送提醒</span></label><label class="neu-toggle"><input type="checkbox"><i></i><span>每日摘要</span></label></section>
          <div class="neu-actions reveal"><button class="neu-button" type="submit">保存更改</button><button class="neu-button ghost" type="button" data-toast="连接测试成功">测试连接</button></div>
        </form>
      </main>
    `);
  }

  function commandDeck(e) {
    return shell('stage-10', `
      <header class="s10-top"><span>COMMAND DECK / ${e.id}</span>${backLink()}</header>
      <main class="s10-main">
        <div class="s10-palette reveal">
          <div class="s10-search"><span>⌘</span><input data-command-search placeholder="搜索动作、实例或日志" aria-label="搜索命令"><kbd>ESC</kbd></div>
          <div class="s10-results">
            <div class="s10-group"><span>建议动作</span>
              <button data-toast="已执行：检查远程存储 B"><i>${icon('alert')}</i><div><b>检查远程存储 B</b><small>解决连续超时的连接问题</small></div><kbd>↵</kbd></button>
              <button data-toast="已执行：全量强制做种"><i>${icon('play')}</i><div><b>运行全量强制做种</b><small>在 5 个节点上执行当前策略</small></div><kbd>↵</kbd></button>
              <button data-toast="已打开今日执行日志"><i>${icon('clock')}</i><div><b>打开今日执行日志</b><small>查看过去 24 小时的全部活动</small></div><kbd>↵</kbd></button>
            </div>
            <div class="s10-group"><span>实例</span>
              ${nodes.map(function (n) { return '<button data-toast="已打开 ' + n[0] + '"><i>' + icon('server') + '</i><div><b>' + n[0] + '</b><small>' + n[1] + '</small></div><kbd>↵</kbd></button>'; }).join('')}
            </div>
          </div>
          <footer class="s10-foot"><span>↑↓ 选择</span><span>↵ 执行</span><span>esc 关闭</span></footer>
        </div>
      </main>
    `);
  }

  function archiveRoom(e) {
    return shell('stage-11', `
      <header class="s11-top"><div class="s11-crumb">ARCHIVE / RUNS / 2026</div>${backLink()}</header>
      <main class="s11-main">
        <aside class="s11-tree"><span>ARCHIVE</span><nav><a class="active">${icon('folder')} 所有日志 <b>05</b></a><a>${icon('folder')} 成功 <b>18</b></a><a>${icon('folder')} 异常 <b>01</b></a><a>${icon('folder')} 已归档 <b>12</b></a></nav><div><span>STORAGE USED</span><b>68%</b><i><em style="width:68%"></em></i><small>6.8 TB of 10 TB</small></div></aside>
        <section class="s11-list">
          <header><div><span class="kicker">ARCHIVE / ${e.id}</span><h1>${e.title}</h1><p>按时间归档的执行记录，每一份都可以再打开。</p></div><button data-toast="上传入口已打开">${icon('plus')} 上传</button></header>
          ${events.concat(events.slice(0, 1)).map(function (x, i) { return '<article class="s11-file reveal" data-toast="已打开 ' + x[0] + '"><i class="file-icon ' + x[3] + '">' + icon(i % 2 ? 'server' : 'folder') + '</i><div><b>' + x[1] + ' · ' + x[0] + '</b><small>' + x[2] + '</small></div><time>' + x[4] + '</time></article>'; }).join('')}
        </section>
      </main>
    `);
  }

  function weekField(e) {
    var days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
    var slots = [[], ['连接测试', '09:00'], [], ['媒体同步', '15:00'], [], ['全量做种', '18:00'], []];
    return shell('stage-12', `
      <header class="s12-top"><div class="s12-brand">QB<span> / WEEK</span></div><nav><a class="active">周历</a><a>月历</a><a>运行</a></nav>${backLink()}</header>
      <main class="s12-main">
        <aside class="s12-side reveal"><span class="kicker">SCHEDULE / ${e.id}</span><h1>${e.title}</h1><p>本周有四组计划任务，忙碌集中在傍晚。</p><div class="s12-stat"><span>ACTIVE</span><b>04</b><small>schedules</small></div><button data-toast="排程表单已打开">${icon('plus')} 添加排程</button></aside>
        <section class="s12-cal reveal">
          <div class="s12-head">WEEK 31 / 27 JUL — 02 AUG 2026</div>
          <div class="s12-row">${days.map(function (d, di) { return '<div class="s12-day' + (di === 5 ? ' today' : '') + '"><small>' + d + '</small><b>' + (27 + di) + '</b>' + (slots[di][0] ? '<span class="s12-slot s' + (di % 3) + '"><b>' + slots[di][0] + '</b><small>' + slots[di][1] + '</small></span>' : '<i class="s12-empty"></i>') + '</div>'; }).join('')}</div>
        </section>
      </main>
    `);
  }

  function heatRoom(e) {
    var cells = '';
    for (var i = 0; i < 84; i += 1) {
      cells += '<button class="s13-cell l' + ((i * 7 + 3) % 5) + '" data-toast="已查看 ' + (i % 12 + 6) + ':00 时段"></button>';
    }
    return shell('stage-13', `
      <header class="s13-top"><span>ACTIVITY MATRIX / ${e.id}</span>${backLink()}</header>
      <main class="s13-main">
        <header class="s13-head reveal"><div><span class="kicker">ANALYTICS / ${e.id}</span><h1>${e.title}</h1><p>颜色越深，代表该时段的执行越密集。</p></div><div class="s13-total"><small>TOTAL RUNS</small><b data-count="128">0</b><span>+12.4%</span></div></header>
        <section class="s13-board reveal">
          <div class="s13-days"><span>周一</span><span>周二</span><span>周三</span><span>周四</span><span>周五</span><span>周六</span><span>周日</span></div>
          <div class="s13-matrix">${cells}</div>
          <div class="s13-hours"><span>06:00</span><span>09:00</span><span>12:00</span><span>15:00</span><span>18:00</span><span>21:00</span></div>
        </section>
        <footer class="s13-key">LESS <i class="l0"></i><i class="l1"></i><i class="l2"></i><i class="l3"></i><i class="l4"></i> MORE <b>hover a cell for detail</b></footer>
      </main>
    `);
  }

  function fieldNotes(e) {
    return shell('stage-14', `
      <header class="s14-top"><span>FIELD NOTE ${e.id} / 08.01.26</span>${backLink()}</header>
      <main class="s14-main">
        <header class="s14-head reveal"><span>today's observation</span><h1>${e.title}</h1><p>现场记录：节点在晨间批次里保持稳定，只有一处连接需要跟进。</p></header>
        <section class="s14-notes">
          <article class="s14-note reveal"><b>01</b><h2>运行状态</h2><p>调度器在线。远程存储 A 完成 36 个种子的强制做种，NAS 响应 43ms。</p><em>keep watching</em></article>
          <article class="s14-note warn reveal"><b>02</b><h2>需要跟进</h2><p>远程存储 B 连续两次请求超时。先确认 WebUI，再重启测试。</p><button data-toast="已标记为待处理">标记待处理</button></article>
          <article class="s14-note reveal"><b>03</b><h2>下一次巡检</h2><p>今天 18:00 · 全量强制做种 · 预计 15 分钟。</p><small>□ cert · □ url · □ schedule</small></article>
        </section>
        <section class="s14-check reveal"><header><span>CHECKLIST</span><b>03 / 04 done</b></header><ul><li class="done" data-check>${icon('check')}<span>确认调度器在线</span></li><li class="done" data-check>${icon('check')}<span>检查远程存储 A 的连接</span></li><li class="done" data-check>${icon('check')}<span>查看今日执行日志</span></li><li data-check><i></i><span>核对远程存储 B 的证书</span></li></ul></section>
      </main>
    `);
  }

  function magazineLux(e) {
    return shell('stage-15', `
      <header class="s15-nav"><span>qBT / REPORT</span><span>NO. ${e.id} / 2026</span>${backLink()}</header>
      <main class="s15-main">
        <section class="s15-hero reveal">
          <div><p>THE FLEET IN 2026</p><h1>状态<br><em>静默</em></h1></div>
          <div class="s15-number"><small>FLEET HEALTH</small><b><i data-count="82">0</i><span>%</span></b><p>四个节点在线，一个节点需要确认。</p></div>
        </section>
        <section class="s15-index reveal">
          <div><small>01 / EXECUTIVE SUMMARY</small><p>本周 128 次种子操作，126 次完成。</p></div>
          <div><small>02 / AUDIT TRAIL</small><p>唯一持续关注项是远程存储 B 的网络连接。</p></div>
          <div><small>03 / NEXT WEEK</small><p>保持当前间隔，周四加入一次全量做种。</p></div>
        </section>
        <footer class="s15-foot">STATIC STUDY / PREPARED BY CONTROL ROOM</footer>
      </main>
    `);
  }

  function inboxLight(e) {
    return shell('stage-16', `
      <header class="s16-top"><div class="s16-brand">QB<span> / INBOX</span></div>${backLink()}</header>
      <main class="s16-main">
        <aside class="s16-side reveal"><span>QUEUE</span><nav><a class="active">全部 <b>03</b></a><a>需要确认 <b>01</b></a><a>已完成 <b>02</b></a><a>稍后处理 <b>00</b></a></nav><div><span>QUEUE HEALTH</span><b>72</b><small>任务正在顺序流动</small></div></aside>
        <section class="s16-list">
          <header class="s16-head reveal"><div><span class="kicker">ATTENTION / ${e.id}</span><h1>${e.title}</h1><p>需要处理的事不多，刚好可以在一个早上读完。</p></div><button data-toast="已刷新队列" data-refresh>${icon('refresh')} 刷新</button></header>
          ${['high', 'medium', 'low'].map(function (level, i) { var item = [['检查远程存储 B', '连接连续两次超时，确认地址和证书后重新测试。', 'HIGH · due now'], ['恢复影音服务器调度', '当前策略处于暂停状态。', 'MEDIUM · in 2h'], ['补齐测试节点间隔', '为测试节点设置定时任务。', 'LOW · today']][i]; return '<article class="s16-item reveal"><i class="s16-level ' + level + '"></i><div><small>' + item[2] + '</small><h2>' + item[0] + '</h2><p>' + item[1] + '</p></div><button data-toast="已处理：' + item[0] + '">处理 ' + icon('arrow') + '</button></article>'; }).join('')}
        </section>
      </main>
    `);
  }

  function splitInk(e) {
    return shell('stage-17', `
      <main class="s17-main">
        <section class="s17-panel s17-dark reveal"><span>PLANNED / 07.31 — 08.07</span><h1><i data-count="18">0</i></h1><p>本周计划执行 18 次调度动作，包含 1 次全量做种。</p><ul><li><i></i>每日连接测试 <b>07</b></li><li><i></i>强制做种批次 <b>10</b></li><li><i></i>全量巡检 <b>01</b></li></ul></section>
        <div class="s17-divider" aria-hidden="true"></div>
        <section class="s17-panel s17-light reveal"><span>EXECUTED / AS OF 08.01</span><h1><i data-count="16">0</i></h1><p>已按计划完成 16 次，剩余 2 次将在今天傍晚执行。</p><ul><li><i class="good"></i>连接测试 <b>06 / 07</b></li><li><i class="good"></i>做种批次 <b>09 / 10</b></li><li><i class="warn"></i>全量巡检 <b>01 / 01</b></li></ul></section>
      </main>
    `);
  }

  function denseGrid(e) {
    return shell('stage-18', `
      <header class="s18-top"><div class="s18-brand">QB<span> / INVENTORY</span></div><div><span>UPDATED 09:42:18</span>${backLink()}</div></header>
      <main class="s18-main">
        <header class="s18-head reveal"><div><span class="kicker">INVENTORY / ${e.id}</span><h1>${e.title}</h1><p>全部实例、间隔、负载与最近错误，集中在同一张表里。</p></div><button data-toast="CSV 已导出">${icon('download')} 导出</button></header>
        <div class="s18-table-wrap reveal"><table class="s18-table"><thead><tr><th>实例</th><th>地址</th><th>状态</th><th>间隔</th><th>负载</th><th>种子</th><th>成功率</th><th>最近错误</th><th></th></tr></thead><tbody>${nodes.map(function (n, i) { return '<tr><td><b>' + n[0] + '</b></td><td><span class="mono">' + n[1] + '</span></td><td><i class="s18-status ' + n[3] + '"></i>' + n[2] + '</td><td>' + (15 + i * 10) + 'm</td><td><span class="s18-load"><i style="width:' + n[4] + '%"></i></span></td><td>' + n[5] + '</td><td>98.4%</td><td><span class="s18-err">' + (n[3] === 'bad' ? 'timeout' : '-') + '</span></td><td><button data-toast="已打开 ' + n[0] + '">' + icon('arrow') + '</button></td></tr>'; }).join('')}</tbody></table></div>
      </main>
    `);
  }

  function blueprint(e) {
    return shell('stage-19', `
      <header class="s19-top"><div><span>SCHEDULER ARCHITECTURE</span><small>DWG. QB-2026-08</small></div>${backLink()}</header>
      <main class="s19-main">
        <header class="s19-head reveal"><span class="kicker">ARCHITECTURE / ${e.id}</span><h1>${e.title}</h1><p>调度器、执行器与 qBittorrent 节点之间的连接方式。</p></header>
        <section class="s19-board reveal">
          <div class="s19-box scheduler"><small>01 / SCHEDULER</small><b>APScheduler</b><span>每 15 分钟触发</span></div>
          <div class="s19-box worker"><small>02 / WORKER</small><b>Reannounce Worker</b><span>分批获取 hash 并执行</span></div>
          <div class="s19-box api"><small>03 / API</small><b>qB WebUI v2</b><span>HTTP + JSON</span></div>
          <div class="s19-box node-a"><small>NODE</small><b>家用 NAS</b><span>nas.local:8080</span></div>
          <div class="s19-box node-b"><small>NODE</small><b>远程存储 A</b><span>qb-a.example.net</span></div>
          <div class="s19-box node-c"><small>NODE</small><b>远程存储 B</b><span>qb-b.example.net</span></div>
          <i class="s19-line l1"></i><i class="s19-line l2"></i><i class="s19-line l3"></i><i class="s19-line l4"></i>
          <span class="s19-note n1">4.x / 5.x</span><span class="s19-note n2">batch 50</span><span class="s19-note n3">tls optional</span>
        </section>
      </main>
    `);
  }

  function liquidDark(e) {
    return shell('stage-20', `
      <div class="liquid lq-a"></div><div class="liquid lq-b"></div><div class="liquid lq-c"></div>
      <header class="s20-nav glass-dark">${miniBrand(e)}<nav><a class="active">总览</a><a>实例</a><a>分析</a></nav>${backLink()}</header>
      <main class="s20-main">
        <section class="s20-hero glass-dark reveal">
          <div><span class="kicker">FLEET / LIVE</span><h1>状态，<em>保持清醒。</em></h1><p>四个节点在线，一个节点等待确认。所有信号都在同一块玻璃后面。</p><div class="s20-actions"><button class="s20-primary" data-toast="连接测试已开始">${icon('play')} 测试连接</button><button class="s20-ghost" data-toast="已打开调度设置">${icon('settings')} 调度设置</button></div></div>
          <div class="s20-meter tilt"><span>FLEET HEALTH</span><b><i data-count="82">0</i><small>%</small></b><i class="meter"><em style="width:82%"></em></i><small>4 online / 5 total</small></div>
        </section>
        <section class="s20-cards">
          <article class="s20-card glass-dark reveal"><span>今日执行</span><b data-count="18">0</b><small>18 runs / 2 remaining</small><i class="s20-spark"><em style="width:72%"></em></i></article>
          <article class="s20-card glass-dark reveal"><span>平均延迟</span><b>43<small>ms</small></b><small>last connection test</small><i class="s20-spark"><em style="width:43%"></em></i></article>
          <article class="s20-card glass-dark reveal"><span>需要关注</span><b>01</b><small>remote storage B</small><i class="s20-spark warn"><em style="width:18%"></em></i></article>
        </section>
      </main>
    `);
  }

  var templates = {
    glassAir: glassAir,
    swissLedger: swissLedger,
    oledTerminal: oledTerminal,
    paperIssue: paperIssue,
    studioWarm: studioWarm,
    bentoOps: bentoOps,
    constellation: constellation,
    brutalSignal: brutalSignal,
    neuTouch: neuTouch,
    commandDeck: commandDeck,
    archiveRoom: archiveRoom,
    weekField: weekField,
    heatRoom: heatRoom,
    fieldNotes: fieldNotes,
    magazineLux: magazineLux,
    inboxLight: inboxLight,
    splitInk: splitInk,
    denseGrid: denseGrid,
    blueprint: blueprint,
    liquidDark: liquidDark
  };

  function reveal(root) {
    var items = root.querySelectorAll('.reveal');
    if (!('IntersectionObserver' in window)) {
      items.forEach(function (item) { item.classList.add('is-visible'); });
      return;
    }
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: .08 });
    items.forEach(function (item, i) { item.style.transitionDelay = Math.min(i * 40, 280) + 'ms'; observer.observe(item); });
  }

  function counters(root) {
    root.querySelectorAll('[data-count]').forEach(function (el) {
      var target = Number(el.dataset.count);
      var pad = el.dataset.count.length > 1 && el.dataset.count.indexOf('0') === 0;
      var start = performance.now();
      function tick(now) {
        var p = Math.min((now - start) / 850, 1);
        var val = Math.round(target * (1 - Math.pow(1 - p, 3)));
        el.textContent = pad ? String(val).padStart(2, '0') : String(val);
        if (p < 1) requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
    });
  }

  function toast(root, text) {
    var el = root.querySelector('.toast');
    if (!el) return;
    el.textContent = text;
    el.classList.add('visible');
    clearTimeout(root.__toast);
    root.__toast = setTimeout(function () { el.classList.remove('visible'); }, 2200);
  }

  function tilt(root) {
    if (!window.matchMedia('(hover:hover)').matches) return;
    root.querySelectorAll('.tilt').forEach(function (el) {
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width - .5;
        var y = (e.clientY - r.top) / r.height - .5;
        el.style.transform = 'perspective(900px) rotateX(' + (-y * 5) + 'deg) rotateY(' + (x * 6) + 'deg) translateY(-3px)';
      });
      el.addEventListener('pointerleave', function () { el.style.transform = ''; });
    });
  }

  function typeLines(root) {
    var lines = Array.prototype.slice.call(root.querySelectorAll('[data-type]'));
    if (!lines.length) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      lines.forEach(function (line) { line.textContent = line.dataset.type; });
      return;
    }
    var index = 0, char = 0;
    var timer = setInterval(function () {
      var line = lines[index];
      if (!line) { clearInterval(timer); return; }
      char += 1;
      line.textContent = line.dataset.type.slice(0, char);
      if (char >= line.dataset.type.length) { index += 1; char = 0; }
    }, 14);
  }

  function bind(root) {
    reveal(root);
    counters(root);
    tilt(root);
    typeLines(root);

    root.querySelectorAll('[data-toast]').forEach(function (el) {
      el.addEventListener('click', function () { toast(root, this.dataset.toast); });
    });

    root.querySelectorAll('[data-refresh]').forEach(function (el) {
      el.addEventListener('click', function () {
        this.classList.add('spinning');
        toast(root, '状态已刷新 · 示例数据保持不变');
        setTimeout(function () { el.classList.remove('spinning'); }, 650);
      });
    });

    var prompt = root.querySelector('.t3-prompt');
    if (prompt) {
      prompt.addEventListener('submit', function (ev) {
        ev.preventDefault();
        var input = prompt.querySelector('input');
        toast(root, 'command executed: ' + (input.value || 'help'));
        input.value = '';
      });
      root.querySelectorAll('[data-command]').forEach(function (el) {
        el.addEventListener('click', function () {
          var input = root.querySelector('.t3-prompt input');
          if (input) { input.value = this.dataset.command; input.focus(); }
        });
      });
    }

    var commandSearch = root.querySelector('[data-command-search]');
    if (commandSearch) {
      commandSearch.addEventListener('input', function () {
        var q = this.value.trim().toLowerCase();
        root.querySelectorAll('.s10-results button').forEach(function (btn) {
          btn.hidden = !!q && btn.textContent.toLowerCase().indexOf(q) === -1;
        });
      });
    }

    root.querySelectorAll('.s7-node').forEach(function (btn) {
      btn.addEventListener('click', function () {
        root.querySelectorAll('.s7-node').forEach(function (x) { x.classList.remove('active'); });
        this.classList.add('active');
        var n = nodes[Number(this.dataset.node)];
        var name = root.querySelector('[data-node-name]');
        var note = root.querySelector('[data-node-note]');
        var meta = root.querySelector('[data-node-meta]');
        if (name) name.textContent = n[0];
        if (note) note.textContent = n[3] === 'bad' ? '该节点连续超时，建议先核对地址与证书。' : '节点连接稳定，最近一次测试通过。';
        if (meta) meta.innerHTML = '<div><dt>地址</dt><dd>' + n[1] + '</dd></div><div><dt>负载</dt><dd>' + n[4] + '%</dd></div><div><dt>种子</dt><dd>' + n[5] + '</dd></div>';
      });
    });

    root.querySelectorAll('[data-check]').forEach(function (el) {
      el.addEventListener('click', function () { this.classList.toggle('done'); });
    });

    root.querySelectorAll('input[type=range]').forEach(function (input) {
      input.addEventListener('input', function () {
        var out = input.parentNode.querySelector('.range-value');
        if (out) out.textContent = input.value + ' 分钟';
      });
    });

    var neuForm = root.querySelector('[data-neu-form]');
    if (neuForm) neuForm.addEventListener('submit', function (ev) { ev.preventDefault(); toast(root, '设置已保存'); });
  }

  function cardPreview(e) {
    return '<div class="card-preview pv-' + e.id + '"><span class="pv-num">' + e.id + '</span><i class="pv-bar"></i><i class="pv-bar short"></i><i class="pv-dot"></i><b>' + e.page + '</b></div>';
  }

  function initIndex() {
    var grid = document.querySelector('[data-example-grid]');
    if (!grid) return;
    grid.innerHTML = examples.map(function (e) {
      return '<a class="example-card reveal" href="' + e.id + '-' + e.slug + '.html" data-filter-value="' + e.family + '" data-search="' + (e.title + ' ' + e.note + ' ' + e.tags.join(' ')).toLowerCase() + '">' + cardPreview(e) + '<div class="card-meta"><small>' + e.id + ' / 20 · ' + e.page + '</small><h2>' + e.title + '</h2><p>' + e.note + '</p><div class="card-tags">' + e.tags.map(function (tag) { return '<span>' + tag + '</span>'; }).join('') + '</div></div></a>';
    }).join('');

    var search = document.querySelector('[data-example-search]');
    var filters = document.querySelectorAll('[data-filter]');
    var count = document.querySelector('[data-example-count]');
    var active = 'all';
    function update() {
      var q = search ? search.value.trim().toLowerCase() : '';
      var visible = 0;
      grid.querySelectorAll('.example-card').forEach(function (card) {
        card.hidden = !((active === 'all' || card.dataset.filterValue === active) && (!q || card.dataset.search.indexOf(q) !== -1));
        if (!card.hidden) visible += 1;
      });
      if (count) count.textContent = visible + ' directions';
    }
    filters.forEach(function (filter) {
      filter.addEventListener('click', function () {
        active = this.dataset.filter;
        filters.forEach(function (x) { x.classList.toggle('is-active', x === filter); });
        update();
      });
    });
    if (search) search.addEventListener('input', update);
    reveal(document);
  }

  function initPage() {
    var root = document.querySelector('[data-example]');
    if (!root) return;
    var e = examples.filter(function (x) { return x.id === root.dataset.example; })[0];
    if (!e) return;
    var keys = {
      'glass-air': 'glassAir',
      'swiss-ledger': 'swissLedger',
      'oled-terminal': 'oledTerminal',
      'paper-issue': 'paperIssue',
      'studio-warm': 'studioWarm',
      'bento-ops': 'bentoOps',
      'constellation': 'constellation',
      'brutal-signal': 'brutalSignal',
      'neu-touch': 'neuTouch',
      'command-deck': 'commandDeck',
      'archive-room': 'archiveRoom',
      'week-field': 'weekField',
      'heat-room': 'heatRoom',
      'field-notes': 'fieldNotes',
      'magazine-lux': 'magazineLux',
      'inbox-light': 'inboxLight',
      'split-ink': 'splitInk',
      'dense-grid': 'denseGrid',
      'blueprint': 'blueprint',
      'liquid-dark': 'liquidDark'
    };
    var key = keys[e.slug];
    root.className = 'demo host-' + key;
    root.innerHTML = templates[key](e);
    document.title = e.title + ' - qBT-Dashboard';
    bind(root);
  }

  document.addEventListener('DOMContentLoaded', function () { initIndex(); initPage(); });
})();
