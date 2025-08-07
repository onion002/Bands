<template>
  <div class="home-view">
    <!-- 🎵 未认证用户的英雄区域 -->
    <section v-if="!authStore.isAuthenticated" class="hero-section">
      <div class="hero-background">
        <div class="gradient-overlay"></div>
        <div class="pattern-overlay bg-noise"></div>
      </div>

      <div class="hero-content">
        <div class="hero-text">
          <h1 class="hero-title">
            <span class="title-line">
              <span class="text-gradient">独立音乐人</span>
            </span>
            <span class="title-line">管理平台</span>
          </h1>
          <p class="hero-subtitle">
            探索独特音乐世界，感受原创音乐魅力，连接艺术家与粉丝的桥梁
          </p>

          <!-- 🎨 操作按钮 -->
          <div class="hero-actions">
            <router-link to="/auth/login" class="btn btn-primary btn-lg">
              <i class="fa fa-sign-in"></i>
              开始体验
            </router-link>
            <router-link to="/public" class="btn btn-secondary btn-lg">
              <i class="fa fa-eye"></i>
              浏览作品
            </router-link>
          </div>
        </div>

        <!-- 🎵 音乐播放器预览 -->
        <div class="music-preview">
          <div class="preview-card card card-interactive">
            <div class="preview-image">
              <div class="album-cover">
                <i class="fa fa-music"></i>
              </div>
            </div>
            <div class="preview-content">
              <h3 class="track-title">欢迎来到音乐世界</h3>
              <p class="artist-name">SOUNDWAVE 平台</p>
              <div class="player-controls">
                <button class="play-btn">
                  <i class="fa fa-play-circle"></i>
                </button>
                <div class="progress-bar">
                  <div class="progress" style="width: 35%"></div>
                </div>
                <span class="time">1:23 / 3:45</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 🌟 特性展示 -->
      <div class="features-section">
        <div class="features-grid">
          <div class="feature-card card">
            <div class="feature-icon">
              <i class="fa fa-users"></i>
            </div>
            <h3>乐队管理</h3>
            <p>轻松管理乐队信息、成员资料和演出安排</p>
          </div>
          <div class="feature-card card">
            <div class="feature-icon">
              <i class="fa fa-calendar"></i>
            </div>
            <h3>活动安排</h3>
            <p>统一管理演出活动，追踪票务和场地信息</p>
          </div>
          <div class="feature-card card">
            <div class="feature-icon">
              <i class="fa fa-chart-line"></i>
            </div>
            <h3>数据分析</h3>
            <p>深入了解粉丝喜好，优化音乐创作方向</p>
          </div>
        </div>
      </div>

      <!-- 🎯 向下滚动指示器 -->
      <div class="scroll-indicator animate-float">
        <a href="#features" class="scroll-link">
          <i class="fa fa-angle-down"></i>
        </a>
      </div>
    </section>

    <!-- 🔄 已认证用户跳转加载 -->
    <div v-else-if="authStore.isAuthenticated && !redirecting" class="loading-section">
      <div class="loading-content">
        <div class="loading-spinner animate-pulse-slow">
          <i class="fa fa-spinner fa-spin"></i>
        </div>
        <h3>正在跳转...</h3>
        <p>为您准备专属体验</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useStaggerAnimation, useMusicAnimation } from '@/composables/useAnimations'

const router = useRouter()
const authStore = useAuthStore()
const redirecting = ref(false)

// 🎨 动画控制
const { elementsRef: heroElementsRef, staggerIn } = useStaggerAnimation()
const { barsRef, startVisualization } = useMusicAnimation()

onMounted(async () => {
  console.log('HomeView mounted')
  console.log('Initial auth state:', {
    isAuthenticated: authStore.isAuthenticated,
    token: authStore.token,
    user: authStore.user
  })

  // 🎨 启动进入动画
  if (!authStore.isAuthenticated) {
    setTimeout(() => staggerIn(150), 100)
    setTimeout(() => startVisualization(), 500)
  }

  // 初始化认证状态
  authStore.initAuth()

  console.log('After initAuth:', {
    isAuthenticated: authStore.isAuthenticated,
    token: authStore.token,
    user: authStore.user
  })

  // 如果有token但没有用户信息，验证token
  if (authStore.token && !authStore.user) {
    console.log('Verifying token...')
    const isValid = await authStore.verifyToken()
    console.log('Token verification result:', isValid)
  }

  // 如果用户已登录，根据用户类型跳转
  if (authStore.isAuthenticated) {
    console.log('User is authenticated, redirecting...')
    redirecting.value = true
    setTimeout(() => {
      if (authStore.isAdmin) {
        console.log('Redirecting to dashboard')
        router.push('/dashboard')
      } else {
        console.log('Redirecting to public')
        router.push('/public')
      }
    }, 1000)
  } else {
    console.log('User is not authenticated, showing landing page')
  }
})
</script>

<style scoped lang="scss">
@use '@/assets/scss/variables' as *;
@use '@/assets/scss/mixins' as *;

