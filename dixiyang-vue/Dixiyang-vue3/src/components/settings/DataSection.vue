<template>
  <SettingsSection
    title="数据"
    description="所有创作内容存在服务器，这里只管理本机的界面数据。"
  >
    <SettingRow
      label="恢复默认外观"
      desc="清除背景图与字体设置，恢复初始界面。创作内容与账号信息不受影响。"
      stacked
    >
      <button class="btn btn-ghost" type="button" @click="resetAppearance">
        <RefreshLeft /> 恢复默认外观
      </button>
    </SettingRow>

    <div class="row-divider"></div>

    <SettingRow
      label="清理历史偏好"
      desc="移除旧版本遗留、已不再生效的本地设置项（创作偏好、AI 建议开关等）。"
      stacked
    >
      <button class="btn btn-ghost" type="button" :disabled="cleaning" @click="cleanLegacy">
        <Delete /> {{ cleaning ? '清理中…' : '清理历史偏好' }}
      </button>
    </SettingRow>

    <p v-if="cleanResult !== null" class="result-tip">
      {{ cleanResult > 0 ? `已清理 ${cleanResult} 项历史设置` : '没有发现需要清理的历史设置' }}
    </p>
  </SettingsSection>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Delete, RefreshLeft } from '@element-plus/icons-vue'
import SettingsSection from '@/components/SettingsSection.vue'
import SettingRow from '@/components/settings/SettingRow.vue'
import { useBackgroundConfig } from '@/composables/useBackgroundConfig'
import { useFontConfig } from '@/composables/useFontConfig'
import { confirmDelete } from '@/utils/confirm'

const cfg = useBackgroundConfig()
const fontConfig = useFontConfig()

/** 恢复默认外观：背景 + 字体一并重置（背景通过空串语义同步到服务器） */
const resetAppearance = async () => {
  const ok = await confirmDelete('恢复默认外观？将清除当前背景图与字体设置。')
  if (!ok) return
  cfg.resetToDefault()
  fontConfig.resetToDefault()
  ElMessage.success('已恢复默认外观')
}

// 旧版死设置的 localStorage 前缀（写入后从未被任何代码读取）
const LEGACY_PREFIXES = ['creation_', 'ai_sugg_']

const cleaning = ref(false)
const cleanResult = ref<number | null>(null)

const cleanLegacy = () => {
  cleaning.value = true
  cleanResult.value = null
  try {
    const keys: string[] = []
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i)
      if (key && LEGACY_PREFIXES.some((p) => key.startsWith(p))) keys.push(key)
    }
    keys.forEach((k) => localStorage.removeItem(k))
    cleanResult.value = keys.length
  } finally {
    cleaning.value = false
  }
}
</script>

<style scoped>
.row-divider {
  height: 1px;
  background: var(--border-color);
}

.result-tip {
  margin: 0;
  font-size: 0.8125rem;
  color: var(--text-muted);
}
</style>
