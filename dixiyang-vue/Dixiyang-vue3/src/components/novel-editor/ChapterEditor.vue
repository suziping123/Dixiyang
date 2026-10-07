<template>
  <div class="chapter-editor">
    <input
      class="chapter-title-input"
      :value="title"
      placeholder="章节标题"
      @input="$emit('update:title', ($event.target as HTMLInputElement).value)"
    />
    <div ref="editorHost" class="editor-host"></div>
    <div class="editor-status">
      <span class="status-item">{{ wordCountLabel }}</span>
      <span v-if="ghostText" class="status-item ghost-hint">Tab 接受补全 · Esc 取消</span>
      <span class="status-item save-hint">{{ saveHint }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { EditorState, StateEffect, StateField, type Extension } from '@codemirror/state'
import {
  Decoration,
  EditorView,
  WidgetType,
  keymap,
  lineNumbers,
  placeholder as cmPlaceholder,
  type DecorationSet,
  type ViewUpdate,
} from '@codemirror/view'
import { defaultKeymap, history, historyKeymap, insertNewline } from '@codemirror/commands'
import { bracketMatching, indentUnit } from '@codemirror/language'

const props = withDefaults(
  defineProps<{
    modelValue: string
    title?: string
    ghostText?: string
    saveHint?: string
    readOnly?: boolean
  }>(),
  { modelValue: '', title: '', ghostText: '', saveHint: '', readOnly: false },
)

const emit = defineEmits<{
  'update:modelValue': [content: string]
  'update:title': [title: string]
  'accept-ghost': []
  'reject-ghost': []
  'ai-trigger': []
  'doc-change': []
}>()

const editorHost = ref<HTMLElement | null>(null)
const wordCount = ref(0)
let view: EditorView | null = null
let applyingExternal = false

const wordCountLabel = computed(() => `${wordCount.value} 字`)

function countWords(text: string): number {
  return text.replace(/\s/g, '').length
}

class GhostTextWidget extends WidgetType {
  constructor(readonly text: string) {
    super()
  }
  toDOM() {
    const span = document.createElement('span')
    span.className = 'cm-ghost-text'
    span.textContent = this.text
    return span
  }
  ignoreEvent() {
    return false
  }
}

/** ghost text 更新信号（null 表示清除） */
const SetGhostEffect = StateEffect.define<string | null>()

const ghostField = StateField.define<DecorationSet>({
  create: () => Decoration.none,
  update(deco, tr) {
    for (const effect of tr.effects) {
      if (effect.is(SetGhostEffect)) {
        if (!effect.value) return Decoration.none
        const pos = Math.min(tr.state.selection.main.head, tr.state.doc.length)
        return Decoration.set([
          { from: pos, to: pos, value: Decoration.widget({ pos, side: 1, widget: new GhostTextWidget(effect.value) }) },
        ])
      }
    }
    if (tr.docChanged || tr.selection) {
      // 用户继续输入或移动光标 → 补全自动失效
      return Decoration.none
    }
    return deco
  },
  provide: (f) => EditorView.decorations.from(f),
})

function buildExtensions(): Extension[] {
  return [
    lineNumbers(),
    history(),
    bracketMatching(),
    indentUnit.of('  '),
    ghostField,
    EditorView.lineWrapping,
    cmPlaceholder('开始书写……'),
    EditorState.readOnly.of(props.readOnly),
    EditorView.updateListener.of((update: ViewUpdate) => {
      if (update.docChanged) {
        wordCount.value = countWords(update.state.doc.toString())
        if (!applyingExternal) {
          emit('update:modelValue', update.state.doc.toString())
          emit('doc-change')
        }
      }
    }),
    keymap.of([
      {
        key: 'Mod-Space',
        run: () => {
          emit('ai-trigger')
          return true
        },
      },
      // Tab 彻底废掉：有幽灵文本时接受补全，否则吞掉（不缩进、不移焦点）
      {
        key: 'Tab',
        run: () => {
          if (props.ghostText) emit('accept-ghost')
          return true
        },
        shift: () => true,
      },
      // 换行不复制行首缩进（覆盖 standardKeymap 的 insertNewlineAndIndent）
      {
        key: 'Enter',
        run: insertNewline,
        shift: insertNewline,
      },
      // 吞掉缩进类快捷键（前置，优先于 defaultKeymap 同名绑定）
      { key: 'Mod-[', run: () => true },
      { key: 'Mod-]', run: () => true },
      { key: 'Mod-Alt-\\', run: () => true },
      {
        key: 'Escape',
        run: () => {
          if (props.ghostText) {
            emit('reject-ghost')
            return true
          }
          return false
        },
      },
      ...defaultKeymap,
      ...historyKeymap,
    ]),
    EditorView.theme({
      '&': {
        height: '100%',
        backgroundColor: 'transparent',
        fontSize: '17px',
      },
      '.cm-scroller': {
        fontFamily: "'Georgia', 'Noto Serif SC', 'Songti SC', serif",
        lineHeight: '1.95',
        padding: '0 0 40vh 0',
        overflow: 'auto',
      },
      '.cm-content': {
        caretColor: 'var(--accent-primary)',
        maxWidth: '720px',
        margin: '0 auto',
        padding: '32px 24px 0',
        color: 'var(--text-primary)',
      },
      '.cm-line': {
        textIndent: '2em',
        // 底部 padding = 1.95em（≈一个空行），制造段落视觉间距；
        // 必须用 padding（计入 getBoundingClientRect，CM6 高度测量准确），不能用 margin
        padding: '0 4px 1.95em',
      },
      '&.cm-focused .cm-cursor': {
        borderLeftColor: 'var(--accent-primary)',
        borderLeftWidth: '2px',
      },
      '&.cm-focused .cm-selectionBackground, .cm-selectionBackground': {
        backgroundColor: 'rgba(75,139,245,0.28) !important',
      },
      '.cm-gutters': {
        backgroundColor: 'transparent',
        color: 'var(--text-disabled)',
        border: 'none',
      },
      '.cm-activeLineGutter': {
        backgroundColor: 'transparent',
      },
      '.cm-ghost-text': {
        color: 'rgba(168, 196, 255, 0.9)',
        fontStyle: 'italic',
        backgroundColor: 'rgba(75, 139, 245, 0.12)',
        borderRadius: '3px',
        padding: '0 3px',
        textDecoration: 'underline dotted rgba(120, 165, 255, 0.7)',
        textDecorationSkipInk: 'none',
        pointerEvents: 'none',
      },
    }),
  ]
}

function initEditor() {
  if (!editorHost.value) return
  view = new EditorView({
    state: EditorState.create({
      doc: props.modelValue,
      extensions: buildExtensions(),
    }),
    parent: editorHost.value,
  })
  wordCount.value = countWords(props.modelValue)
}

watch(
  () => props.modelValue,
  (next) => {
    if (!view) return
    const current = view.state.doc.toString()
    if (next === current) return
    applyingExternal = true
    const pos = view.state.selection.main.head
    view.dispatch({
      changes: { from: 0, to: current.length, insert: next },
      selection: { anchor: Math.min(pos, next.length) },
    })
    applyingExternal = false
  },
)

watch(
  () => props.ghostText,
  (ghost) => {
    view?.dispatch({ effects: SetGhostEffect.of(ghost || null) })
  },
)

onMounted(initEditor)
onBeforeUnmount(() => {
  view?.destroy()
  view = null
})

defineExpose({
  focus: () => view?.focus(),
  getCursorPos: () => view?.state.selection.main.head ?? 0,
  getDoc: () => view?.state.doc.toString() ?? '',
  getTextBefore: (maxChars = 2000) => {
    if (!view) return ''
    const pos = view.state.selection.main.head
    return view.state.doc.sliceString(Math.max(0, pos - maxChars), pos)
  },
  getTextAfter: (maxChars = 200) => {
    if (!view) return ''
    const pos = view.state.selection.main.head
    return view.state.doc.sliceString(pos, Math.min(view.state.doc.length, pos + maxChars))
  },
  insertAtCursor: (text: string) => {
    if (!view) return
    const { from, to } = view.state.selection.main
    view.dispatch({
      changes: { from, to, insert: text },
      selection: { anchor: from + text.length },
    })
    view.focus()
  },
  scrollCursorIntoView: () => {
    if (!view) return
    view.dispatch({
      effects: EditorView.scrollIntoView(view.state.selection.main.head, { y: 'center' }),
    })
  },
})
</script>

<style scoped>
.chapter-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-width: 0;
}

.chapter-title-input {
  border: none;
  background: transparent;
  color: var(--text-primary);
  font-size: 1.5rem;
  font-weight: 700;
  font-family: var(--font-family-serif);
  text-align: center;
  padding: 28px 24px 12px;
  outline: none;
  border-bottom: 1px solid transparent;
  transition: border-color var(--dur) var(--ease-out);
}
.chapter-title-input:focus {
  border-bottom-color: var(--surface-glass-border);
}
.chapter-title-input::placeholder {
  color: var(--text-disabled);
}

.editor-host {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.editor-status {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 8px 16px;
  font-size: 0.78rem;
  color: var(--text-muted);
  border-top: 1px solid var(--surface-glass-border);
  background: rgba(0, 0, 0, 0.22); /* 纸面内部分隔条，而非整块面板色 */
  flex-shrink: 0;
}
.ghost-hint {
  color: var(--accent-secondary);
}
.save-hint {
  color: var(--text-secondary);
}
</style>
