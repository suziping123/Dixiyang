<template>
  <el-dialog
    :model-value="modelValue"
    :title="draftId ? '编辑草稿' : '写点子'"
    width="720px"
    :close-on-click-modal="false"
    @update:model-value="emit('update:modelValue', $event)"
    @open="init"
  >
    <div class="editor-body">
      <!-- 分区 -->
      <div class="field">
        <label class="field-label">分区</label>
        <div class="chip-group">
          <button
            v-for="c in CATEGORIES"
            :key="c.key"
            type="button"
            class="chip"
            :class="{ on: form.category === c.key }"
            @click="onCategoryChange(c.key)"
          >
            {{ c.label }}
          </button>
        </div>
      </div>

      <!-- 标题 -->
      <div class="field">
        <label class="field-label" for="idea-title">标题</label>
        <el-input id="idea-title" v-model="form.title" maxlength="100" show-word-limit placeholder="一句话说清你的点子" />
      </div>

      <!-- 来源（按分区显示；SourcePicker 与下架编辑共用；弹窗可见才挂载，避免页面加载即发请求） -->
      <SourcePicker
        v-if="modelValue && (form.category === 'character' || form.category === 'idea')"
        ref="srcPicker"
        :category="form.category"
        v-model="sourceRef"
        v-model:novel-id="sourceNovelId"
        @change="resetPreview"
      />

      <!-- 正文 -->
      <div class="field">
        <label class="field-label" for="idea-content">正文</label>
        <el-input
          id="idea-content"
          v-model="form.content"
          type="textarea"
          :rows="8"
          maxlength="20000"
          show-word-limit
          placeholder="写下你的灵感、设定或经验……"
          @input="resetPreview"
        />
      </div>

      <!-- 标签 -->
      <div class="field">
        <label class="field-label">标签（回车添加，最多 5 个）</label>
        <el-select
          v-model="form.tags"
          multiple
          filterable
          allow-create
          default-first-option
          :multiple-limit="5"
          :reserve-keyword="false"
          placeholder="如：世界观、写作技巧"
          @change="resetPreview"
        >
          <el-option v-for="t in hotTags" :key="t.tag" :label="`#${t.tag}`" :value="t.tag" />
        </el-select>
      </div>

      <!-- 配图 -->
      <div class="field">
        <label class="field-label">配图（{{ form.images.length }}/9，首张为封面；按住拖动可调整顺序）</label>
        <div
          class="img-grid"
          @pointerdown="onGridPointerDown"
          @pointermove="onGridPointerMove"
          @pointerup="onGridPointerUpWrapped"
          @pointercancel="onGridPointerUp"
        >
          <div
            v-for="(u, i) in form.images"
            :key="u"
            class="img-cell"
            :class="{ dragging: dragIndex === i, 'drop-target': overIndex === i }"
          >
            <img :src="u" alt="" draggable="false" />
            <button type="button" class="img-del" title="移除" @click="removeImage(i)">×</button>
            <span v-if="i === 0" class="img-cover-tag">封面</span>
          </div>
          <button
            v-if="form.images.length < 9"
            type="button"
            class="img-add"
            :disabled="uploading"
            @click="pickImage"
          >
            <span class="img-add-icon">＋</span>
            <span>{{ uploading ? '上传中…' : '添加图片' }}</span>
          </button>
          <img v-if="ghostSrc" class="drag-ghost" :src="ghostSrc" :style="ghostStyle" alt="" />
        </div>
        <input
          ref="fileInput"
          type="file"
          accept="image/jpeg,image/png,image/webp,image/gif"
          hidden
          @change="onFileChange"
        />
      </div>

      <!-- 预览面板 -->
      <div v-if="previewed" class="preview-panel">
        <div class="preview-head">
          <span class="preview-badge">已预览</span>
          <span class="preview-cat">{{ catLabel(form.category) }}</span>
          <b>{{ form.title || '（未命名）' }}</b>
        </div>
        <div class="preview-content">{{ form.content || '（空正文）' }}</div>
        <div v-if="previewNote" class="preview-note">{{ previewNote }}</div>
        <div v-if="previewTags.length" class="preview-tags">
          <span v-for="t in previewTags" :key="t" class="mini-tag">#{{ t }}</span>
        </div>
      </div>
      <div v-else class="preview-hint">发布前需先点击「预览」确认内容与附件来源。</div>
    </div>

    <template #footer>
      <div class="dialog-foot">
        <div v-if="publishError" class="publish-error" role="alert">{{ publishError }}</div>
        <div class="foot-btns">
          <el-button :loading="saving" @click="saveDraft">保存草稿</el-button>
          <el-button :loading="previewing" @click="doPreview">预览</el-button>
          <el-button type="primary" :disabled="!previewed" :loading="publishing" @click="doPublish">
            确认发布
          </el-button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  getDraft, createDraft, updateDraft, publishDraft,
  listTags, uploadIdeaImage,
  type IdeaCategory,
} from '@/api/ideaApi'
import { useImageDragSort } from '@/composables/useImageDragSort'
import SourcePicker from '@/components/idea/SourcePicker.vue'

