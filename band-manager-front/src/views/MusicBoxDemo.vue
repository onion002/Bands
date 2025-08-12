<template>
  <div class="music-box-demo">
    <div class="demo-header">
      <h1>🎵 音乐盒演示</h1>
      <p>体验音乐搜索和播放功能</p>
    </div>

    <div class="demo-content">
      <div class="feature-section">
        <h2>✨ 功能特性</h2>
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <h3>智能搜索</h3>
            <p>支持歌曲名、歌手、专辑搜索</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🎵</div>
            <h3>高品质播放</h3>
            <p>支持多种音质选择</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">📱</div>
            <h3>响应式设计</h3>
            <p>适配各种设备屏幕</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🎨</div>
            <h3>美观界面</h3>
            <p>深色主题，霓虹配色</p>
          </div>
        </div>
      </div>

      <div class="usage-section">
        <h2>📖 使用说明</h2>
        <div class="usage-steps">
          <div class="step">
            <div class="step-number">1</div>
            <div class="step-content">
              <h3>打开音乐盒</h3>
              <p>点击页面左上角的旋转黑胶唱片图标</p>
            </div>
          </div>
          <div class="step">
            <div class="step-number">2</div>
            <div class="step-content">
              <h3>搜索音乐</h3>
              <p>在搜索框中输入歌曲名、歌手或专辑名</p>
            </div>
          </div>
          <div class="step">
            <div class="step-number">3</div>
            <div class="step-content">
              <h3>选择音质</h3>
              <p>选择合适的音质，从标准到超清母带</p>
            </div>
          </div>
          <div class="step">
            <div class="step-number">4</div>
            <div class="step-content">
              <h3>播放音乐</h3>
              <p>点击搜索结果中的歌曲开始播放</p>
            </div>
          </div>
        </div>
      </div>

      <div class="debug-section">
        <h3>🔧 调试信息</h3>
        <div class="debug-content">
          <p><strong>问题描述：</strong>音乐搜索成功，但播放失败</p>
          <p><strong>可能原因：</strong></p>
          <ul>
            <li>音频URL无效或已过期</li>
            <li>网络连接问题</li>
            <li>浏览器兼容性问题</li>
            <li>CORS跨域限制</li>
            <li>音频格式不支持</li>
          </ul>
          <p><strong>调试步骤：</strong></p>
          <ol>
            <li>打开浏览器开发者工具（F12）</li>
            <li>查看控制台（Console）的错误信息</li>
            <li>检查网络（Network）标签页的请求状态</li>
            <li>确认音频URL是否可访问</li>
          </ol>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 音乐盒演示页面
</script>

<style lang="scss" scoped>
.music-box-demo {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.demo-header {
  text-align: center;
  margin-bottom: 3rem;

  h1 {
    font-size: 2.5rem;
    color: #ff6b9d;
    margin-bottom: 1rem;
    font-weight: 700;
  }

  p {
    font-size: 1.2rem;
    color: #e0e0e0;
    opacity: 0.8;
  }
}

.demo-content {
  .feature-section {
    margin-bottom: 4rem;

    h2 {
      font-size: 2rem;
      color: #00d4ff;
      margin-bottom: 2rem;
      text-align: center;
    }

    .features-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 2rem;

      .feature-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;

        &:hover {
          transform: translateY(-5px);
          border-color: #ff6b9d;
          box-shadow: 0 10px 30px rgba(255, 107, 157, 0.2);
        }

        .feature-icon {
          font-size: 3rem;
          margin-bottom: 1rem;
        }

        h3 {
          font-size: 1.3rem;
          color: #fff;
          margin-bottom: 1rem;
        }

        p {
          color: #b0b0b0;
          line-height: 1.6;
        }
      }
    }
  }

  .usage-section {
    margin-bottom: 4rem;

    h2 {
      font-size: 2rem;
      color: #00d4ff;
      margin-bottom: 2rem;
      text-align: center;
    }

    .usage-steps {
      display: flex;
      flex-direction: column;
      gap: 2rem;

      .step {
        display: flex;
        align-items: center;
        gap: 2rem;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 2rem;

        .step-number {
          width: 60px;
          height: 60px;
          background: linear-gradient(135deg, #ff6b9d, #00d4ff);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.5rem;
          font-weight: 700;
          color: #fff;
          flex-shrink: 0;
        }

        .step-content {
          h3 {
            font-size: 1.3rem;
            color: #fff;
            margin-bottom: 0.5rem;
          }

          p {
            color: #b0b0b0;
            line-height: 1.6;
            margin: 0;
          }
        }
      }
    }
  }

  .debug-section {
    background: rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 1.5rem;

    h3 {
      margin: 0 0 1rem 0;
      color: #ff6b9d;
      font-size: 1.2rem;
    }

    .debug-content {
      color: #e0e0e0;
      line-height: 1.6;

      p {
        margin-bottom: 0.5rem;
      }

      ul, ol {
        margin: 0.5rem 0;
        padding-left: 1.5rem;
      }

      li {
        margin-bottom: 0.25rem;
      }

      strong {
        color: #ff6b9d;
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .music-box-demo {
    padding: 1rem;
  }

  .demo-header h1 {
    font-size: 2rem;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .step {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
}
</style>