.home-view {
  min-height: 100vh;
  width: 100%;
}

// 🎵 英雄区域样式
.hero-section {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  padding: 2rem;

  .hero-background {
    position: absolute;
    inset: 0;
    z-index: 0;

    .gradient-overlay {
      position: absolute;
      inset: 0;
      background: linear-gradient(135deg, rgba($primary, 0.2), rgba($secondary, 0.2));
      mix-blend-mode: overlay;
    }

    .pattern-overlay {
      position: absolute;
      inset: 0;
      opacity: 0.3;
    }
  }

  .hero-content {
    position: relative;
    z-index: 10;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 4rem;
    max-width: 1200px;
    width: 100%;
    align-items: center;

    @media (max-width: 768px) {
      grid-template-columns: 1fr;
      gap: 2rem;
      text-align: center;
    }
  }

  .hero-text {
    .hero-title {
      font-family: $font-family-display;
      font-size: clamp(2.5rem, 8vw, 4rem);
      font-weight: 700;
      line-height: 1.1;
      margin: 0 0 1.5rem;
      letter-spacing: -0.02em;
      @include fade-in-up(0.8s, 40px, 0.2s);

      .title-line {
        display: block;
        @include fade-in-left(0.6s, 30px);

        &:first-child {
          animation-delay: 0.4s;
        }

        &:last-child {
          color: $white;
          animation-delay: 0.6s;
        }
      }
    }

    .hero-subtitle {
      font-size: clamp(1rem, 3vw, 1.25rem);
      color: $gray-300;
      line-height: 1.6;
      margin: 0 0 2.5rem;
      max-width: 500px;
      @include fade-in-up(0.6s, 30px, 0.8s);
    }

    .hero-actions {
      display: flex;
      gap: 1rem;
      flex-wrap: wrap;
      @include fade-in-up(0.5s, 20px, 1s);

      .btn {
        @include animated-button;

        &:nth-child(1) {
          animation-delay: 1.2s;
        }

        &:nth-child(2) {
          animation-delay: 1.4s;
        }
      }

      @media (max-width: 480px) {
        flex-direction: column;
      }
    }
  }
}

// 🎵 音乐预览卡片
.music-preview {
  .preview-card {
    max-width: 400px;
    padding: 2rem;

    .preview-image {
      text-align: center;
      margin-bottom: 1.5rem;

      .album-cover {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: $gradient-primary;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        font-size: 3rem;
        color: $white;
        box-shadow: $shadow-primary;
      }
    }

    .preview-content {
      text-align: center;

      .track-title {
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0 0 0.5rem;
        color: $white;
      }

      .artist-name {
        color: $primary;
        font-weight: 500;
        margin: 0 0 1.5rem;
      }

      .player-controls {
        display: flex;
        align-items: center;
        gap: 1rem;

        .play-btn {
          background: none;
          border: none;
          color: $primary;
          font-size: 2rem;
          cursor: pointer;
          transition: all $transition-normal ease;

          &:hover {
            color: $white;
            transform: scale(1.1);
          }
        }

        .progress-bar {
          flex: 1;
          height: 4px;
          background: rgba($lightgray, 0.3);
          border-radius: 2px;
          overflow: hidden;

          .progress {
            height: 100%;
            background: $gradient-primary;
            border-radius: 2px;
            transition: width $transition-normal ease;
          }
        }

        .time {
          font-size: 0.875rem;
          color: $gray-400;
          min-width: 80px;
        }
      }
    }
  }
}
// 🌟 特性展示区域
.features-section {
  margin-top: 4rem;
  width: 100%;
  max-width: 1200px;

  .features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;

    .feature-card {
      text-align: center;
      padding: 2rem;

      .feature-icon {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background: rgba($primary, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1.5rem;
        font-size: 2rem;
        color: $primary;
        transition: all $transition-normal ease;
      }

      h3 {
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0 0 1rem;
        color: $white;
      }

      p {
        color: $gray-400;
        line-height: 1.6;
        margin: 0;
      }

      &:hover .feature-icon {
        background: rgba($primary, 0.2);
        transform: scale(1.1);
      }
    }
  }
}

// 🎯 滚动指示器
.scroll-indicator {
  position: absolute;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);

  .scroll-link {
    color: rgba($white, 0.7);
    font-size: 2rem;
    text-decoration: none;
    transition: color $transition-normal ease;

    &:hover {
      color: $primary;
    }
  }
}

// 🔄 加载区域
.loading-section {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: $gradient-dark;

  .loading-content {
    text-align: center;

    .loading-spinner {
      font-size: 4rem;
      color: $primary;
      margin-bottom: 2rem;
    }

    h3 {
      font-size: 1.5rem;
      font-weight: 600;
      margin: 0 0 0.5rem;
      color: $white;
    }

    p {
      color: $gray-400;
      margin: 0;
    }
  }
}

// 🎨 响应式动画优化



@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
</style>