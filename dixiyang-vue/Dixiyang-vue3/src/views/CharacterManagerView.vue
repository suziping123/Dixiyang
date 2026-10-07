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
    <div class="bg-gradient-animation"></div>

    <FloatingNav />

    <main class="main-stage">
      <NovelPageHeader page-title="角色管理" />

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
          <!-- 入场错峰：内联 --i 只给卡片壳，靠继承下发到子元素（不落到表单控件上） -->
          <div
            v-for="(character, index) in characters"
            :key="character.id"
            class="character-card-wrapper"
            :style="{ '--i': Math.min(index, 7) }"
          >
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
                  <span v-if="character.extra && Object.keys(character.extra).length > 0" class="info-tag settings-tag">📋 有设定</span>
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

          <!-- 幽灵卡无内联 --i：CSS 变量按内容宽度自动多占一格（手机上自动落到下一行） -->
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
          返回
        </button>
      </div>
    </main>

    <!-- 创建/编辑角色弹窗（width 用 min() 防窄屏 650px 超出视口挤掉底部按钮） -->
    <el-dialog
      v-model="showDialog"
      :title="isEditMode ? '编辑角色' : '创建新角色'"
      width="min(650px, 92vw)"
      class="character-dialog"
      @close="resetForm"
    >
      <el-form :model="form" label-position="top" class="character-form" @submit.prevent @keyup.enter="enterSubmit(saveCharacter, $event)">
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

    <!-- 删除确认弹窗（独立 .delete-dialog 类：手机上保持居中短弹窗，不套用底部抽屉） -->
    <el-dialog v-model="showDeleteDialog" title="确认删除" width="min(400px, 92vw)" class="character-dialog delete-dialog">
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
import FloatingNav from '@/components/FloatingNav.vue'
import NovelPageHeader from '@/components/NovelPageHeader.vue'
import { useBackgroundConfig } from '@/composables/useBackgroundConfig'
import { useTextColorCustomizer } from '@/composables/useTextColorCustomizer'
import type { Character, CharacterDTO } from '@/api/types'
import { getCharacterList, createCharacter, updateCharacter, deleteCharacter as deleteCharacterApi } from '@/api/characterApi'
import { useNovelStore } from '@/stores/novelStore'
import { enterSubmit } from '@/utils/enterSubmit'

const router = useRouter()
const route = useRoute()
const bgConfig = useBackgroundConfig()
const textColorCustomizer = useTextColorCustomizer()
const novelStore = useNovelStore()

const isLoading = ref(true)
const isSaving = ref(false)
const isDeleting = ref(false)
const characters = ref<Character[]>([])
const showDialog = ref(false)
const showDeleteDialog = ref(false)
const isEditMode = ref(false)
const deleteCandidate = ref<Character | null>(null)
const editingId = ref<number | null>(null)
const hoveredCard = ref<number | null>(null)

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
      extraFields.value.push({
        key,
        value: typeof value === 'object' && value !== null
          ? JSON.stringify(value)
          : String(value)
      })
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
  showDialog.value = true
}

const openEditDialog = (character: Character) => {
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
    await fetchCharacters()
  } catch (error) {
    console.error('保存角色失败:', error)
    ElMessage.error(isEditMode.value ? '更新失败' : '创建失败')
  } finally {
    isSaving.value = false
  }
}

const confirmDelete = (character: Character) => {
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
    novelStore.loadNovel(novelId.value)
  }

  textColorCustomizer.loadFromStorage()
  textColorCustomizer.applyCSSVariables()
})
</script>

<style scoped>
.character-manager-container {
  min-height: 100vh;
  background: transparent;
  color: var(--text-primary);
  overflow: hidden;
  position: relative;
  font-family: var(--font-family);
}

/* 主舞台 */
.main-stage {
  position: relative;
  z-index: 1;
  padding: 80px 120px;
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
  border-radius: var(--radius-sm);
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition:
    transform var(--dur) var(--ease-out),
    box-shadow var(--dur) var(--ease-out),
    filter var(--dur) var(--ease-out);
}

.create-character-btn:hover {
  transform: translateY(-2px);
  filter: brightness(1.06);
  box-shadow: 0 4px 20px var(--accent-soft-strong);
}

.create-character-btn:active {
  transform: translateY(0) scale(0.985);
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
  height: 100%;
}

