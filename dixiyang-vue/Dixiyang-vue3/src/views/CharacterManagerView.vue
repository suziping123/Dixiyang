<!--
 * @Author: suziping123 yunzhiming123@gmail.com
 * @Date: 2026-03-23 13:42:16
 * @LastEditors: suziping123 yunzhiming123@gmail.com
 * @LastEditTime: 2026-03-23 16:20:54
 * @FilePath: \Dixiyang\dixiyang-vue\Dixiyang-vue3\src\views\CharacterManagerView.vue
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
-->
<template>
  <div class="character-manager-container">
    <div class="bg-gradient-animation" :class="{ paused: !bgConfig.animEnabled.value }" :style="{ '--bg-intensity': (bgConfig.intensity.value as any) / 100 }"></div>

    <nav class="floating-nav">
      <div
        v-for="(item, idx) in navItems"
        :key="idx"
        class="nav-item"
        :class="{ active: activeNav === 2 }"
        @click="handleNavClick(idx)"
        :title="item.tooltip"
      >
        {{ item.iconClass }}
      </div>
    </nav>

    <main class="main-stage">
      <header class="stage-header">
        <div class="header-top">
          <div class="logo-wrapper">
            <h1 class="logo-text">DIXIYANG <span class="engine-span">ENGINE</span></h1>
            <div class="glow-line"></div>
          </div>
          <div class="header-controls">
            <BackgroundControl mode="compact" />
          </div>
        </div>
        <p class="subtitle">角色管理 - 小说：<span class="user-name">{{ novelTitle || '未知小说' }}</span></p>
      </header>

      <div class="character-section">
        <div class="section-header">
          <h2 class="section-title">✧ 角色管理</h2>
          <button class="create-character-btn" @click="openCreateDialog">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
            创建新角色
          </button>
        </div>

        <div v-if="isLoading" class="loading-state">
          <div class="spinner"></div>
          <p>正在加载角色列表...</p>
        </div>

        <div v-else-if="characters.length > 0" class="character-grid">
          <div v-for="character in characters" :key="character.id" class="character-card-wrapper">
            <div class="glass-card character-card" @mouseenter="hoveredCard = character.id" @mouseleave="hoveredCard = null">
              <div class="card-glow" :style="{ opacity: hoveredCard === character.id ? 1 : 0 }"></div>

              <div class="character-avatar">
                <span class="avatar-text">{{ character.name.charAt(0) }}</span>
              </div>

              <div class="card-content">
                <h3 class="character-name">{{ character.name }}</h3>
                <div class="character-info">
                  <span v-if="character.gender" class="info-tag">{{ character.gender }}</span>
                  <span v-if="character.age" class="info-tag">{{ character.age }}岁</span>
                </div>
                <p v-if="character.appearance" class="character-desc">{{ character.appearance }}</p>
                <p v-else-if="character.background" class="character-desc">{{ character.background }}</p>

                <div class="card-actions">
                  <button class="action-btn edit-btn" @click="openEditDialog(character)">
                    <svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/></svg>
                    编辑
                  </button>
                  <button class="action-btn delete-btn" @click="confirmDelete(character)">
                    <svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
                    删除
                  </button>
                </div>
              </div>
              <div class="card-border-gradient"></div>
            </div>
          </div>

          <div class="character-card-wrapper create-card-wrapper">
            <div class="glass-card create-card" @click="openCreateDialog">
              <div class="card-create-content">
                <svg class="create-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
                <span>创建新角色</span>
                <p class="create-hint">添加新的故事角色</p>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="empty-state">
          <svg viewBox="0 0 100 100" class="empty-icon"><circle cx="50" cy="50" r="40" fill="none" stroke="currentColor" stroke-width="2" opacity="0.3"/><path d="M50 30 L60 50 L50 70 L40 50 Z" fill="currentColor" opacity="0.3"/></svg>
          <p>暂无角色，点击上方按钮创建第一个角色</p>
        </div>
      </div>

      <div class="back-section">
        <button class="back-btn" @click="goBack">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/></svg>
          返回小说
        </button>
      </div>
    </main>

    <!-- 创建/编辑角色弹窗 -->
    <el-dialog
      v-model="showDialog"
      :title="isEditMode ? '编辑角色' : '创建新角色'"
      width="650px"
      class="character-dialog"
      @close="resetForm"
    >
      <el-form :model="form" label-position="top" class="character-form">
        <el-form-item label="角色名称" required>
          <el-input v-model="form.name" placeholder="请输入角色名称" />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="性别">
              <el-select v-model="form.gender" placeholder="请选择性别" clearable style="width: 100%;">
                <el-option label="男" value="男" />
                <el-option label="女" value="女" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="年龄">
              <el-input-number v-model="form.age" :min="0" :max="9999" placeholder="年龄" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="外貌描述">
          <el-input v-model="form.appearance" type="textarea" :rows="3" placeholder="描述角色的外貌特征" />
        </el-form-item>

        <el-form-item label="背景故事">
          <el-input v-model="form.background" type="textarea" :rows="3" placeholder="角色的背景故事" />
        </el-form-item>

        <el-form-item label="性格特点">
          <el-input v-model="form.personality" type="textarea" :rows="3" placeholder="描述角色的性格特点" />
        </el-form-item>

        <el-form-item label="额外信息 (键值对)">
          <div class="extra-fields">
            <div v-for="(item, index) in extraFields" :key="index" class="extra-field-row">
              <el-input v-model="item.key" placeholder="键名" class="extra-key" />
              <el-input v-model="item.value" placeholder="值" class="extra-value" />
              <el-button type="danger" :icon="Delete" circle @click="removeExtraField(index)" />
            </div>
            <el-button type="primary" link @click="addExtraField">
              <svg viewBox="0 0 24 24" fill="currentColor" style="width: 16px; height: 16px; margin-right: 4px;"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
              添加字段
            </el-button>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showDialog = false">取消</el-button>
          <el-button type="primary" @click="saveCharacter" :loading="isSaving">
            {{ isEditMode ? '保存修改' : '创建角色' }}
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 删除确认弹窗 -->
    <el-dialog v-model="showDeleteDialog" title="确认删除" width="400px" class="character-dialog">
      <p>确定要删除角色「{{ deleteCandidate?.name }}」吗？此操作不可恢复。</p>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showDeleteDialog = false">取消</el-button>
          <el-button type="danger" @click="handleDeleteCharacter" :loading="isDeleting">确认删除</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'
