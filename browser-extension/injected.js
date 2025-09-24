// Injected script that runs in the page context to intercept fetch requests
(function() {
  'use strict';
  
  console.log('🚀 Doubao API监听脚本已启动');
  console.log('🔧 当前页面URL:', window.location.href);
  console.log('🔧 当前域名:', window.location.hostname);
  
  // Store original fetch and XMLHttpRequest
  const originalFetch = window.fetch;
  const originalXHROpen = XMLHttpRequest.prototype.open;
  const originalXHRSend = XMLHttpRequest.prototype.send;
  
  // Helper function to check if URL should be monitored
  function shouldMonitorURL(url) {
    const shouldMonitor = url.includes('doubao.com') && url.includes('/samantha/chat/completion');
    console.log('🔍 检查URL:', url, '-> 监听:', shouldMonitor);
    return shouldMonitor;
  }
  
  // Helper function to extract request data
  function extractRequestData(url, method, config = {}) {
    const urlObj = new URL(url);
    const searchParams = {};
    
    // Get all URL parameters
    for (const [key, value] of urlObj.searchParams.entries()) {
      searchParams[key] = value;
    }
    
    // Get request body
    let requestBody = null;
    if (config.body) {
      requestBody = typeof config.body === 'string' ? config.body : JSON.stringify(config.body);
    }
    
    return {
      url: url,
      method: method || 'GET',
      searchParams: searchParams,
      aid: searchParams.aid || null,
      cookies: document.cookie,
      headers: config.headers || {},
      requestBody: requestBody,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent
    };
  }
  
  // Helper function to send data to content script
  function sendToContentScript(type, data) {
    console.log('📨 发送消息到content script:', type, data);
    window.postMessage({
      type: type,
      payload: data
    }, '*');
  }
  
  // Override fetch to intercept requests
  window.fetch = function(...args) {
    const [resource, config] = args;
    const url = typeof resource === 'string' ? resource : resource.url;
    
    // Log ALL fetch requests for debugging
    console.log('📡 Fetch请求:', url);
    
    if (shouldMonitorURL(url)) {
      console.log('🎯 监听到聊天请求:', url);
      
      const requestData = extractRequestData(url, config?.method, config);
      
      // Print all GET parameters clearly
      console.log('📝 请求详情:');
      console.log('  URL:', requestData.url);
      console.log('  Method:', requestData.method);
      console.log('  🔍 所有GET参数:');
      if (Object.keys(requestData.searchParams).length > 0) {
        Object.entries(requestData.searchParams).forEach(([key, value]) => {
          console.log(`    ${key}: ${value}`);
        });
      } else {
        console.log('    无GET参数');
      }
      console.log('  Headers:', requestData.headers);
      console.log('  Cookies长度:', requestData.cookies.length);
      console.log('  完整数据:', requestData);
      
      // Send request data to content script
      sendToContentScript('DOUBAO_API_REQUEST', requestData);
      
      // Intercept response
      const fetchPromise = originalFetch.apply(this, args);
      fetchPromise.then(response => {
        if (response.ok) {
          const clonedResponse = response.clone();
          clonedResponse.text().then(responseText => {
            console.log('📤 响应数据:', response.status);
            sendToContentScript('DOUBAO_API_RESPONSE', {
              status: response.status,
              headers: Object.fromEntries(response.headers.entries()),
              body: responseText.substring(0, 1000),
              timestamp: new Date().toISOString()
            });
          }).catch(err => {
            console.error('读取响应失败:', err);
          });
        }
      }).catch(err => {
        console.error('请求失败:', err);
        sendToContentScript('DOUBAO_API_ERROR', {
          error: err.message,
          timestamp: new Date().toISOString()
        });
      });
      
      return fetchPromise;
    }
    
    // Call original fetch for other requests
    return originalFetch.apply(this, args);
  };
  
  // Override XMLHttpRequest
  XMLHttpRequest.prototype.open = function(method, url, ...rest) {
    this._method = method;
    this._url = url;
    
    // Log ALL XHR requests for debugging
    console.log('📡 XHR请求:', method, url);
    
    return originalXHROpen.apply(this, [method, url, ...rest]);
  };
  
  XMLHttpRequest.prototype.send = function(body) {
    if (shouldMonitorURL(this._url)) {
      console.log('🎯 监听到聊天请求 (XHR):', this._url);
      
      const requestData = extractRequestData(this._url, this._method, { body: body });
      
      // Print all GET parameters clearly
      console.log('📝 请求详情 (XHR):');
      console.log('  URL:', requestData.url);
      console.log('  Method:', requestData.method);
      console.log('  🔍 所有GET参数:');
      if (Object.keys(requestData.searchParams).length > 0) {
        Object.entries(requestData.searchParams).forEach(([key, value]) => {
          console.log(`    ${key}: ${value}`);
        });
      } else {
        console.log('    无GET参数');
      }
      console.log('  Request Body:', requestData.requestBody ? requestData.requestBody.substring(0, 200) + '...' : 'none');
      console.log('  Cookies长度:', requestData.cookies.length);
      console.log('  完整数据:', requestData);
      
      // Send request data to content script
      sendToContentScript('DOUBAO_API_REQUEST', requestData);
      
      // Set up response handler
      const originalOnReadyStateChange = this.onreadystatechange;
      this.onreadystatechange = function() {
        if (this.readyState === 4) {
          console.log('📤 响应数据 (XHR):', this.status);
          sendToContentScript('DOUBAO_API_RESPONSE', {
            status: this.status,
            body: this.responseText.substring(0, 1000),
            timestamp: new Date().toISOString()
          });
        }
        
        if (originalOnReadyStateChange) {
          originalOnReadyStateChange.apply(this, arguments);
        }
      };
    }
    
    return originalXHRSend.apply(this, [body]);
  };
  
  // Test if script injection works
  setTimeout(() => {
    console.log('✅ 监听脚本部署完成，开始测试...');
    console.log('🧪 测试fetch是否被拦截...');
    // Don't actually make the request, just test the interception
    console.log('🔧 Fetch函数是否被重写:', window.fetch !== originalFetch);
    console.log('🔧 XHR.open是否被重写:', XMLHttpRequest.prototype.open !== originalXHROpen);
    console.log('🔧 XHR.send是否被重写:', XMLHttpRequest.prototype.send !== originalXHRSend);
  }, 1000);
  
  console.log('✅ 监听脚本部署完成，等待豆包聊天请求...');
})();