.glass-card {
  /* 深色玻璃底板：backdrop-filter 只负责模糊背后内容、不提供底色，
     底板透明度过低（旧值 --glass-bg = rgba(255,255,255,.05)）时卡片看起来就是全透明。
     加 !important 是为了压过 main.css 里同名的全局 .glass-card。 */
  background: var(--glass-bg-strong) !important;
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  padding: 24px;
  position: relative;
  overflow: hidden;
  transition:
    transform var(--dur) var(--ease-out),
    box-shadow var(--dur) var(--ease-out),
    border-color var(--dur) var(--ease-out);
  height: 100%;
}

/* 入场：仅透明度错峰（--i 由内联 style 下发，见卡片模板）
   注意：祖先一旦存在生效的 transform/filter/will-change 就会生成 backdrop root，
   子元素 .glass-card 的 backdrop-filter 将采不到页面背景 → 卡片变全透明。
   故此处关键帧【只允许动 opacity】，禁止再加 transform。 */
@keyframes cardIn {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

.character-card-wrapper {
  animation: cardIn 320ms var(--ease-out) both;
  animation-delay: calc(var(--i, 0) * 40ms);
}

.character-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.character-card:hover {
  transform: translateY(-4px);
  border-color: var(--glass-border-hover);
  box-shadow: var(--shadow-card);
}

/* 触屏适配：无 hover 可依赖，按压时轻微内缩代替上浮 */
.character-card:active {
  transform: scale(0.985);
}

.card-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--neon-blue), var(--neon-cyan), var(--neon-purple));
  opacity: 0;
  transition: opacity var(--dur) var(--ease-out);
}

.character-card:hover .card-glow {
  opacity: 1;
}

.card-border-gradient {
  position: absolute;
  inset: 0;
  border-radius: var(--radius-md);
  padding: 1px;
  background: linear-gradient(135deg, var(--accent-soft-strong), transparent, var(--accent-soft-strong));
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
  margin: 0 auto 16px;
  /* 内描边 + 底部微光：与玻璃卡同一套质感，不再是一枚实心圆 */
  box-shadow:
    inset 0 0 0 1px rgba(255, 255, 255, 0.16),
    0 2px 10px rgba(0, 0, 0, 0.3);
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
  line-height: 1.3;
  /* 超长名字折行不溢出（手机上每行只能容 4~5 个汉字） */
  overflow-wrap: anywhere;
}

.character-info {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
  margin-bottom: 12px;
}

.info-tag {
  padding: 2px 10px;
  background: var(--accent-soft);
  border: 1px solid var(--accent-soft-strong);
  border-radius: 999px;
  font-size: 0.85rem;
  line-height: 1.5;
  color: var(--accent-primary);
  font-variant-numeric: tabular-nums;
}

.settings-tag {
  background: var(--accent-soft-strong);
  border-color: var(--accent-purple);
  color: var(--accent-purple);
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
  justify-content: center;
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
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  cursor: pointer;
  transition:
    background var(--dur-fast) var(--ease-out),
    color var(--dur-fast) var(--ease-out),
    transform var(--dur-fast) var(--ease-out);
}

.action-btn svg {
  width: 16px;
  height: 16px;
  transition: transform var(--dur) var(--ease-out);
}

.action-btn:hover svg {
  transform: scale(1.08);
}

.action-btn:active {
  transform: scale(0.97);
}

.edit-btn {
  background: var(--accent-soft);
  color: var(--accent-primary);
}

.edit-btn:hover {
  background: var(--accent-soft-strong);
}

.delete-btn {
  background: var(--danger-soft);
  color: var(--danger);
}

.delete-btn:hover {
  background: var(--danger-soft);
  box-shadow: inset 0 0 0 1px var(--danger-border);
}

/* 创建卡片：虚线幽灵卡，和实心角色卡形成层级区分 */
.create-card {
  min-height: 280px;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  border-style: dashed;
  cursor: pointer;
}

.create-card:hover {
  transform: translateY(-4px);
  border-style: solid;
  border-color: var(--accent-primary);
  box-shadow: var(--shadow-card);
}

.create-card:active {
  transform: scale(0.985);
}

.card-create-content {
  width: 100%;
}

.create-icon {
  width: 48px;
  height: 48px;
  color: var(--neon-blue);
  transition: transform var(--dur) var(--ease-out);
}

.create-card:hover .create-icon {
  transform: scale(1.12) rotate(90deg);
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
  opacity: 0.9;
}

.empty-state p {
  color: var(--text-secondary);
  font-size: 1rem;
}