import BackgroundControl from '@/components/BackgroundControl.vue'
import { useBackgroundConfig } from '@/composables/useBackgroundConfig'
import { useTextColorCustomizer } from '@/composables/useTextColorCustomizer'
import type { CharacterVO, CharacterDTO } from '@/api/characterApi'
import { getCharacterList, createCharacter, updateCharacter, deleteCharacter as deleteCharacterApi } from '@/api/characterApi'

const router = useRouter()
const route = useRoute()
const bgConfig = useBackgroundConfig()
const textColorCustomizer = useTextColorCustomizer()

const activeNav = ref(2)
const novelTitle = ref('')
const isLoading = ref(true)
const isSaving = ref(false)
const isDeleting = ref(false)
const characters = ref<CharacterVO[]>([])
const showDialog = ref(false)
const showDeleteDialog = ref(false)
const isEditMode = ref(false)
const deleteCandidate = ref<CharacterVO | null>(null)
const editingId = ref<number | null>(null)
const hoveredCard = ref<number | null>(null)

const navItems = ref([
  { iconClass: '🏠', tooltip: '首页' },
  { iconClass: '🧭', tooltip: '发现' },
  { iconClass: '💾', tooltip: '库' },
  { iconClass: '🔔', tooltip: '通知' },
  { iconClass: '⚙️', tooltip: '设置' },
])

