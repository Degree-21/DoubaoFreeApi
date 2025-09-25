// Content script that runs on doubao.com pages
(function() {
  'use strict';

  console.log('Doubao API Monitor content script loaded');

  // Inject the monitoring script into the page
  const script = document.createElement('script');
  script.src = chrome.runtime.getURL('injected.js');
  script.onload = function() {
    this.remove();
  };
  (document.head || document.documentElement).appendChild(script);

  // Send log to popup
  function sendLog(message, type = 'info', detail = null) {
    chrome.runtime.sendMessage({
      type: 'MONITOR_LOG',
      message: message,
      logType: type,
      detail: detail
    }).catch(() => {
      // Popup might be closed, ignore error
    });
  }

  // Send initial log
  sendLog('监听脚本已注入到豆包页面', 'success');

  // Listen for messages from background script (network interception)
  chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
    if (message.type === 'NETWORK_REQUEST_INTERCEPTED') {
      console.log('📨 收到background script的网络拦截数据:', message.data);
      
      const data = message.data;
      const paramCount = Object.keys(data.searchParams || {}).length;
      const cookieLength = data.cookies ? data.cookies.length : 0;
      const logMessage = `🎯 网络拦截到聊天请求 - AID: ${data.aid} (${paramCount}个参数, Cookie长度: ${cookieLength})`;
      
      // Send detailed log with expandable data
      sendLog(logMessage, 'success', data);
      
      // Get user data from storage and send to reporting endpoint
      chrome.storage.sync.get(['phone', 'name'], function(userData) {
        if (userData.phone && userData.name) {
          const reportData = {
            user: {
              phone: userData.phone,
              name: userData.name
            },
            request: data
          };
          
          // Send to reporting endpoint
          reportToEndpoint(reportData);
        } else {
          sendLog('❌ 用户信息未保存，无法上报数据', 'error');
        }
      });
    }
  });

  // Keep the injected script as fallback - Listen for messages from the injected script
  window.addEventListener('message', function(event) {
    if (event.source !== window) return;
    
    if (event.data.type === 'DOUBAO_API_REQUEST') {
      console.log('API request intercepted:', event.data.payload);
      const payload = event.data.payload;
      
      // Create a detailed log message
      const paramCount = Object.keys(payload.searchParams || {}).length;
      const logMessage = `🎯 监听到聊天请求 - AID: ${payload.aid} (${paramCount}个参数)`;
      
      // Send detailed log with expandable data
      sendLog(logMessage, 'success', payload);
      
      // Get user data from storage and send to reporting endpoint
      chrome.storage.sync.get(['phone', 'name'], function(userData) {
        if (userData.phone && userData.name) {
          const reportData = {
            user: {
              phone: userData.phone,
              name: userData.name
            },
            request: payload
          };
          
          // Send to reporting endpoint
          reportToEndpoint(reportData);
        } else {
          sendLog('❌ 用户信息未保存，无法上报数据', 'error');
        }
      });
    }
    
    if (event.data.type === 'DOUBAO_API_RESPONSE') {
      console.log('API response intercepted:', event.data.payload);
      const payload = event.data.payload;
      sendLog(`📤 收到聊天响应 - 状态: ${payload.status}`, 'success', {
        ...payload,
        responseBody: payload.body
      });
    }
    
    if (event.data.type === 'DOUBAO_API_ERROR') {
      console.log('API error intercepted:', event.data.payload);
      sendLog(`❌ 请求失败: ${event.data.payload.error}`, 'error', event.data.payload);
    }
  });

  function reportToEndpoint(data) {
    const reportingUrl = 'http://localhost:8001/api/monitor/report';
    
    sendLog(`正在上报数据到: ${reportingUrl}`, 'info');
    
    fetch(reportingUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data)
    }).then(response => {
      if (response.ok) {
        sendLog(`数据上报成功 (状态: ${response.status})`, 'success');
        console.log('Data reported successfully:', response.status);
      } else {
        sendLog(`数据上报失败 (状态: ${response.status})`, 'error');
        console.error('Failed to report data:', response.status);
      }
    }).catch(error => {
      sendLog(`数据上报失败: ${error.message}`, 'error');
      console.error('Failed to report data:', error);
    });
  }
})();