
    var threatsData = [];

    function escapeHtml(str) {
      if (!str) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    }

    function formatMarkdown(text) {
      if (!text) return '';
      var escaped = escapeHtml(text);
      var parts = escaped.split('```');
      var out = '';
      for (var i = 0; i < parts.length; i++) {
        if (i % 2 === 1) {
          out += '<pre class="bg-dark text-light p-2 rounded"><code>' + parts[i] + '</code></pre>';
        } else {
          var p = parts[i];
          p = p.replace(/`([^`]+)`/g, '<code class="bg-light px-1 text-danger">$1</code>');
          p = p.replace(/^### (.*$)/gm, '<h5 class="fw-bold text-primary mt-2">$1</h5>');
          p = p.replace(/^#### (.*$)/gm, '<h6 class="fw-bold text-dark mt-2">$1</h6>');
          p = p.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
          p = p.replace(/\*([^*]+)\*/g, '<em>$1</em>');
          p = p.replace(/^&gt; (.*$)/gm, '<blockquote class="border-start border-3 border-secondary ps-2 my-1 text-muted">$1</blockquote>');
          p = p.replace(/^- (.*$)/gm, '<li>$1</li>');
          p = p.replace(/\n/g, '<br/>');
          out += p;
        }
      }
      return out;
    }

    function loadData() {
      fetch('/api/threats')
        .then(function(r) { return r.json(); })
        .then(function(data) {
          threatsData = data;
          renderThreats(data);
        })
        .catch(function(err) { console.error('Threat load error:', err); });

      fetch('/api/status')
        .then(function(r) { return r.json(); })
        .then(function(sData) {
          var badge = document.getElementById('ollamaBadge');
          if (sData.ollama_online) {
            if (sData.models && sData.models.length > 0) {
              badge.className = 'badge bg-success';
              badge.innerHTML = '<i class="bi bi-check-circle me-1"></i>Ollama Active: ' + escapeHtml(sData.models[0]);
            } else {
              badge.className = 'badge bg-warning text-dark';
              badge.innerHTML = '<i class="bi bi-exclamation-triangle me-1"></i>Ollama Online (No models pulled)';
            }
          } else {
            badge.className = 'badge bg-secondary';
            badge.innerHTML = '<i class="bi bi-cpu me-1"></i>Ollama Standby / RAG Active';
          }
          document.getElementById('engineStatus').innerHTML =
            '<div><strong>Ollama Connected:</strong> ' + (sData.ollama_online ? 'Yes (Port 11434)' : 'Offline / Standby') + '</div>' +
            '<div><strong>Available Models:</strong> ' + (sData.models && sData.models.length > 0 ? escapeHtml(sData.models.join(', ')) : 'None pulled yet') + '</div>' +
            '<div><strong>Vector Dimensions:</strong> 384-dim normalized</div>' +
            '<div><strong>Knowledge Chunks:</strong> ' + (sData.knowledge_chunks || 17) + '</div>';
        })
        .catch(function(err) { console.error('Status error:', err); });
    }

    function renderThreats(list) {
      var tbody = document.getElementById('threatsTbody');
      tbody.innerHTML = '';
      document.getElementById('recordCount').innerText = list.length + ' Threats Loaded';

      for (var i = 0; i < list.length; i++) {
        var t = list[i];
        var badgeSev = 'badge-low';
        if (t.severity === 'Critical') badgeSev = 'badge-critical';
        else if (t.severity === 'High') badgeSev = 'badge-high';
        else if (t.severity === 'Medium') badgeSev = 'badge-medium';

        var badgeStatus = 'badge-active';
        if (t.status === 'Resolved') badgeStatus = 'badge-resolved';
        else if (t.status === 'Anticipated') badgeStatus = 'badge-anticipated';
        else if (t.status === 'Evolving') badgeStatus = 'badge-evolving';

        var tr = document.createElement('tr');
        tr.innerHTML =
          '<td><strong>' + escapeHtml(t.platform) + '</strong></td>' +
          '<td><div class="fw-bold">' + escapeHtml(t.name) + '</div><code class="small text-muted">' + escapeHtml(t.cve_id) + '</code></td>' +
          '<td><span class="badge ' + badgeStatus + '">' + escapeHtml(t.status) + '</span></td>' +
          '<td><span class="badge ' + badgeSev + '">' + escapeHtml(t.severity) + '</span></td>' +
          '<td><span class="small text-muted">' + escapeHtml(t.attack_vector || 'N/A') + '</span></td>' +
          '<td><button type="button" class="btn btn-sm btn-outline-primary" onclick="showModal(' + i + ')"><i class="bi bi-shield-check me-1"></i>Mitigate</button></td>';
        tbody.appendChild(tr);
      }
    }

    function filterThreats() {
      var plat = document.getElementById('selPlatform').value;
      var stat = document.getElementById('selStatus').value;
      var sev = document.getElementById('selSeverity').value;

      var filtered = threatsData.filter(function(t) {
        if (plat !== 'All' && t.platform !== plat) return false;
        if (stat !== 'All' && t.status !== stat) return false;
        if (sev !== 'All' && t.severity !== sev) return false;
        return true;
      });
      renderThreats(filtered);
    }

    function showModal(idx) {
      var t = threatsData[idx];
      document.getElementById('mTitle').innerText = '[' + t.platform + '] ' + t.name + ' (' + t.cve_id + ')';
      document.getElementById('mBody').innerHTML =
        '<div class="mb-3">' +
          '<span class="badge bg-secondary me-2">Platform: ' + escapeHtml(t.platform) + '</span>' +
          '<span class="badge bg-info me-2">Lifecycle: ' + escapeHtml(t.status) + '</span>' +
          '<span class="badge bg-danger">Severity: ' + escapeHtml(t.severity) + ' (CVSS ' + (t.cvss_score || 'N/A') + ')</span>' +
        '</div>' +
        '<p><strong>Description:</strong> ' + escapeHtml(t.description) + '</p>' +
        '<div class="card p-3 mb-3 bg-light">' +
          '<strong>Step-by-Step Remediation Procedure:</strong>' +
          '<pre class="mt-2 mb-0" style="white-space: pre-wrap; font-family: inherit;">' + escapeHtml(t.mitigation_steps) + '</pre>' +
        '</div>' +
        (t.mitigation_script ?
          '<div class="card p-3 bg-dark text-light">' +
            '<strong>Automated Mitigation Command:</strong>' +
            '<code class="text-warning mt-1">' + escapeHtml(t.mitigation_script) + '</code>' +
          '</div>' : '');
      try {
        new bootstrap.Modal(document.getElementById('threatModal')).show();
      } catch(e) {
        var el = document.getElementById('threatModal');
        el.className = 'modal fade show';
        el.style.display = 'block';
      }
    }

    function fillPrompt(txt) {
      var input = document.getElementById('chatInput');
      input.value = txt;
      sendChat();
    }

    function sendChat() {
      var input = document.getElementById('chatInput');
      var sendBtn = document.getElementById('sendBtn');
      var text = input.value.trim();
      if (!text) {
        input.focus();
        return;
      }

      sendBtn.disabled = true;
      sendBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Sending...';

      var chatBox = document.getElementById('chatBox');
      chatBox.innerHTML += '<div class="chat-msg chat-user"><strong>You:</strong> ' + escapeHtml(text) + '</div>';
      chatBox.scrollTop = chatBox.scrollHeight;
      input.value = '';

      var loadId = 'load_' + Date.now();
      chatBox.innerHTML += '<div id="' + loadId + '" class="chat-msg chat-bot text-muted"><div class="spinner-border spinner-border-sm me-2"></div>Analyzing threat intelligence & retrieving vectors...</div>';
      chatBox.scrollTop = chatBox.scrollHeight;

      fetch('/api/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: text})
      })
      .then(function(res) { return res.json(); })
      .then(function(data) {
        var loadElem = document.getElementById(loadId);
        if (loadElem) loadElem.remove();

        var rendered = formatMarkdown(data.response || 'No response returned.');
        chatBox.innerHTML += '<div class="chat-msg chat-bot">' + rendered + '</div>';
        chatBox.scrollTop = chatBox.scrollHeight;

        if (data.sources && data.sources.length > 0) {
          var sc = document.getElementById('sourcesContainer');
          sc.innerHTML = '';
          for (var i = 0; i < data.sources.length; i++) {
            var s = data.sources[i];
            sc.innerHTML +=
              '<div class="card p-2 mb-2 bg-light border-start border-3 border-primary">' +
                '<div class="fw-bold">' + escapeHtml(s.source) + ' <span class="badge bg-primary float-end">Score: ' + s.score + '</span></div>' +
                '<div class="text-truncate mt-1 text-muted">' + escapeHtml(s.text) + '</div>' +
              '</div>';
          }
        }
      })
      .catch(function(err) {
        var loadElem = document.getElementById(loadId);
        if (loadElem) loadElem.remove();
        chatBox.innerHTML += '<div class="chat-msg chat-bot text-danger"><strong>Error connecting to assistant:</strong> ' + escapeHtml(err.toString()) + '</div>';
        chatBox.scrollTop = chatBox.scrollHeight;
      })
      .finally(function() {
        sendBtn.disabled = false;
        sendBtn.innerHTML = '<i class="bi bi-send-fill me-1"></i>Send';
        input.focus();
      });
    }

    function clearChat() {
      document.getElementById('chatBox').innerHTML = '<div class="chat-msg chat-bot">Chat history cleared. Ready for your inquiries.</div>';
      document.getElementById('sourcesContainer').innerHTML = '<span class="text-muted">Ask a question to see retrieved MongoDB vector documents.</span>';
    }

    function triggerScan() {
      var area = document.getElementById('scanReportArea');
      area.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary"></div><div class="mt-2 text-muted">Auditing system and dependencies...</div></div>';
      fetch('/api/scan', {method: 'POST'})
        .then(function(res) { return res.json(); })
        .then(function(data) {
          var html =
            '<div class="row g-2 mb-3">' +
              '<div class="col-3"><div class="card p-2 text-center bg-light"><strong>Total Findings:</strong> ' + data.total_vulnerabilities + '</div></div>' +
              '<div class="col-3"><div class="card p-2 text-center bg-danger text-light"><strong>Critical/High:</strong> ' + (data.critical_count + data.high_count) + '</div></div>' +
              '<div class="col-3"><div class="card p-2 text-center bg-warning"><strong>Medium:</strong> ' + data.medium_count + '</div></div>' +
              '<div class="col-3"><div class="card p-2 text-center bg-info text-light"><strong>Low:</strong> ' + data.low_count + '</div></div>' +
            '</div>' +
            '<h6>Discovered Vulnerabilities & Remediation:</h6>';

          for (var i = 0; i < data.findings.length; i++) {
            var f = data.findings[i];
            html +=
              '<div class="card p-3 mb-2 border-start border-4 border-warning">' +
                '<div class="d-flex justify-content-between align-items-center">' +
                  '<div>' +
                    '<strong>[' + escapeHtml(f.severity) + '] ' + escapeHtml(f.title) + '</strong>' +
                    '<div class="small text-muted">CVE: <code>' + escapeHtml(f.cve_id) + '</code> | Platform: ' + escapeHtml(f.platform) + '</div>' +
                  '</div>' +
                  '<button type="button" class="btn btn-sm btn-success" onclick="mitigateVuln(\'' + escapeHtml(f.cve_id) + '\')"><i class="bi bi-lightning-charge me-1"></i>Confirm & Mitigate</button>' +
                '</div>' +
                '<p class="mt-2 mb-1 small">' + escapeHtml(f.details) + '</p>' +
                '<code class="p-1 bg-light text-dark small">' + escapeHtml(f.fix_command) + '</code>' +
              '</div>';
          }
          area.innerHTML = html;
        })
        .catch(function(err) {
          area.innerHTML = '<div class="alert alert-danger">Scan failed: ' + escapeHtml(err.toString()) + '</div>';
        });
    }

    function mitigateVuln(cve) {
      if(!confirm('Apply mitigation for ' + cve + '? This will update the threat status to Resolved in MongoDB.')) return;
      fetch('/api/mitigate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({cve_id: cve})
      })
      .then(function(r) { return r.json(); })
      .then(function(data) {
        alert(data.message);
        triggerScan();
        loadData();
      });
    }

    function runExScript() {
      var term = document.getElementById('exTerminal');
      term.style.display = 'block';
      term.innerText = 'Executing Exercises 1 - 18 verification script...\n';
      fetch('/api/run_exercises')
        .then(function(r) { return r.text(); })
        .then(function(text) {
          term.innerText = text;
        });
    }

    window.addEventListener('load', function() {
      var input = document.getElementById('chatInput');
      if (input) {
        input.addEventListener('keydown', function(e) {
          if (e.key === 'Enter') {
            e.preventDefault();
            sendChat();
          }
        });
      }
      loadData();
    });
  