const props = defineProps<{
  modelValue: boolean
  draftId: number | null
}>()

const emit = defineEmits<{
  'update:modelValue': [v: boolean]
  saved: []
  published: []
}>()

const CATEGORIES: { key: IdeaCategory; label: string }[] = [
  { key: 'idea', label: '点子' },
  { key: 'character', label: '角色' },
  { key: 'setting', label: '设定' },
  { key: 'timeline', label: '时间线' },
  { key: 'tech', label: '技术' },
]
const CATEGORY_LABEL: Record<string, string> = {
  idea: '点子', character: '角色', setting: '设定', timeline: '时间线', tech: '技术',
}
const catLabel = (c: string) => CATEGORY_LABEL[c] ?? c

const form = reactive({
  category: 'idea' as IdeaCategory,
  title: '',
  content: '',
  tags: [] as string[],
  images: [] as string[],
})
const sourceRef = ref('')
const sourceNovelId = ref<number | ''>('')
const srcPicker = ref<InstanceType<typeof SourcePicker> | null>(null)

const hotTags = ref<{ tag: string; count: number }[]>([])

const previewed = ref(false)
const previewing = ref(false)
const previewNote = ref('')
const saving = ref(false)
const publishing = ref(false)
const uploading = ref(false)
const publishError = ref('')
const fileInput = ref<HTMLInputElement | null>(null)

const previewTags = computed(() => form.tags)

// 配图拖拽排序（第一张=封面）；真拖过才重置预览（顺序变化影响发布内容）
const { dragIndex, overIndex, ghostSrc, ghostStyle, onGridPointerDown, onGridPointerMove, onGridPointerUp } =
  useImageDragSort(() => form.images)
const onGridPointerUpWrapped = (e: PointerEvent) => {
  const wasDragging = dragIndex.value != null
  onGridPointerUp(e)
  if (wasDragging) resetPreview()
}

const resetPreview = () => {
  previewed.value = false
  previewNote.value = ''
}

const unwrap = <T,>(res: unknown): T | null => {
  const r = res as { code?: number; msg?: string; data?: T }
  if (r && r.code === 200) return r.data as T
  ElMessage.warning((r && r.msg) || '操作失败')
  return null
}

// ---------- 分区切换（切分区必须清来源，防残留 id 被当 sessionId 上传） ----------

const onCategoryChange = (key: IdeaCategory) => {
  if (form.category === key) return
  form.category = key
  sourceRef.value = ''
  sourceNovelId.value = ''
  resetPreview()
}

// ---------- 来源对话级联已抽至 SourcePicker 组件 ----------

// ---------- 配图 ----------

const pickImage = () => fileInput.value?.click()

const onFileChange = async (e: Event) => {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return
  if (form.images.length >= 9) {
    ElMessage.warning('最多 9 张配图')
    return
  }
  uploading.value = true
  try {
    const res = await uploadIdeaImage(file)
    if (res.code === 200 && res.data) {
      form.images.push(res.data)
      resetPreview()
    } else {
      const msg = res.msg || '上传失败'
      ElMessage.warning(msg)
      publishError.value = msg
    }
  } finally {
    uploading.value = false
  }
}

const removeImage = (i: number) => {
  form.images.splice(i, 1)
  resetPreview()
}

// ---------- 打开初始化 ----------

