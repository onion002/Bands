<template>
  <div class="test-container">
    <h2>组件测试页面</h2>
    
    <h3>FilterSection 组件测试</h3>
    <FilterSection
      select-label="测试选择"
      :select-value="testSelectValue"
      select-placeholder="请选择"
      :select-options="testOptions"
      search-label="测试搜索"
      :search-value="testSearchValue"
      search-placeholder="请输入搜索内容"
      @select-change="handleSelectChange"
      @search-input="handleSearchInput"
    />
    
    <div class="test-output">
      <p>选择值: {{ testSelectValue }}</p>
      <p>搜索值: {{ testSearchValue }}</p>
    </div>
    
    <h3>EmptyState 组件测试</h3>
    <EmptyState
      icon-class="fas fa-music"
      message="这是一个测试空状态"
      button-text="测试按钮"
      button-icon="fas fa-plus"
      @button-click="handleButtonClick"
    />
    
    <div v-if="buttonClicked" class="test-output">
      <p>按钮已被点击！</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import FilterSection from './FilterSection.vue'
import EmptyState from './EmptyState.vue'

const testSelectValue = ref('')
const testSearchValue = ref('')
const buttonClicked = ref(false)

const testOptions = [
  { value: 'option1', label: '选项1' },
  { value: 'option2', label: '选项2' },
  { value: 'option3', label: '选项3' }
]

const handleSelectChange = (value: string | number) => {
  testSelectValue.value = value as string
}

const handleSearchInput = (value: string) => {
  testSearchValue.value = value
}

const handleButtonClick = () => {
  buttonClicked.value = true
  setTimeout(() => {
    buttonClicked.value = false
  }, 2000)
}
</script>

<style scoped>
.test-container {
  padding: 20px;
  background: #1a1a1a;
  color: white;
  min-height: 100vh;
}

.test-output {
  margin: 20px 0;
  padding: 15px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

h2, h3 {
  color: #e53935;
  margin-bottom: 20px;
}
</style>
