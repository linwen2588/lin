/**
 * 大家庭成员记录 - 首页逻辑
 * 功能：加载成员数据，渲染成员网格
 */

(function() {
  'use strict';

  // DOM元素
  const loadingContainer = document.getElementById('loadingContainer');
  const errorContainer = document.getElementById('errorContainer');
  const errorMessage = document.getElementById('errorMessage');
  const membersContainer = document.getElementById('membersContainer');
  const membersGrid = document.getElementById('membersGrid');

  // 数据缓存
  let galleryData = null;

  /**
   * 初始化应用
   */
  function init() {
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
      
      if (!galleryData || !galleryData.members) {
        throw new Error('数据格式错误');
      }
      
      renderMembers(galleryData.members);
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
    return '无法加载家庭数据，请刷新页面重试。';
  }

  /**
   * 显示加载状态
   */
  function showLoading() {
    loadingContainer.style.display = 'flex';
    errorContainer.style.display = 'none';
    membersContainer.style.display = 'none';
  }

  /**
   * 显示错误状态
   */
  function showError(message) {
    loadingContainer.style.display = 'none';
    errorContainer.style.display = 'flex';
    membersContainer.style.display = 'none';
    errorMessage.textContent = message;
  }

  /**
   * 显示内容
   */
  function showContent() {
    loadingContainer.style.display = 'none';
    errorContainer.style.display = 'none';
    membersContainer.style.display = 'block';
  }

  /**
   * 渲染成员网格
   */
  function renderMembers(members) {
    if (!members || members.length === 0) {
      membersGrid.innerHTML = `
        <div class="empty-state" style="grid-column: 1 / -1;">
          <div class="empty-icon">👨‍👩‍👧‍👦</div>
          <h2 class="empty-title">还没有成员</h2>
          <p class="empty-desc">在 images/ 文件夹下创建成员文件夹并添加头像即可开始</p>
        </div>
      `;
      return;
    }

    membersGrid.innerHTML = members.map(member => createMemberCard(member)).join('');
    
    // 添加点击事件
    document.querySelectorAll('.member-card').forEach(card => {
      card.addEventListener('click', function() {
        const memberId = this.dataset.memberId;
        navigateToMember(memberId);
      });
    });
  }

  /**
   * 创建成员卡片HTML
   */
  function createMemberCard(member) {
    const avatarUrl = member.avatar || 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">👤</text></svg>';
    const photoCount = member.photoCount || 0;
    const videoCount = member.videoCount || 0;
    const displayName = formatMemberName(member.name);
    
    // 构建数量显示文本
    let countText = `${photoCount} 张照片`;
    if (videoCount > 0) {
      countText += ` · ${videoCount} 个视频`;
    }
    
    return `
      <article class="member-card" data-member-id="${escapeHtml(member.id)}" role="button" tabindex="0">
        <img 
          class="member-avatar" 
          src="${escapeHtml(avatarUrl)}" 
          alt="${escapeHtml(displayName)}的头像"
          onerror="this.src='data:image/svg+xml,<svg xmlns=\\'http://www.w3.org/2000/svg\\' viewBox=\\'0 0 100 100\\'><text y=\\'.9em\\' font-size=\\'90\\'>👤</text></svg>'"
        >
        <h3 class="member-name">${escapeHtml(displayName)}</h3>
        <span class="member-count">
          <span>📷</span>
          <span>${countText}</span>
        </span>
      </article>
    `;
  }

  /**
   * 格式化成员名称
   * 将文件夹名转换为更友好的显示名称
   */
  function formatMemberName(name) {
    if (!name) return '未命名';
    
    // 常见名称映射
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
    
    // 首字母大写
    return name.charAt(0).toUpperCase() + name.slice(1);
  }

  /**
   * 跳转到成员详情页
   */
  function navigateToMember(memberId) {
    window.location.href = `member.html?id=${encodeURIComponent(memberId)}`;
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