const init = async () => {
  resetPreview()
  publishError.value = ''
  form.title = ''
  form.content = ''
  form.tags = []
  form.images = []
  form.category = 'idea'
  sourceRef.value = ''
  sourceNovelId.value = ''

  hotTags.value = unwrap<{ tag: string; count: number }[]>(await listTags(20)) ?? []

  if (props.draftId != null) {
    const d = unwrap<{
      category: IdeaCategory; title: string; content: string;
      tags: string[]; images?: string[]; sourceRef?: string | null;
    }>(await getDraft(props.draftId))
    if (d) {
      form.category = d.category
      form.title = d.title
      form.content = d.content
      form.tags = d.tags ?? []
      form.images = d.images ?? []
      sourceRef.value = d.sourceRef ?? ''
      // 交给 SourcePicker 反查所属小说并填充二级列表
      await nextTick()
      await srcPicker.value?.echo()
    }
  }
}

// ---------- 保存 / 预览 / 发布 ----------

const validate = (): string | null => {
  if (!form.title.trim()) return '请填写标题'
  if (!form.content.trim()) return '请填写正文'
  if (form.category === 'character' && !sourceRef.value) return '请选择来源角色'
  return null
}

const payload = () => ({
  category: form.category,
  title: form.title.trim(),
  content: form.content.trim(),
  tags: form.tags,
  images: form.images,
  ...(sourceRef.value ? { sourceRef: sourceRef.value } : {}),
})

const saveDraft = async () => {
  const err = validate()
  if (err) {
    publishError.value = err
    ElMessage.warning(err)
    return
  }
  saving.value = true
  try {
    const res =
      props.draftId != null
        ? await updateDraft(props.draftId, payload())
        : await createDraft(payload())
    const r = res as { code?: number; msg?: string }
    if (r.code === 200) {
      publishError.value = ''
      ElMessage.success('草稿已保存')
      emit('saved')
      if (props.draftId == null) emit('update:modelValue', false)
    } else {
      publishError.value = r.msg || '保存失败'
      ElMessage.warning(r.msg || '保存失败')
    }
  } finally {
    saving.value = false
  }
}

const doPreview = async () => {
  const err = validate()
  if (err) {
    publishError.value = err
    ElMessage.warning(err)
    return
  }
  previewing.value = true
  try {
    // 预览即生成附件来源摘要，确认后才允许发布（列表在 SourcePicker 内）
    if (form.category === 'character' && sourceRef.value) {
      const hit = srcPicker.value?.characters.find((c) => String(c.id) === sourceRef.value)
      previewNote.value = `附件：角色卡「${hit?.name ?? sourceRef.value}」，发布时导出完整人设供他人一键导入。`
    } else if (form.category === 'idea' && sourceRef.value) {
      const hit = srcPicker.value?.sessions.find((s) => s.sessionId === sourceRef.value)
      previewNote.value = `附件：对话快照「${hit?.title ?? '所选对话'}」，发布时导出整条对话链为只读快照。`
    } else {
      previewNote.value = '纯文字发布，无附件。'
    }
    previewed.value = true
    publishError.value = ''
  } finally {
    previewing.value = false
  }
}

const doPublish = async () => {
  if (!previewed.value) return
  publishError.value = ''
  // 发布前确保草稿已保存（新草稿先落库）
  saving.value = true
  let draftId = props.draftId
  try {
    if (draftId == null) {
      const res = (await createDraft(payload())) as { code?: number; msg?: string; data?: { id: number } }
      if (res.code !== 200) {
        publishError.value = res.msg || '保存草稿失败'
        ElMessage.warning(res.msg || '保存草稿失败')
        return
      }
      draftId = res.data!.id
    } else {
      const res = (await updateDraft(draftId, payload())) as { code?: number; msg?: string }
      if (res.code !== 200) {
        publishError.value = res.msg || '保存草稿失败'
        ElMessage.warning(res.msg || '保存草稿失败')
        return
      }
    }
  } finally {
    saving.value = false
  }

  publishing.value = true
  try {
    const res = (await publishDraft(draftId, true)) as { code?: number; msg?: string }
    if (res.code === 200) {
      publishError.value = ''
      ElMessage.success('发布成功')
      emit('published')
    } else {
      publishError.value = res.msg || '发布失败'
      ElMessage.warning(res.msg || '发布失败')
    }
  } finally {
    publishing.value = false
  }
}