const form = reactive<Omit<CharacterDTO, 'extra'> & { extra?: string }>({
  novelId: 0,
  name: '',
  gender: '',
  age: undefined,
  appearance: '',
  background: '',
  personality: ''
})

interface ExtraField {
  key: string
  value: string
}

const extraFields = ref<ExtraField[]>([])

const novelId = computed(() => {
  return Number(route.params.novelId) || 0
})

const handleNavClick = (idx: number) => {
  activeNav.value = idx
  const routes = ['/home', '/discover', '/library', '/notifications', '/settings']
  const routePath = routes[idx]
  if (routePath && routePath !== '/home') {
    router.push(routePath).catch(() => console.log(`功能开发中...`))
  }
}

const goBack = () => {
  router.back()
}

const addExtraField = () => {
  extraFields.value.push({ key: '', value: '' })
}

const removeExtraField = (index: number) => {
  extraFields.value.splice(index, 1)
}

const extraFieldsToJson = (): Record<string, string> | undefined => {
  const result: Record<string, string> = {}
  for (const field of extraFields.value) {
    if (field.key.trim()) {
      result[field.key.trim()] = field.value
    }
  }
  return Object.keys(result).length > 0 ? result : undefined
}

const jsonToExtraFields = (extra: Record<string, unknown> | string | undefined) => {
  extraFields.value = []
  if (!extra) return

  let extraObj: Record<string, unknown> | null = null

  if (typeof extra === 'string') {
    try {
      extraObj = JSON.parse(extra)
    } catch {
      return
    }
  } else {
    extraObj = extra
  }

  if (extraObj && typeof extraObj === 'object') {
    for (const [key, value] of Object.entries(extraObj)) {
      extraFields.value.push({ key, value: String(value) })
    }
  }
}

const fetchCharacters = async () => {
  if (!novelId.value) return

  try {
    isLoading.value = true
    const res = await getCharacterList(novelId.value, 1, 100)
    characters.value = res.data.records || res.data || []
  } catch (error) {
    console.error('获取角色列表失败:', error)
    ElMessage.error('加载角色列表失败')
  } finally {
    isLoading.value = false
  }
}

const resetForm = () => {
  form.novelId = novelId.value
  form.name = ''
  form.gender = ''
  form.age = undefined
  form.appearance = ''
  form.background = ''
  form.personality = ''
  extraFields.value = []
  isEditMode.value = false
  editingId.value = null
}

const openCreateDialog = () => {
  resetForm()
  bgConfig.setAnimEnabled(false)
  showDialog.value = true
}

const openEditDialog = (character: CharacterVO) => {
  isEditMode.value = true
  editingId.value = character.id
  form.novelId = character.novelId
  form.name = character.name
  form.gender = character.gender || ''
  form.age = character.age
  form.appearance = character.appearance || ''
  form.background = character.background || ''
  form.personality = character.personality || ''
  jsonToExtraFields(character.extra as string | Record<string, unknown> | undefined)
  bgConfig.setAnimEnabled(false)
  showDialog.value = true
}

const saveCharacter = async () => {
  if (!form.name.trim()) {
    ElMessage.warning('请输入角色名称')
    return
  }

  try {
    isSaving.value = true

    const extraJson = extraFieldsToJson()
    const characterData: CharacterDTO = {
      ...form,
      extra: extraJson ? JSON.stringify(extraJson) : undefined
    }

    if (isEditMode.value && editingId.value) {
      await updateCharacter(editingId.value, characterData)
      ElMessage.success('角色更新成功')
    } else {
      await createCharacter(characterData)
      ElMessage.success('角色创建成功')
    }

    showDialog.value = false
    bgConfig.setAnimEnabled(true)
    await fetchCharacters()
  } catch (error) {
    console.error('保存角色失败:', error)
    ElMessage.error(isEditMode.value ? '更新失败' : '创建失败')
  } finally {
    isSaving.value = false
  }
}