/* 返回按钮 */
.back-section {
  margin-top: 40px;
  text-align: center;
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

/* 弹窗配色见文件末尾【非 scoped】样式块：
   scoped 的 `:deep()` 编译为 `.character-dialog[data-v-x] .el-dialog`（要求祖先带类），
   而 EP 把 class 透传落在对话框根节点 `.el-dialog` 自身 → 永久不匹配，规则形同死代码，故移除。 */

/* 响应式：三档沿用项目既有断点（1024 / 768 / 480） */
@media (max-width: 1024px) {
  .main-stage {
    padding: 60px 32px;
    /* 导航已改右侧悬浮球，去掉旧左侧竖条的 margin-left（否则整体偏左不居中） */
    margin-left: 0;
  }

  /* 平板：280px 下限在 1024 屏会挤出 4 列窄卡，降到 240px 收成 2~3 列 */
  .character-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 18px;
  }
}

@media (max-width: 768px) {
  .main-stage {
    padding: 32px 14px 24px;
    margin-left: 0;
  }

  .section-header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
    margin-bottom: 18px;
  }

  .section-title {
    font-size: 1.05rem;
  }

  .create-character-btn {
    padding: 9px 14px;
    font-size: 0.85rem;
    justify-content: center;
  }

  /* 150px 下限：375 屏自动两列（每卡 ≈166px），320 屏自动降单列，无需额外断点 */
  .character-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 12px;
  }

  /* 卡片紧凑：缩小内边距/头像/留白，避免移动端巨卡（信息一项不减） */
  .glass-card {
    padding: 12px 10px;
  }

  /* 触屏无 hover：去掉上浮改用按压反馈，避免“点一下跳一下” */
  .character-card:hover {
    transform: none;
  }

  .character-card:active {
    transform: scale(0.985);
  }

  .character-avatar {
    width: 40px;
    height: 40px;
    margin-bottom: 8px;
  }

  .avatar-text {
    font-size: 1rem;
  }

  .character-name {
    font-size: 0.95rem;
    margin-bottom: 4px;
  }

  .character-info {
    gap: 5px;
    margin-bottom: 8px;
  }

  .info-tag {
    padding: 1px 7px;
    font-size: 0.7rem;
  }

  .character-desc {
    font-size: 0.78rem;
    line-height: 1.45;
    margin-bottom: 10px;
    /* 固定两行高度：同排卡片按钮始终对齐（有/无描述都不塌） */
    min-height: 2.32em;
  }

  .card-actions {
    gap: 6px;
  }

  .action-btn {
    padding: 7px 4px;
    font-size: 0.78rem;
    gap: 4px;
  }

  .action-btn svg {
    width: 14px;
    height: 14px;
  }

  .create-card {
    min-height: 0;
    padding: 16px 10px;
  }

  .create-icon {
    width: 36px;
    height: 36px;
  }

  .create-card span {
    font-size: 0.9rem;
    margin-bottom: 4px;
  }

  .create-hint {
    font-size: 0.75rem;
  }

  .loading-state,
  .empty-state {
    padding: 40px 12px;
  }

  .empty-icon {
    width: 56px;
    height: 56px;
  }

  .empty-state p {
    font-size: 0.85rem;
  }

  .back-section {
    margin-top: 24px;
  }

  /* 弹窗相关的移动端规则（单列 / 底部抽屉 / 输入框字号）见末尾【非 scoped】样式块 */

  /* 键值对行：手机上两列 + 触控友好的删除按钮 */
  .extra-field-row {
    gap: 8px;
  }
}

@media (max-width: 480px) {
  .main-stage {
    padding: 28px 12px 20px;
  }

  .character-grid {
    gap: 10px;
  }

  /* 148px 宽的卡上 1px 渐变描边收益低于合成开销，超窄档关掉 */
  .card-border-gradient {
    display: none;
  }

  .novel-cover-thumb {
    width: 40px;
    height: 40px;
  }
}
</style>

<!--
  弹窗配色/移动端抽屉已【全站统一】到 src/assets/main.css 的 `.el-dialog` 规则，
  这里只保留本页专属覆写（性别/年龄两列改单列）。
  历史说明：scoped 的 `.character-dialog :deep(.el-dialog)` 会编译成
  `.character-dialog[data-v-x] .el-dialog`（要求祖先带类），而 Element Plus 2.13 把 dialog 的
  class 经 $attrs 透传到对话框根节点 `.el-dialog` 自身，故 scoped 规则永不匹配 —— 必须走全局样式。
-->
<style>
@media (max-width: 768px) {
  /* 本页表单的「性别 / 年龄」两列在手机上改单列（其余抽屉样式由全局 .el-dialog 提供） */
  .el-dialog .el-col {
    flex: 0 0 100%;
    max-width: 100%;
  }
}
</style>
