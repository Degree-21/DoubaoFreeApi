// Popup script for handling user input and navigation
document.addEventListener('DOMContentLoaded', function() {
  const phoneInput = document.getElementById('phone');
  const nameInput = document.getElementById('name');
  const saveButton = document.getElementById('save');
  const openDoubaoButton = document.getElementById('open-doubao');
  const clearButton = document.getElementById('clear-data');
  const copyLogsButton = document.getElementById('copy-logs');
  const clearLogsButton = document.getElementById('clear-logs');
  const statusDiv = document.getElementById('status');
  const logContainer = document.getElementById('log-container');
  const pinNotification = document.getElementById('pin-notification');
  const hidePinBtn = document.getElementById('hide-pin-btn');

  // Check if extension should show pin notification
  checkPinStatus();

  // Add event listener for hide pin button
  hidePinBtn.addEventListener('click', function() {
    hidePinNotification();
  });

  // Load saved data
  chrome.storage.sync.get(['phone', 'name'], function(result) {
    if (result.phone) {
      phoneInput.value = result.phone;
    }
    if (result.name) {
      nameInput.value = result.name;
    }
    
    // If both phone and name are saved, disable save button and show status
    if (result.phone && result.name) {
      saveButton.disabled = true;
      saveButton.textContent = '已保存';
      showStatus('用户信息已保存，可以开始监听', 'success');
    }
  });

  // Load monitoring logs
  loadLogs();

  // Save user data
  saveButton.addEventListener('click', function() {
    const phone = phoneInput.value.trim();
    const name = nameInput.value.trim();

    if (!phone || !name) {
      showStatus('请填写完整的手机号和名称', 'error');
      return;
    }

    // Simple phone validation
    const phoneRegex = /^1[3-9]\d{9}$/;
    if (!phoneRegex.test(phone)) {
      showStatus('请输入正确的手机号格式', 'error');
      return;
    }

    // Disable button and show loading state
    saveButton.disabled = true;
    saveButton.textContent = '保存中...';

    chrome.storage.sync.set({
      phone: phone,
      name: name,
      timestamp: Date.now()
    }, function() {
      if (chrome.runtime.lastError) {
        showStatus('保存失败: ' + chrome.runtime.lastError.message, 'error');
        saveButton.disabled = false;
        saveButton.textContent = '保存信息';
      } else {
        showStatus('保存成功，正在跳转...', 'success');
        saveButton.textContent = '已保存';
        addLog('用户信息保存成功', 'success');
        
        // Auto jump to Doubao chat page after 1 second
        setTimeout(function() {
          chrome.tabs.create({ url: 'https://www.doubao.com/chat/' });
          window.close();
        }, 1000);
      }
    });
  });

  // Clear user data
  clearButton.addEventListener('click', function() {
    if (confirm('确定要清除所有数据吗？')) {
      chrome.storage.sync.clear(function() {
        phoneInput.value = '';
        nameInput.value = '';
        saveButton.disabled = false;
        saveButton.textContent = '保存信息';
        showStatus('数据已清除', 'success');
        addLog('用户数据已清除', 'success');
      });
    }
  });

  // Open Doubao chat page
  openDoubaoButton.addEventListener('click', function() {
    chrome.tabs.create({ url: 'https://www.doubao.com/chat/' });
    window.close();
  });

  // Copy all logs to clipboard
  copyLogsButton.addEventListener('click', function() {
    console.log('Copy button clicked');
    console.log('Log container children:', logContainer.children.length);
    
    const logs = collectAllLogs();
    console.log('Collected logs:', logs);
    
    if (logs.length === 0) {
      showStatus('没有日志可以复制', 'error');
      return;
    }

    const logText = formatLogsForCopy(logs);
    console.log('Formatted log text length:', logText.length);
    
    // Copy to clipboard
    navigator.clipboard.writeText(logText).then(function() {
      showStatus(`已复制 ${logs.length} 条日志到剪贴板`, 'success');
    }).catch(function(err) {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = logText;
      document.body.appendChild(textArea);
      textArea.select();
      try {
        document.execCommand('copy');
        showStatus(`已复制 ${logs.length} 条日志到剪贴板`, 'success');
      } catch (fallbackErr) {
        showStatus('复制失败，请手动复制', 'error');
        console.error('Copy failed:', fallbackErr);
      }
      document.body.removeChild(textArea);
    });
  });

  // Clear all logs
  clearLogsButton.addEventListener('click', function() {
    const logs = collectAllLogs();
    if (logs.length === 0) {
      showStatus('没有日志可以清除', 'error');
      return;
    }

    if (confirm(`确定要清除所有 ${logs.length} 条日志吗？此操作不可撤销。`)) {
      // Clear log container
      logContainer.innerHTML = '<div class="log-item">等待监听数据...</div>';
      
      // Clear stored logs
      chrome.storage.local.remove(['monitorLogs'], function() {
        showStatus('日志已清除', 'success');
        console.log('All logs cleared');
      });
    }
  });

  function showStatus(message, type) {
    statusDiv.textContent = message;
    statusDiv.className = 'status ' + type;
    
    // Clear status after 3 seconds
    setTimeout(function() {
      statusDiv.textContent = '';
      statusDiv.className = '';
    }, 3000);
  }

  function addLog(message, type = 'info', detail = null) {
    const timestamp = new Date().toLocaleTimeString();
    const logItem = document.createElement('div');
    logItem.className = 'log-item' + (type !== 'info' ? ' ' + type : '');
    
    // Add expandable class if there's detail data
    if (detail) {
      logItem.className += ' expandable';
    }
    
    logItem.textContent = `[${timestamp}] ${message}`;
    
    // Add expand icon if there's detail
    if (detail) {
      const expandIcon = document.createElement('span');
      expandIcon.className = 'expand-icon';
      expandIcon.textContent = '▼';
      logItem.appendChild(expandIcon);
      
      // Create detail section
      const logDetail = document.createElement('div');
      logDetail.className = 'log-detail';
      
      if (typeof detail === 'object') {
        // Format object data nicely
        logDetail.innerHTML = formatDetailData(detail);
      } else {
        logDetail.textContent = detail;
      }
      
      logItem.appendChild(logDetail);
      
      // Add click handler to toggle detail
      logItem.addEventListener('click', function() {
        const isExpanded = logDetail.classList.contains('show');
        logDetail.classList.toggle('show');
        expandIcon.textContent = isExpanded ? '▼' : '▲';
      });
    }
    
    // Add to top of log container
    if (logContainer.children.length > 0 && logContainer.children[0].textContent === '等待监听数据...') {
      logContainer.innerHTML = '';
    }
    
    logContainer.insertBefore(logItem, logContainer.firstChild);
    
    // Keep only last 20 logs
    while (logContainer.children.length > 20) {
      logContainer.removeChild(logContainer.lastChild);
    }
    
    // Save logs to storage
    saveLogs();
  }

  function formatDetailData(data) {
    let html = '';
    
    if (data.url) {
      html += `<h5>🔗 请求URL:</h5>${data.url}\n\n`;
    }
    
    if (data.method) {
      html += `<h5>📝 请求方法:</h5>${data.method}\n\n`;
    }
    
    if (data.aid) {
      html += `<h5>🎯 AID参数:</h5>${data.aid}\n\n`;
    }
    
    // Display all GET parameters
    if (data.searchParams && Object.keys(data.searchParams).length > 0) {
      html += `<h5>🔍 所有GET参数 (共${Object.keys(data.searchParams).length}个):</h5>`;
      for (const [key, value] of Object.entries(data.searchParams)) {
        html += `  ${key}: ${value}\n`;
      }
      html += '\n';
    }
    
    if (data.headers && Object.keys(data.headers).length > 0) {
      html += `<h5>📋 请求头:</h5>${JSON.stringify(data.headers, null, 2)}\n\n`;
    }
    
    if (data.requestBody) {
      html += `<h5>📦 请求体:</h5>`;
      try {
        const parsed = JSON.parse(data.requestBody);
        html += JSON.stringify(parsed, null, 2);
      } catch (e) {
        html += data.requestBody;
      }
      html += '\n\n';
    }
    
    if (data.cookies) {
      html += `<h5>🍪 Cookies:</h5>${data.cookies}\n\n`;
    }
    
    if (data.responseBody) {
      html += `<h5>📤 响应内容:</h5>`;
      try {
        const parsed = JSON.parse(data.responseBody);
        html += JSON.stringify(parsed, null, 2);
      } catch (e) {
        html += data.responseBody;
      }
      html += '\n\n';
    }
    
    if (data.timestamp) {
      html += `<h5>⏰ 时间戳:</h5>${data.timestamp}`;
    }
    
    return html;
  }

  function loadLogs() {
    chrome.storage.local.get(['monitorLogs'], function(result) {
      if (result.monitorLogs && result.monitorLogs.length > 0) {
        logContainer.innerHTML = '';
        result.monitorLogs.forEach(function(log) {
          const logItem = document.createElement('div');
          logItem.className = 'log-item' + (log.type !== 'info' ? ' ' + log.type : '');
          
          if (log.detail) {
            logItem.className += ' expandable';
          }
          
          logItem.textContent = log.message;
          
          if (log.detail) {
            const expandIcon = document.createElement('span');
            expandIcon.className = 'expand-icon';
            expandIcon.textContent = '▼';
            logItem.appendChild(expandIcon);
            
            const logDetail = document.createElement('div');
            logDetail.className = 'log-detail';
            
            if (typeof log.detail === 'object') {
              logDetail.innerHTML = formatDetailData(log.detail);
            } else {
              logDetail.textContent = log.detail;
            }
            
            logItem.appendChild(logDetail);
            
            logItem.addEventListener('click', function() {
              const isExpanded = logDetail.classList.contains('show');
              logDetail.classList.toggle('show');
              expandIcon.textContent = isExpanded ? '▼' : '▲';
            });
          }
          
          logContainer.appendChild(logItem);
        });
      }
    });
  }

  function saveLogs() {
    const logs = Array.from(logContainer.children).map(function(item) {
      const log = {
        message: item.childNodes[0].textContent,
        type: item.className.includes('success') ? 'success' : 
              item.className.includes('error') ? 'error' : 'info'
      };
      
      // Check if this log has detail data
      const detailElem = item.querySelector('.log-detail');
      if (detailElem) {
        // Try to extract detail from the formatted HTML
        // This is a simplified version - ideally we'd store the original detail object
        log.detail = detailElem.textContent;
      }
      
      return log;
    });
    
    chrome.storage.local.set({ monitorLogs: logs });
  }

  function collectAllLogs() {
    const logs = [];
    const logItems = logContainer.children;
    
    for (let i = 0; i < logItems.length; i++) {
      const item = logItems[i];
      if (item.textContent.includes('等待监听数据...')) continue;
      
      // Get the main message text (first text node, excluding expand icons)
      let messageText = '';
      const textNodes = [];
      
      // Walk through child nodes to get only the main text
      for (let j = 0; j < item.childNodes.length; j++) {
        const node = item.childNodes[j];
        if (node.nodeType === Node.TEXT_NODE) {
          textNodes.push(node.textContent.trim());
        }
      }
      
      // Join text nodes and clean up
      messageText = textNodes.join(' ').replace(/[▼▲]\s*$/, '').trim();
      
      // If still empty, fallback to first text node content
      if (!messageText && item.childNodes.length > 0) {
        messageText = item.childNodes[0].textContent.replace(/[▼▲]\s*$/, '').trim();
      }
      
      if (!messageText) continue; // Skip empty logs
      
      const logData = {
        message: messageText,
        type: item.className.includes('success') ? 'success' : 
              item.className.includes('error') ? 'error' : 'info'
      };
      
      // Get detail data if exists
      const detailElem = item.querySelector('.log-detail');
      if (detailElem) {
        logData.detail = detailElem.textContent;
      }
      
      logs.push(logData);
    }
    
    console.log('collectAllLogs found:', logs.length, 'logs');
    return logs;
  }

  function formatLogsForCopy(logs) {
    let text = '=== 豆包API监听日志 ===\n';
    text += `导出时间: ${new Date().toLocaleString()}\n`;
    text += `日志条数: ${logs.length}\n\n`;
    
    logs.forEach(function(log, index) {
      // Clean message text from any remaining UI artifacts
      let cleanMessage = log.message
        .replace(/[▼▲]\s*/g, '') // Remove expand icons
        .replace(/详细信息:[\s\S]*/g, '') // Remove detail section from main message
        .trim();
      
      text += `[${index + 1}] ${cleanMessage}\n`;
      
      if (log.detail) {
        text += '\n详细信息:\n';
        // Clean detail text
        let cleanDetail = log.detail
          .replace(/^详细信息:\s*/g, '') // Remove duplicate "详细信息:" header
          .trim();
        text += cleanDetail.split('\n').map(line => '  ' + line).join('\n');
        text += '\n';
      }
      
      text += '\n' + '-'.repeat(50) + '\n\n';
    });
    
    return text;
  }

  // Listen for messages from content script about monitoring events
  chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
    if (message.type === 'MONITOR_LOG') {
      addLog(message.message, message.logType || 'info', message.detail || null);
    }
  });

  // Check if should show pin notification
  function checkPinStatus() {
    chrome.storage.local.get(['pinNotificationHidden'], function(result) {
      // Show notification if not hidden and this is likely the first few uses
      if (!result.pinNotificationHidden) {
        pinNotification.style.display = 'block';
      }
    });
  }

  // Hide pin notification and remember the choice
  function hidePinNotification() {
    pinNotification.style.display = 'none';
    chrome.storage.local.set({ pinNotificationHidden: true });
  }
});