watch(
  () => props.modelValue,
  (open) => {
    if (!open) resetPreview()
  },
)
</script>

<style scoped>
.editor-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 62vh;
  overflow-y: auto;
  padding-right: 4px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 600;
}

.chip-group {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.chip {
  padding: 6px 14px;
  border-radius: 999px;
  border: 1px solid var(--surface-glass-border);
  background: var(--surface-glass);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all var(--dur-fast) var(--ease-out);
}

.chip.on {
  background: var(--accent-soft-strong);
  border-color: var(--accent-primary);
  color: var(--accent-primary);
  font-weight: 600;
}

.preview-panel {
  border: 1px solid var(--accent-primary);
  background: var(--accent-soft);
  border-radius: var(--radius-md);
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.preview-head {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.preview-badge {
  font-size: 11px;
  background: var(--accent-primary);
  color: #fff;
  border-radius: 999px;
  padding: 2px 8px;
}

.preview-cat {
  font-size: 11px;
  color: var(--text-secondary);
  background: var(--surface-input);
  border-radius: 999px;
  padding: 2px 8px;
}

.preview-content {
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-on-card);
  white-space: pre-wrap;
  max-height: 180px;
  overflow-y: auto;
}

.preview-note {
  font-size: 12px;
  color: var(--accent-cyan);
}

.preview-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.mini-tag {
  font-size: 11px;
  color: var(--text-muted);
  background: var(--surface-input);
  border-radius: 4px;
  padding: 2px 6px;
}

.preview-hint {
  font-size: 12px;
  color: var(--text-muted);
  background: var(--surface-input);
  border-radius: var(--radius-sm);
  padding: 10px 12px;
}

.dialog-foot {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.foot-btns {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

/* 发布/保存失败的弹窗内错误条（与 ElMessage 双保险，保证失败必有可见提示） */
.publish-error {
  text-align: left;
  font-size: 13px;
  line-height: 1.5;
  color: var(--danger, #f56c6c);
  background: var(--danger-soft, rgba(245, 108, 108, 0.12));
  border: 1px solid var(--danger-border, rgba(245, 108, 108, 0.4));
  border-radius: var(--radius-sm);
  padding: 8px 12px;
}

/* 配图网格 */
.img-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(96px, 1fr));
  gap: 8px;
  touch-action: none; /* 触屏拖拽排序前提，否则先被页面滚动抢走 */
}

.img-cell.dragging {
  opacity: 0.35;
}

.img-cell.drop-target {
  outline: 2px solid var(--accent-primary);
  outline-offset: -2px;
}

.drag-ghost {
  position: fixed;
  width: 96px;
  height: 96px;
  object-fit: cover;
  border-radius: var(--radius-sm);
  pointer-events: none;
  z-index: 2000; /* 压过 el-dialog 内容 */
  opacity: 0.9;
  box-shadow: var(--shadow-card, 0 8px 24px rgba(0, 0, 0, 0.5));
}

.img-cell {
  position: relative;
  aspect-ratio: 1;
  border-radius: var(--radius-sm);
  overflow: hidden;
  border: 1px solid var(--glass-border);
  background: var(--surface-input);
}

.img-cell img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.img-del {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.65);
  color: #fff;
  font-size: 13px;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.img-del:hover {
  background: var(--danger, #f56c6c);
}

.img-cover-tag {
  position: absolute;
  left: 4px;
  bottom: 4px;
  font-size: 10px;
  color: #fff;
  background: var(--accent-primary);
  border-radius: 999px;
  padding: 1px 6px;
}

.img-add {
  aspect-ratio: 1;
  border-radius: var(--radius-sm);
  border: 1px dashed var(--glass-border);
  background: var(--surface-input);
  color: var(--text-muted);
  font-size: 12px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  transition: all var(--dur-fast) var(--ease-out);
}

.img-add:hover:not(:disabled) {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.img-add:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.img-add-icon {
  font-size: 20px;
  line-height: 1;
}

/* 移动端：来源双列下拉改单列，编辑体加高 */
@media (max-width: 768px) {
  .editor-body {
    max-height: 72vh;
  }
}
</style>
