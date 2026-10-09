<template>
  <el-dialog
    :model-value="modelValue"
    title="修改帖子"
    width="720px"
    :close-on-click-modal="false"
    @update:model-value="emit('update:modelValue', $event)"
    @open="init"
  >
    <div class="editor-body">
      <div v-if="post?.status === 'removed'" class="removed-note">
        该帖已下架——下架期间只有你能看到。修改保存后可重新上架。
      </div>

      <div class="field">
        <label class="field-label">分区（不可更改）</label>
        <span class="cat-readonly">{{ catLabel(post?.category) }}</span>
      </div>

      <div class="field">
        <label class="field-label" for="post-edit-title">标题</label>
        <el-input id="post-edit-title" v-model="form.title" maxlength="100" show-word-limit placeholder="一句话说清你的点子" />
      </div>

      <div class="field">
        <label class="field-label" for="post-edit-content">正文</label>
        <el-input
          id="post-edit-content"
          v-model="form.content"
          type="textarea"
          :rows="8"
          maxlength="20000"
          show-word-limit
          placeholder="写下你的灵感、设定或经验……"
        />
      </div>

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
        >
          <el-option v-for="t in hotTags" :key="t.tag" :label="`#${t.tag}`" :value="t.tag" />
        </el-select>
      </div>

      <div class="field">
        <label class="field-label">配图（最多 9 张，首张为封面）</label>
        <div class="img-grid">
          <div v-for="(u, i) in form.images" :key="u" class="img-cell">
            <img :src="u" alt="" />
            <button type="button" class="img-del" title="移除" @click="form.images.splice(i, 1)">×</button>
            <span v-if="i === 0" class="img-cover-tag">封面</span>
          </div>
          <button
            v-if="form.images.length < 9"
            type="button"
            class="img-add"
            :disabled="uploading"
            @click="fileInput?.click()"
          >
            <span class="img-add-icon">＋</span>
            <span>{{ uploading ? '上传中…' : '添加图片' }}</span>
          </button>
        </div>
        <input
          ref="fileInput"
          type="file"
          accept="image/jpeg,image/png,image/webp,image/gif"
          hidden
          @change="onFileChange"
        />
      </div>
    </div>

    <template #footer>
      <div class="dialog-foot">
        <div v-if="saveError" class="publish-error" role="alert">{{ saveError }}</div>
        <div class="foot-btns">
          <el-button @click="emit('update:modelValue', false)">取消</el-button>
          <el-button type="primary" :loading="saving" @click="save">保存修改</el-button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { getPost, updatePost, listTags, uploadIdeaImage, type IdeaPostItem } from '@/api/ideaApi'

const props = defineProps<{
  modelValue: boolean
  postId: number
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', v: boolean): void
  (e: 'saved'): void
}>()

const CATEGORY_LABEL: Record<string, string> = {
  idea: '点子', character: '角色', setting: '设定', timeline: '时间线', tech: '技术',
}
const catLabel = (c?: string) => (c ? CATEGORY_LABEL[c] ?? c : '')

const post = ref<IdeaPostItem | null>(null)
const form = reactive({ title: '', content: '', tags: [] as string[], images: [] as string[] })
const hotTags = ref<{ tag: string; count: number }[]>([])
const fileInput = ref<HTMLInputElement>()
const uploading = ref(false)
const saving = ref(false)
const saveError = ref('')

const unwrap = <T,>(res: unknown): T | null => {
  const r = res as { code?: number; data?: T }
  return r && r.code === 200 ? (r.data as T) : null
}

const init = async () => {
  saveError.value = ''
  post.value = null
  form.title = ''
  form.content = ''
  form.tags = []
  form.images = []
  const [p, t] = await Promise.all([
    getPost(props.postId).then((r) => unwrap<IdeaPostItem>(r)),
    listTags(20).then((r) => unwrap<{ tag: string; count: number }[]>(r)),
  ])
  hotTags.value = t ?? []
  if (p) {
    post.value = p
    form.title = p.title
    form.content = p.content ?? ''
    form.tags = [...(p.tags ?? [])]
    form.images = [...(p.images ?? [])]
  } else {
    ElMessage.warning('帖子加载失败')
    emit('update:modelValue', false)
  }
}

const onFileChange = async (ev: Event) => {
  const input = ev.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return
  if (form.images.length >= 9) {
    ElMessage.warning('最多 9 张配图')
    return
  }
  uploading.value = true
  try {
    const res = (await uploadIdeaImage(file)) as { code?: number; msg?: string; data?: string }
    if (res.code === 200 && res.data) {
      form.images.push(res.data)
    } else {
      ElMessage.warning(res.msg || '上传失败')
    }
  } finally {
    uploading.value = false
  }
}

const save = async () => {
  if (!form.title.trim()) {
    saveError.value = '标题不能为空'
    return
  }
  saving.value = true
  saveError.value = ''
  try {
    const res = (await updatePost(props.postId, {
      title: form.title.trim(),
      content: form.content,
      tags: form.tags,
      images: form.images,
    })) as { code?: number; msg?: string }
    if (res.code === 200) {
      ElMessage.success(post.value?.status === 'removed' ? '已保存，可重新上架' : '已保存')
      emit('saved')
      emit('update:modelValue', false)
    } else {
      saveError.value = res.msg || '保存失败'
    }
  } finally {
    saving.value = false
  }
}
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

.removed-note {
  font-size: 13px;
  color: var(--danger, #f56c6c);
  background: var(--danger-soft, rgba(245, 108, 108, 0.12));
  border: 1px solid var(--danger-border, rgba(245, 108, 108, 0.4));
  border-radius: var(--radius-sm);
  padding: 8px 12px;
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

.cat-readonly {
  align-self: flex-start;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--accent-cyan);
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

.img-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(96px, 1fr));
  gap: 8px;
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

/* 移动端：编辑表单单列紧凑 */
@media (max-width: 768px) {
  .editor-body {
    max-height: 72vh;
  }
}
</style>
