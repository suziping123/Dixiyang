<template>
  <SettingsSection
    title="外观"
    description="背景图跟随账号同步，换设备也能保持；字体设置保存在当前浏览器。"
  >
    <div class="block">
      <h3 class="block-title">背景图</h3>
      <BackgroundControl mode="full" />
    </div>

    <div class="row-divider"></div>

    <div class="block">
      <h3 class="block-title">字体</h3>
      <FontControl />
    </div>
  </SettingsSection>
</template>

<script setup lang="ts">
import SettingsSection from '@/components/SettingsSection.vue'
import BackgroundControl from '@/components/BackgroundControl.vue'
import FontControl from '@/components/FontControl.vue'
</script>

<style scoped>
.block {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.block-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin: 0;
}

.row-divider {
  height: 1px;
  background: var(--border-color);
}
</style>