const confirmDelete = (character: CharacterVO) => {
  deleteCandidate.value = character
  showDeleteDialog.value = true
}

const handleDeleteCharacter = async () => {
  if (!deleteCandidate.value) return

  try {
    isDeleting.value = true
    await deleteCharacterApi(deleteCandidate.value.id)
    ElMessage.success('删除成功')
    showDeleteDialog.value = false
    await fetchCharacters()
  } catch (error) {
    console.error('删除角色失败:', error)
    ElMessage.error('删除失败')
  } finally {
    isDeleting.value = false
    deleteCandidate.value = null
  }
}

onMounted(() => {
  if (novelId.value) {
    form.novelId = novelId.value
    fetchCharacters()
  }
  novelTitle.value = `小说 ${route.params.novelId}`

  textColorCustomizer.loadFromStorage()
  textColorCustomizer.applyCSSVariables()
})
</script>

<style scoped>
.character-manager-container {
  min-height: 100vh;
  background: var(--dark-bg);
  color: var(--text-primary);
  overflow: hidden;
  position: relative;
  font-family: var(--font-family);
}

/* 导航栏样式 */
.floating-nav {
  position: fixed;
  left: 30px;
  top: 50%;
  transform: translateY(-50%);
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 50px;
  padding: 20px 10px;
  display: flex;
  flex-direction: column;
  gap: 25px;
  z-index: 100;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.nav-item {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  color: var(--text-muted);
  font-size: 1.5rem;
}

.nav-item:hover { color: var(--neon-cyan); transform: scale(1.1); }
.nav-item.active { background: rgba(59, 130, 246, 0.2); color: var(--neon-blue); box-shadow: inset 0 0 20px rgba(59, 130, 246, 0.3), 0 0 20px rgba(59, 130, 246, 0.5); }

/* 主舞台 */
.main-stage {
  position: relative;
  z-index: 1;
  padding: 80px 120px;
  margin-left: 100px;
}

.stage-header {
  margin-bottom: 40px;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 30px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.logo-wrapper {
  position: relative;
}

.logo-text {
  font-size: 2.5rem;
  font-weight: 900;
  letter-spacing: 0.3em;
  background: linear-gradient(135deg, var(--neon-blue), var(--neon-cyan), var(--neon-purple));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 40px rgba(59, 130, 246, 0.5);
  margin: 0;
}

.engine-span {
  font-size: 1.5rem;
  font-weight: 300;
  letter-spacing: 0.2em;
  margin-left: 10px;
}

.glow-line {
  position: absolute;
  bottom: -10px;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(90deg, transparent, var(--neon-blue), var(--neon-cyan), transparent);
  border-radius: 2px;
  animation: glowPulse 2s ease-in-out infinite;
}

@keyframes glowPulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

.subtitle {
  font-size: 1.1rem;
  color: var(--text-secondary);
  margin-top: 30px;
}

.user-name {
  color: var(--neon-cyan);
  font-weight: 600;
}

/* 角色区域 */
.character-section {
  margin-bottom: 40px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.section-title {
  font-size: 1.5rem;
  color: var(--text-primary);
  margin: 0;
}

.create-character-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: linear-gradient(135deg, var(--neon-blue), var(--neon-cyan));
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.create-character-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(59, 130, 246, 0.4);
}

.create-character-btn svg {
  width: 20px;
  height: 20px;
}

/* 角色网格 */
.character-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 30px;
}

.character-card-wrapper {
  position: relative;
}

.glass-card {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 24px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  height: 100%;
}

.character-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.card-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--neon-blue), var(--neon-cyan), var(--neon-purple));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.character-card:hover .card-glow {
  opacity: 1;
}

.card-border-gradient {
  position: absolute;
  inset: 0;
  border-radius: 16px;
  padding: 1px;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.3), transparent, rgba(168, 85, 247, 0.3));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

/* 角色头像 */
.character-avatar {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, var(--neon-blue), var(--neon-purple));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.avatar-text {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
}

