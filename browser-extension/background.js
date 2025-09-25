// Background script for network monitoring
console.log('🚀 Background script starting...');

// Test if webRequest API is available
if (chrome.webRequest) {
  console.log('✅ webRequest API available');
} else {
  console.log('❌ webRequest API not available');
}

chrome.webRequest.onBeforeSendHeaders.addListener(
  function(details) {
    console.log('📡 拦截到请求:', details.url);
    
    // Only monitor Doubao chat requests
    if (details.url.includes('doubao.com') && 
        details.url.includes('/samantha/chat/completion')) {
      
      console.log('🎯 拦截到豆包聊天请求:', details.url);
      console.log('🔍 请求详情:', details);
      
      // Extract cookies from request headers
      let cookies = null;
      let allHeaders = {};
      
      if (details.requestHeaders) {
        console.log('📋 请求头数量:', details.requestHeaders.length);
        for (const header of details.requestHeaders) {
          allHeaders[header.name] = header.value;
          console.log(`  ${header.name}: ${header.value.substring(0, 100)}${header.value.length > 100 ? '...' : ''}`);
          if (header.name.toLowerCase() === 'cookie') {
            cookies = header.value;
            console.log('🍪 找到Cookie头部! 长度:', header.value.length);
            console.log('🍪 Cookie内容预览:', header.value.substring(0, 200) + (header.value.length > 200 ? '...' : ''));
          }
        }
      } else {
        console.log('❌ 没有请求头数据');
      }
      
      if (cookies) {
        console.log('🍪 最终Cookie长度:', cookies.length);
      } else {
        console.log('❌ 未找到Cookie头部');
        // 检查所有头部名称
        console.log('📋 所有请求头名称:', details.requestHeaders?.map(h => h.name).join(', ') || '无');
      }
      
      // Parse URL parameters
      const url = new URL(details.url);
      const searchParams = {};
      for (const [key, value] of url.searchParams.entries()) {
        searchParams[key] = value;
      }
      
      // Create request data
      const requestData = {
        url: details.url,
        method: details.method,
        cookies: cookies,
        searchParams: searchParams,
        headers: allHeaders,
        timestamp: new Date().toISOString(),
        aid: searchParams.aid || null
      };
      
      // Send to content script
      if (details.tabId && details.tabId >= 0) {
        console.log('📤 发送数据到content script, tabId:', details.tabId);
        chrome.tabs.sendMessage(details.tabId, {
          type: 'NETWORK_REQUEST_INTERCEPTED',
          data: requestData
        }).then(() => {
          console.log('✅ 消息发送成功');
        }).catch(err => {
          console.log('❌ 发送消息到content script失败:', err);
        });
      } else {
        console.log('❌ 无效的tabId:', details.tabId);
      }
    }
  },
  {urls: ["https://www.doubao.com/*"]},
  ["requestHeaders", "extraHeaders"]
);

console.log('🚀 Background script loaded - 网络监听已激活');