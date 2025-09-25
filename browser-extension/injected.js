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
  const originalXHRSetRequestHeader = XMLHttpRequest.prototype.setRequestHeader;
  
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
    
    // Use document.cookie directly - this is the most reliable method
    const cookies = document.cookie;
    
    // 详细的cookie调试信息
    console.log('🍪 Cookie详细调试信息:');
    console.log('  document.cookie原始内容:', document.cookie);
    console.log('  document.cookie长度:', document.cookie?.length || 0);
    console.log('  document.cookie是否为空:', !document.cookie || document.cookie.trim() === '');
    
    if (document.cookie && document.cookie.length > 0) {
      // 解析并显示每个cookie
      const cookieArray = document.cookie.split(';').map(c => c.trim());
      console.log('  解析到的cookie数量:', cookieArray.length);
      cookieArray.forEach((cookie, index) => {
        const [name, value] = cookie.split('=');
        console.log(`  Cookie[${index}]: ${name} = ${value ? value.substring(0, 50) + '...' : 'empty'}`);
      });
    } else {
      console.log('  ❌ 警告: document.cookie为空或不存在');
    }
    
    return {
      url: url,
      method: method || 'GET',
      searchParams: searchParams,
      aid: searchParams.aid || null,
      cookies: cookies,
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
      
      console.log('🔍 Cookie来源检查 (Fetch):');
      console.log('  document.cookie长度:', document.cookie?.length || 0);
      console.log('  document.cookie内容:', document.cookie?.substring(0, 200) + '...' || 'none');
      console.log('  请求头Cookie:', config?.headers?.Cookie || config?.headers?.cookie || '无');
      console.log('  最终使用Cookie长度:', requestData.cookies?.length || 0);
      
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
      console.log('  Cookies:', requestData.cookies ? requestData.cookies.substring(0, 100) + '...' : 'none');
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
    this._headers = {}; // Store headers for monitoring
    
    // Log ALL XHR requests for debugging
    console.log('📡 XHR请求:', method, url);
    
    return originalXHROpen.apply(this, [method, url, ...rest]);
  };
  
  // Override setRequestHeader to capture headers
  XMLHttpRequest.prototype.setRequestHeader = function(name, value) {
    if (!this._headers) this._headers = {};
    this._headers[name] = value;
    return originalXHRSetRequestHeader.apply(this, [name, value]);
  };
  
  XMLHttpRequest.prototype.send = function(body) {
    if (shouldMonitorURL(this._url)) {
      console.log('🎯 监听到聊天请求 (XHR):', this._url);
      
      const requestData = extractRequestData(this._url, this._method, { 
        body: body,
        headers: this._headers || {}
      });
      
      console.log('🔍 Cookie来源检查:');
      console.log('  document.cookie长度:', document.cookie?.length || 0);
      console.log('  document.cookie内容:', document.cookie?.substring(0, 200) + '...' || 'none');
      console.log('  请求头Cookie:', this._headers?.Cookie || this._headers?.cookie || '无');
      console.log('  最终使用Cookie长度:', requestData.cookies?.length || 0);
      
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
      console.log('  Cookies:', requestData.cookies ? requestData.cookies.substring(0, 100) + '...' : 'none');
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
    console.log('🔧 Fetch函数是否被重写:', window.fetch !== originalFetch);
    console.log('🔧 XHR.open是否被重写:', XMLHttpRequest.prototype.open !== originalXHROpen);
    console.log('🔧 XHR.send是否被重写:', XMLHttpRequest.prototype.send !== originalXHRSend);
    
    // Test document.cookie directly
    console.log('🍪 测试Cookie访问:');
    console.log('  当前页面URL:', window.location.href);
    console.log('  当前域名:', window.location.hostname);
    console.log('  document.cookie长度:', document.cookie?.length || 0);
    console.log('  document.cookie内容前200字符:', document.cookie?.substring(0, 200) || 'empty');
    
    // 详细分析cookie内容
    if (document.cookie && document.cookie.length > 0) {
      console.log('✅ Cookie访问正常');
      const cookieArray = document.cookie.split(';').map(c => c.trim());
      console.log('  总共有', cookieArray.length, '个cookie:');
      cookieArray.slice(0, 5).forEach((cookie, index) => {
        const [name, value] = cookie.split('=');
        console.log(`  Cookie[${index}]: ${name} = ${value ? (value.length > 30 ? value.substring(0, 30) + '...' : value) : 'empty'}`);
      });
      if (cookieArray.length > 5) {
        console.log(`  ... 还有 ${cookieArray.length - 5} 个cookie`);
      }
    } else {
      console.log('❌ Cookie为空，可能是页面加载时机问题');
      console.log('  页面加载状态:', document.readyState);
      console.log('  页面协议:', window.location.protocol);
      console.log('  是否HTTPS:', window.location.protocol === 'https:');
      
      // 延迟再次检查
      setTimeout(() => {
        console.log('🔄 3秒后重新检查Cookie:');
        console.log('  document.cookie长度:', document.cookie?.length || 0);
        console.log('  document.cookie内容前200字符:', document.cookie?.substring(0, 200) || 'still empty');
        
        if (document.cookie && document.cookie.length > 0) {
          console.log('✅ 延迟检查成功，现在有cookie了');
          const cookieArray = document.cookie.split(';').map(c => c.trim());
          cookieArray.slice(0, 3).forEach((cookie, index) => {
            const [name, value] = cookie.split('=');
            console.log(`  延迟检查Cookie[${index}]: ${name} = ${value ? value.substring(0, 30) + '...' : 'empty'}`);
          });
        } else {
          console.log('❌ 延迟检查仍然没有cookie');
        }
      }, 3000);
      
      // 再次延迟检查
      setTimeout(() => {
        console.log('🔄 5秒后最终检查Cookie:');
        console.log('  document.cookie长度:', document.cookie?.length || 0);
        if (document.cookie && document.cookie.length > 0) {
          console.log('✅ 最终检查成功');
        } else {
          console.log('❌ 最终检查仍然失败，请检查页面是否正确加载或cookie设置');
        }
      }, 5000);
    }
  }, 1000);
  
  console.log('✅ 监听脚本部署完成，等待豆包聊天请求...');
})();