.character-name {
  font-size: 1.25rem;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.character-info {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.info-tag {
  padding: 2px 10px;
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 12px;
  font-size: 0.85rem;
  color: var(--neon-blue);
}

.character-desc {
  font-size: 0.9rem;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0 0 16px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn svg {
  width: 16px;
  height: 16px;
}

.edit-btn {
  background: rgba(59, 130, 246, 0.2);
  color: var(--neon-blue);
}

.edit-btn:hover {
  background: rgba(59, 130, 246, 0.3);
}

.delete-btn {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.delete-btn:hover {
  background: rgba(239, 68, 68, 0.3);
}

/* 创建卡片 */
.create-card {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 280px;
  cursor: pointer;
  border: 2px dashed var(--glass-border);
}

.create-card:hover {
  border-color: var(--neon-blue);
  transform: translateY(-5px);
}

.card-create-content {
  text-align: center;
}

.create-icon {
  width: 48px;
  height: 48px;
  color: var(--neon-blue);
  margin-bottom: 12px;
}

.create-card span {
  display: block;
  font-size: 1.1rem;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.create-hint {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin: 0;
}

/* 加载和空状态 */
.loading-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--glass-border);
  border-top-color: var(--neon-blue);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-icon {
  width: 80px;
  height: 80px;
  color: var(--neon-blue);
  margin-bottom: 16px;
}

/* 返回按钮 */
.back-section {
  margin-top: 40px;
  text-align: center;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 30px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.back-btn:hover {
  border-color: var(--neon-blue);
  color: var(--neon-blue);
}

.back-btn svg {
  width: 20px;
  height: 20px;
}

/* 额外字段样式 */
.extra-fields {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.extra-field-row {
  display: flex;
  gap: 10px;
  align-items: center;
}

.extra-key {
  flex: 1;
}

.extra-value {
  flex: 2;
}

/* 弹窗样式覆盖 */
.character-dialog :deep(.el-dialog) {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
}

.character-dialog :deep(.el-dialog__title) {
  color: var(--text-primary);
}

.character-dialog :deep(.el-form-item__label) {
  color: var(--text-primary);
}

.character-dialog :deep(.el-input__wrapper),
.character-dialog :deep(.el-textarea__inner),
.character-dialog :deep(.el-select__wrapper),
.character-dialog :deep(.el-input-number__wrapper) {
  background: var(--glass-bg);
  border-color: var(--glass-border);
  color: var(--text-primary);
  box-shadow: none;
}

.character-dialog :deep(.el-input__wrapper:hover),
.character-dialog :deep(.el-textarea__inner:hover),
.character-dialog :deep(.el-select__wrapper:hover) {
  border-color: var(--neon-blue);
}

.character-dialog :deep(.el-input__wrapper.is-focus),
.character-dialog :deep(.el-textarea__inner:focus),
.character-dialog :deep(.el-select__wrapper.is-focus) {
  border-color: var(--neon-blue);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.character-dialog :deep(.el-input__inner),
.character-dialog :deep(.el-select__placeholder),
.character-dialog :deep(.el-select-input) {
  color: var(--text-primary);
}

.character-dialog :deep(.el-option) {
  background: var(--dark-bg);
  color: var(--text-primary);
}

.character-dialog :deep(.el-option:hover) {
  background: rgba(59, 130, 246, 0.2);
}

.character-dialog :deep(.el-option.is-selected) {
  background: rgba(59, 130, 246, 0.3);
}

/* 响应式 */
@media (max-width: 1024px) {
  .main-stage {
    padding: 60px 40px;
    margin-left: 80px;
  }

  .floating-nav {
    left: 15px;
    padding: 15px 8px;
  }

  .nav-item {
    width: 40px;
    height: 40px;
    font-size: 1.2rem;
  }
}

@media (max-width: 768px) {
  .main-stage {
    padding: 40px 20px;
    margin-left: 70px;
  }

  .character-grid {
    grid-template-columns: 1fr;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
}
</style>
