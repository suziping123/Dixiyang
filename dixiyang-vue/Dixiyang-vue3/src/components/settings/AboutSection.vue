<template>
  <SettingsSection title="关于" description="关于本作品与它的运行方式。">
    <div class="about-hero">
      <h3 class="app-name">Dixiyang</h3>
      <p class="app-desc">
        面向长篇小说创作的管理工具：以宇宙为单位组织小说，用时间线与故事节点推进情节，
        角色库与 RAG 助手贯穿写作全程。
      </p>
    </div>

    <div class="row-divider"></div>

    <SettingRow label="数据存放" desc="创作内容保存在服务器，账号内跨设备同步；外观与字体设置保存在本机浏览器。" />
    <SettingRow label="界面版本" desc="当前为暗色玻璃主题（唯一主题），后续主题扩展会在此处提供切换。" />

    <div class="row-divider"></div>

    <div class="about-actions">
      <button class="btn btn-ghost" type="button" @click="router.push('/')">
        <Connection /> 查看介绍页
      </button>
      <button class="btn btn-ghost" type="button" @click="router.push('/home')">
        <HomeFilled /> 返回创作首页
      </button>
    </div>
  </SettingsSection>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Connection, HomeFilled } from '@element-plus/icons-vue'
import SettingsSection from '@/components/SettingsSection.vue'
import SettingRow from '@/components/settings/SettingRow.vue'

const router = useRouter()
</script>

<style scoped>
.about-hero {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.app-name {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
  letter-spacing: 0.02em;
}

.app-desc {
  margin: 0;
  font-size: 0.9375rem;
  line-height: 1.7;
  color: var(--text-secondary);
  max-width: 60ch;
}

.row-divider {
  height: 1px;
  background: var(--border-color);
}

.about-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
}

@media (max-width: 768px) {
  .about-actions {
    flex-direction: column;
    align-items: center;
  }

  .about-actions .btn {
    width: 100%;
    max-width: 320px;
  }
}
</style>
