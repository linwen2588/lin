/**
 * 大家庭成员记录 - 详情页逻辑
 * 功能：加载成员相册，渲染时间轴（支持图片和视频）
 */

(function() {
  'use strict';

  // DOM元素
  const loadingContainer = document.getElementById('loadingContainer');
  const errorContainer = document.getElementById('errorContainer');
  const errorMessage = document.getElementById('errorMessage');
  const pageContent = document.getElementById('pageContent');
  const memberAvatar = document.getElementById('memberAvatar');
  const memberName = document.getElementById('memberName');
  const photoCount = document.getElementById('photoCount');
  const timeline = document.getElementById('timeline');
  const emptyState = document.getElementById('emptyState');

  // 数据缓存
  let galleryData = null;
  let currentMemberId = null;

  /**
   * 初始化应用
   */
  function init() {
    // 获取URL参数
    const urlParams = new URLSearchParams(window.location.search);
    currentMemberId = urlParams.get('id');
    
    if (!currentMemberId) {
      showError('缺少成员ID参数，请从首页进入。');
      return;
    }
    
    loadData();
  }

  /**
   * 加载JSON数据
   */
  async function loadData() {
    try {
      showLoading();
      
      const response = await fetch('data/gallery-data.json');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      galleryData = await response.json();
      
      if (!galleryData || !galleryData.members || !galleryData.galleries) {
        throw new Error('数据格式错误');
      }
      
      // 查找当前成员
      const member = galleryData.members.find(m => m.id === currentMemberId);
      
      if (!member) {
        throw new Error('找不到该成员');
      }
      
      // 获取该成员的相册
      const photos = galleryData.galleries[currentMemberId] || [];
      
      // 渲染页面
      renderHeader(member, photos.length);
      renderTimeline(photos);
      showContent();
      
    } catch (error) {
      console.error('加载数据失败:', error);
      showError(getErrorMessage(error));
    }
  }

  /**
   * 获取友好的错误信息
   */
  function getErrorMessage(error) {
    if (error.message.includes('404')) {
      return '找不到数据文件，请确保已运行 generate_data.py 生成数据。';
    }
    if (error.message.includes('Failed to fetch')) {
      return '网络连接失败，请检查网络后重试。';
    }
    if (error.message.includes('找不到该成员')) {
      return '找不到该成员，请返回首页重新选择。';
    }
    return '无法加载相册数据，请刷新页面重试。';
  }

  /**
   * 显示加载状态
   */
  function showLoading() {
    loadingContainer.style.display = 'flex';
    errorContainer.style.display = 'none';
    pageContent.style.display = 'none';
  }

  /**
   * 显示错误状态
   */
  function showError(message) {
    loadingContainer.style.display = 'none';
    errorContainer.style.display = 'flex';
    pageContent.style.display = 'none';
    errorMessage.textContent = message;
  }

  /**
   * 显示内容
   */
  function showContent() {
    loadingContainer.style.display = 'none';
    errorContainer.style.display = 'none';
    pageContent.style.display = 'block';
  }

  /**
   * 渲染头部信息
   */
  function renderHeader(member, count) {
    const avatarUrl = member.avatar || 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">👤</text></svg>';
    const displayName = formatMemberName(member.name);
    
    memberAvatar.src = avatarUrl;
    memberAvatar.onerror = function() {
      this.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">👤</text></svg>';
    };
    memberName.textContent = displayName;
    
    // 显示照片和视频数量
    let countText = `${count} 张照片`;
    if (member.videoCount > 0) {
      countText = `${member.photoCount} 张照片, ${member.videoCount} 个视频`;
    }
    photoCount.textContent = countText;
    
    // 更新页面标题
    document.title = `${displayName}的相册 - 大家庭成员记录`;
  }

  /**
   * 渲染时间轴
   */
  function renderTimeline(photos) {
    if (!photos || photos.length === 0) {
      timeline.style.display = 'none';
      emptyState.style.display = 'flex';
      return;
    }
    
    timeline.style.display = 'block';
    emptyState.style.display = 'none';
    
    // 按日期倒序排列（最新的在最上面）
    const sortedPhotos = [...photos].sort((a, b) => {
      return (b.sortDate || 0) - (a.sortDate || 0);
    });
    
    timeline.innerHTML = sortedPhotos.map((photo, index) => createTimelineItem(photo, index)).join('');
  }

  /**
   * 创建时间轴项目HTML
   */
  function createTimelineItem(photo, index) {
    const dateStr = formatDate(photo.date);
    const desc = photo.desc || '美好瞬间';
    const isVideo = photo.type === 'video';
    
    // 日期来源标记
    let dateSourceText = '';
    if (photo.dateSource === 'exif') {
      dateSourceText = '<span class="date-source">(EXIF)</span>';
    } else if (photo.dateSource === 'file') {
      dateSourceText = '<span class="date-source">(文件日期)</span>';
    }
    
    // 媒体内容（图片或视频）
    let mediaContent = '';
    if (isVideo) {
      mediaContent = `
        <div class="timeline-image-wrapper">
          <span class="video-badge">🎬 视频</span>
          <video 
            class="timeline-video" 
            src="${escapeHtml(photo.src)}" 
            controls
            preload="metadata"
            onerror="this.classList.add('error'); this.onerror=null;"
          >
            您的浏览器不支持视频播放
          </video>
        </div>
      `;
    } else {
      mediaContent = `
        <div class="timeline-image-wrapper">
          <img 
            class="timeline-image" 
            src="${escapeHtml(photo.src)}" 
            alt="${escapeHtml(desc)}"
            onerror="this.classList.add('error'); this.onerror=null;"
          >
        </div>
      `;
    }
    
    return `
      <article class="timeline-item">
        <div class="timeline-dot"></div>
        <div class="timeline-content">
          ${mediaContent}
          <div class="timeline-info">
            <div class="timeline-date">
              <span>📅</span>
              <time datetime="${escapeHtml(photo.date || '')}">${dateStr}</time>
              ${dateSourceText}
            </div>
            <p class="timeline-desc">${escapeHtml(desc)}</p>
          </div>
        </div>
      </article>
    `;
  }

  /**
   * 格式化日期
   * 将 YYYY-MM-DD 格式转换为 "2024年2月15日"
   */
  function formatDate(dateStr) {
    if (!dateStr) return '未知日期';
    
    // 尝试解析日期
    const date = new Date(dateStr);
    
    if (isNaN(date.getTime())) {
      // 如果不是标准日期格式，尝试手动解析 YYYY-MM-DD
      const match = dateStr.match(/^(\d{4})-(\d{1,2})-(\d{1,2})$/);
      if (match) {
        const year = match[1];
        const month = parseInt(match[2], 10);
        const day = parseInt(match[3], 10);
        return `${year}年${month}月${day}日`;
      }
      return dateStr;
    }
    
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const day = date.getDate();
    
    return `${year}年${month}月${day}日`;
  }

  /**
   * 格式化成员名称
   */
  function formatMemberName(name) {
    if (!name) return '未命名';
    
    const nameMap = {
      'mom': '妈妈',
      'dad': '爸爸',
      'grandma': '奶奶',
      'grandpa': '爷爷',
      'grandmother': '外婆',
      'grandfather': '外公',
      'son': '儿子',
      'daughter': '女儿',
      'child': '宝宝',
      'baby': '宝宝',
      'wife': '妻子',
      'husband': '丈夫',
      'sister': '姐姐/妹妹',
      'brother': '哥哥/弟弟'
    };
    
    const lowerName = name.toLowerCase();
    if (nameMap[lowerName]) {
      return nameMap[lowerName];
    }
    
    return name.charAt(0).toUpperCase() + name.slice(1);
  }

  /**
   * HTML转义，防止XSS
   */
  function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
  }

  // 启动应用
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
