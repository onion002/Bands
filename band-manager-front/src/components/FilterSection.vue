<template>
  <!-- 筛选区域 -->
  <div class="filter-section">
    <div class="filter-group">
      <label>{{ selectLabel }}：</label>
      <select :value="selectValue" @change="handleSelectChange">
        <option value="">{{ selectPlaceholder }}</option>
        <option
          v-for="option in selectOptions"
          :key="option.value"
          :value="option.value"
        >
          {{ option.label }}
        </option>
      </select>
    </div>
    <div class="filter-group">
      <label>{{ searchLabel }}：</label>
      <input
        type="text"
        :value="searchValue"
        @input="handleSearchInput"
        :placeholder="searchPlaceholder"
      >
    </div>
  </div>
</template>

<script setup lang="ts">
interface FilterOption {
  value: string | number
  label: string
}

interface Props {
  // 下拉选择相关
  selectLabel: string
  selectValue: string | number
  selectPlaceholder: string
  selectOptions: FilterOption[]
  
  // 搜索输入相关
  searchLabel: string
  searchValue: string
  searchPlaceholder: string
}

interface Emits {
  (e: 'select-change', value: string | number): void
  (e: 'search-input', value: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const handleSelectChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  emit('select-change', target.value)
}

const handleSearchInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  emit('search-input', target.value)
}
</script>

<style scoped>
.filter-section {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
  padding: 20px 4px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  flex-wrap: wrap;
  border: 1px solid #333;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-group label {
  font-weight: 500;
  color: white;
  white-space: nowrap;
}

.filter-group select,
.filter-group input {
  padding: 8px 12px;
  border: 2px solid #555;
  border-radius: 4px;
  font-size: 14px;
  min-width: 200px;
  background: #333;
  color: white;
}

.filter-group select:focus,
.filter-group input:focus {
  outline: none;
  border-color: #e53935;
  box-shadow: 0 0 0 2px rgba(229, 57, 53, 0.25);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .filter-section {
    flex-direction: column;
    gap: 15px;
  }
  
  .filter-group {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .filter-group select,
  .filter-group input {
    width: 100%;
    min-width: unset;
  }
}
</style>
