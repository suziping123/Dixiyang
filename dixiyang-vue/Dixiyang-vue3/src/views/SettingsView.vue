<template>
  <div class="settings-container">
    <!-- 背景层 -->
    <div class="bg-gradient-animation"></div>

    <!-- 主容器 -->
    <div class="settings-wrapper">
      <!-- 侧边栏菜单 -->
      <aside class="settings-sidebar">
        <div class="sidebar-header">
          <h2 class="sidebar-title">⚙️ 设置</h2>
        </div>

        <nav class="settings-menu">
          <button
            v-for="category in categories"
            :key="category.id"
            class="menu-item"
            :class="{ active: activeCategory === category.id }"
            @click="activeCategory = category.id"
          >
            <span class="menu-icon">{{ category.icon }}</span>
            <span class="menu-label">{{ category.label }}</span>
          </button>
        </nav>

        <div class="sidebar-footer">
          <button class="btn-back" @click="goBack">
            ← 返回首页
          </button>
        </div>
      </aside>

      <!-- 主内容区 -->
      <main class="settings-content">
        <!-- Account Section -->
        <div v-show="activeCategory === 'account'" class="section-wrapper">
          <SettingsSection title="个人账户" description="管理你的账户信息和安全设置">
            <div class="form-group">
              <label class="form-label">昵称</label>
              <div class="input-wrapper">
                <input
                  v-model="accountForm.nickname"
                  type="text"
                  class="form-input"
                  placeholder="输入昵称"
                  @blur="saveAccountInfo"
                />
                <span class="input-hint">你在系统中显示的名字</span>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">邮箱</label>
              <div class="input-wrapper">
                <input
                  v-model="accountForm.email"
                  type="email"
                  class="form-input"
                  placeholder="输入邮箱地址"
                  @blur="saveAccountInfo"
                />
                <span class="input-hint">用于账户恢复和通知</span>
              </div>
            </div>

            <!-- TODO: [Account] 未来添加 - 修改密码表单 -->
            <!-- TODO: [Account] 未来添加 - 三方账户绑定（GitHub/Google等） -->
            <!-- TODO: [Account] 未来添加 - 账户升级/会员选项 -->
          </SettingsSection>
        </div>

        <!-- Display Section -->
        <div v-show="activeCategory === 'display'" class="section-wrapper">
          <SettingsSection title="背景与界面" description="自定义你的视觉体验">
            <BackgroundControl mode="full" />

            <!-- 字体系统 -->
            <div style="margin-top: 24px; padding-top: 24px; border-top: 1px solid rgba(255, 255, 255, 0.1)">
              <FontControl mode="full" />
            </div>

            <!-- TODO: [Display] 未来添加 - 对比度设置 -->
            <!-- TODO: [Display] 未来添加 - 界面语言选择 -->
          </SettingsSection>
        </div>

        <!-- Creation Section -->
        <div v-show="activeCategory === 'creation'" class="section-wrapper">
          <SettingsSection title="创作偏好" description="配置编辑器和创作工具的默认行为">
            <!-- 新小说默认配置 -->
            <div class="subsection">
              <h4 class="subsection-title">新小说配置</h4>
              <div class="form-group">
                <label class="form-label">默认笔名</label>
                <input
                  v-model="creationPrefs.defaultPenName"
                  type="text"
                  class="form-input"
                  placeholder="输入默认笔名"
                  @blur="saveCreationPrefs"
                />
              </div>
            </div>

            <!-- 角色编辑器偏好 -->
            <div class="subsection">
              <h4 class="subsection-title">角色编辑器</h4>
              <div class="form-group">
                <label class="form-label">默认性别</label>
                <select v-model="creationPrefs.defaultCharGender" class="form-input" @change="saveCreationPrefs">
                  <option value="">---</option>
                  <option value="male">男性</option>
                  <option value="female">女性</option>
                  <option value="other">其他</option>
                </select>
              </div>
              <div class="toggle-item">
                <label class="form-label">显示自定义属性</label>
                <button
                  class="toggle-switch"
                  :class="{ active: creationPrefs.showCustomProps }"
                  @click="creationPrefs.showCustomProps = !creationPrefs.showCustomProps; saveCreationPrefs()"
                >
                  <span></span>
                </button>
              </div>
            </div>

            <!-- 故事节点编辑器偏好 -->
            <div class="subsection">
              <h4 class="subsection-title">故事节点编辑器</h4>
              <div class="form-group">
                <label class="form-label">编辑器类型</label>
                <select v-model="creationPrefs.editorType" class="form-input" @change="saveCreationPrefs">
                  <option value="richtext">富文本编辑器</option>
                  <option value="markdown">Markdown编辑器</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">自动保存间隔（秒）</label>
                <input
                  v-model.number="creationPrefs.autoSaveInterval"
                  type="number"
                  min="10"
                  max="300"
                  class="form-input"
                  @blur="saveCreationPrefs"
                />
              </div>
              <div class="toggle-item">
                <label class="form-label">显示字数统计</label>
                <button
                  class="toggle-switch"
                  :class="{ active: creationPrefs.showWordCount }"
                  @click="creationPrefs.showWordCount = !creationPrefs.showWordCount; saveCreationPrefs()"
                >
                  <span></span>
                </button>
              </div>
            </div>

            <!-- 时间线显示偏好 -->
            <div class="subsection">
              <h4 class="subsection-title">时间线显示</h4>
              <div class="form-group">
                <label class="form-label">默认展开深度</label>
                <input
                  v-model.number="creationPrefs.timelineDefaultDepth"
                  type="number"
                  min="1"
                  max="5"
                  class="form-input"
                  @blur="saveCreationPrefs"
                />
              </div>
            </div>

            <!-- TODO: [创作偏好] 未来添加 - 性格特征预设库 -->
            <!-- TODO: [创作偏好] 未来添加 - 节点密度视图设置 -->
            <!-- TODO: [创作偏好] 未来添加 - 关联线条样式设置 -->
          </SettingsSection>
        </div>

        <!-- AI Section -->
        <div v-show="activeCategory === 'ai'" class="section-wrapper">
          <SettingsSection title="RAG 助手设置" description="配置 AI 建议和智能功能">
            <div class="subsection">
              <h4 class="subsection-title">建议类型</h4>
              <div class="checkbox-group">
                <label class="checkbox-item">
                  <input
                    v-model="aiPrefs.suggestions.character"
                    type="checkbox"
                    @change="saveAiPrefs"
                  />
                  <span class="checkbox-label">角色建议</span>
                  <span class="checkbox-desc">基于已有角色数据提供建议</span>
                </label>
                <label class="checkbox-item">
                  <input
                    v-model="aiPrefs.suggestions.story"
                    type="checkbox"
                    @change="saveAiPrefs"
                  />
                  <span class="checkbox-label">故事建议</span>
                  <span class="checkbox-desc">基于故事节点内容提供建议</span>
                </label>
                <label class="checkbox-item">
                  <input
                    v-model="aiPrefs.suggestions.relation"
                    type="checkbox"
                    @change="saveAiPrefs"
                  />
                  <span class="checkbox-label">关系建议</span>
                  <span class="checkbox-desc">基于小说关系提供建议</span>
                </label>
              </div>
            </div>

            <!-- TODO: [RAG助手] 未来添加 - AI模型选择（GPT-4/本地/Claude等） -->
            <!-- TODO: [RAG助手] 未来添加 - 提示词模板库 -->
            <!-- TODO: [RAG助手] 未来添加 - 建议数量和风格设置 -->
            <!-- TODO: [RAG助手] 未来添加 - 知识库微调设置 -->
          </SettingsSection>
        </div>

        <!-- Data Section -->
        <div v-show="activeCategory === 'data'" class="section-wrapper">
          <SettingsSection title="数据管理" description="备份、导出和管理你的创作数据">
            <div class="subsection">
              <h4 class="subsection-title">数据导出</h4>
              <p class="subsection-desc">导出你的创作数据为本地文件</p>
              <div class="button-group">
                <button class="btn-action" @click="handleExportAll">
                  📤 导出全部小说
                </button>
                <button class="btn-action" @click="handleExportCharacters">
                  📤 导出角色库
                </button>
              </div>
            </div>

            <!-- TODO: [数据管理] 未来添加 - 导入功能 -->
            <!-- TODO: [数据管理] 未来添加 - 版本历史面板（关联 StoryNode 编辑历史） -->
            <!-- TODO: [数据管理] 未来添加 - 小说分类管理 -->
            <!-- TODO: [数据管理] 未来添加 - 标签管理 -->
            <!-- TODO: [数据管理] 未来添加 - 自动备份设置 -->
            <!-- TODO: [数据管理] 未来添加 - 云同步选项 -->
          </SettingsSection>
        </div>

        <!-- Security Section -->
        <div v-show="activeCategory === 'security'" class="section-wrapper">
          <SettingsSection title="账户安全" description="管理登录会话和安全选项">
            <div class="subsection">
              <h4 class="subsection-title">登录会话</h4>
              <button class="btn-danger" @click="handleLogout">
                🚪 登出当前会话
              </button>
            </div>

            <!-- TODO: [账户安全] 未来添加 - 已登录设备列表 -->
            <!-- TODO: [账户安全] 未来添加 - 登录历史 -->
            <!-- TODO: [账户安全] 未来添加 - 两步验证设置 -->
            <!-- TODO: [账户安全] 未来添加 - IP白名单 -->
            <!-- TODO: [账户安全] 未来添加 - 活跃会话管理 -->
          </SettingsSection>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/UserStore'
import SettingsSection from '@/components/SettingsSection.vue'
import BackgroundControl from '@/components/BackgroundControl.vue'
import FontControl from '@/components/FontControl.vue'
import { useUser } from '@/composables/useUser'

const router = useRouter()
const userStore = useUserStore()
const { accountForm, saveAccountInfo } = useUser()

// 活跃的设置分类
const activeCategory = ref('account')

// 设置分类导航
const categories = [
  { id: 'account', label: '个人账户', icon: '👤' },
  { id: 'display', label: '背景与界面', icon: '🎨' },
  { id: 'creation', label: '创作偏好', icon: '✏️' },
  { id: 'ai', label: 'RAG助手', icon: '🤖' },
  { id: 'data', label: '数据管理', icon: '💾' },
  { id: 'security', label: '账户安全', icon: '🔒' },
]


// Creation 偏好设置
const creationPrefs = reactive({
  defaultPenName: localStorage.getItem('creation_defaultPenName') || '创作者',
  defaultCharGender: localStorage.getItem('creation_defaultCharGender') || 'female',
  showCustomProps: localStorage.getItem('creation_showCustomProps') !== 'false',
  editorType: localStorage.getItem('creation_editorType') || 'richtext',
  autoSaveInterval: parseInt(localStorage.getItem('creation_autoSaveInterval') || '60'),
  showWordCount: localStorage.getItem('creation_showWordCount') !== 'false',
  timelineDefaultDepth: parseInt(localStorage.getItem('creation_timelineDefaultDepth') || '2'),
})

// AI 偏好设置
const aiPrefs = reactive({
  suggestions: {
    character: localStorage.getItem('ai_sugg_character') !== 'false',
    story: localStorage.getItem('ai_sugg_story') !== 'false',
    relation: localStorage.getItem('ai_sugg_relation') !== 'false',
  },
})

// 保存创作偏好
const saveCreationPrefs = () => {
  localStorage.setItem('creation_defaultPenName', creationPrefs.defaultPenName)
  localStorage.setItem('creation_defaultCharGender', creationPrefs.defaultCharGender)
  localStorage.setItem('creation_showCustomProps', String(creationPrefs.showCustomProps))
  localStorage.setItem('creation_editorType', creationPrefs.editorType)
  localStorage.setItem('creation_autoSaveInterval', String(creationPrefs.autoSaveInterval))
  localStorage.setItem('creation_showWordCount', String(creationPrefs.showWordCount))
  localStorage.setItem('creation_timelineDefaultDepth', String(creationPrefs.timelineDefaultDepth))
}

// 保存 AI 偏好
const saveAiPrefs = () => {
  localStorage.setItem('ai_sugg_character', String(aiPrefs.suggestions.character))
  localStorage.setItem('ai_sugg_story', String(aiPrefs.suggestions.story))
  localStorage.setItem('ai_sugg_relation', String(aiPrefs.suggestions.relation))
}

// 导出全部小说
const handleExportAll = () => {
  console.log('导出全部小说功能（TODO：后端实现）')
  alert('导出功能开发中，敬请期待')
}

// 导出角色库
const handleExportCharacters = () => {
  console.log('导出角色库功能（TODO：后端实现）')
  alert('导出功能开发中，敬请期待')
}

// 登出
const handleLogout = () => {
  if (confirm('确认要登出当前会话吗？')) {
    userStore.logout()
    router.push('/login')
  }
}

// 返回首页
const goBack = () => {
  router.push('/home')
}
</script>

<style scoped>
:root {
  --glass-bg: rgba(255, 255, 255, 0.05);
  --glass-border: rgba(255, 255, 255, 0.15);
  --glass-border-hover: rgba(255, 255, 255, 0.3);
  --neon-primary: #3b82f6;
  --neon-cyan: #06b6d4;
  --dark-bg: #0a0a0c;
  --card-shadow: 0 20px 40px rgba(0,0,0,0.4);
  --glow-shadow: 0 0 20px rgba(59, 130, 246, 0.2);
}

.settings-container {
  min-height: 100vh;
  background: var(--dark-bg);
  color: white;
  overflow: hidden;
  position: relative;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

/* ============ 背景 ============ */
.bg-gradient-animation {
  position: fixed;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at 20% 50%, rgba(168, 85, 247, 0.08) 0%, transparent 50%),
              radial-gradient(circle at 80% 80%, rgba(59, 130, 246, 0.08) 0%, transparent 50%),
              radial-gradient(circle at 50% 0%, rgba(6, 182, 212, 0.05) 0%, transparent 50%),
              radial-gradient(circle at center, #1e1b4b 0%, var(--dark-bg) 70%);
  z-index: 0;
  animation: rotate 30s linear infinite;
  opacity: 0.5;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* ============ 主容器 ============ */
.settings-wrapper {
  position: relative;
  z-index: 1;
  display: flex;
  min-height: 100vh;
}

/* ============ 侧边栏 ============ */
.settings-sidebar {
  width: 280px;
  padding: 30px 20px;
  background: var(--glass-bg);
  backdrop-filter: blur(16px);
  border-right: 1px solid var(--glass-border);
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
}

.sidebar-header {
  margin-bottom: 30px;
}

.sidebar-title {
  font-size: 1.5rem;
  font-weight: 900;
  margin: 0;
  letter-spacing: -1px;
}

.settings-menu {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  text-align: left;
  font-weight: 500;
}

.menu-item:hover {
  color: var(--neon-primary);
  background: rgba(59, 130, 246, 0.05);
  border-color: rgba(59, 130, 246, 0.2);
}

.menu-item.active {
  color: white;
  background: rgba(59, 130, 246, 0.15);
  border-color: var(--neon-primary);
  box-shadow: inset 0 0 12px rgba(59, 130, 246, 0.1);
}

.menu-icon {
  font-size: 1.3rem;
}

.menu-label {
  flex: 1;
}

.sidebar-footer {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--glass-border);
}

.btn-back {
  width: 100%;
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.95rem;
  font-weight: 500;
}

.btn-back:hover {
  color: var(--neon-cyan);
  border-color: var(--neon-cyan);
  background: rgba(6, 182, 212, 0.05);
}

/* ============ 主内容区 ============ */
.settings-content {
  flex: 1;
  padding: 40px;
  overflow-y: auto;
}

.section-wrapper {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ============ 表单元素 ============ */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-weight: 600;
  color: white;
  font-size: 0.95rem;
}

.input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-input {
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--glass-border);
  border-radius: 10px;
  color: white;
  font-size: 0.95rem;
  transition: all 0.3s;
}

.form-input:focus {
  outline: none;
  border-color: var(--neon-primary);
  background: rgba(59, 130, 246, 0.05);
  box-shadow: 0 0 12px rgba(59, 130, 246, 0.2);
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.input-hint {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.5);
}

/* ============ Subsections ============ */
.subsection {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(59, 130, 246, 0.1);
  border-radius: 12px;
}

.subsection-title {
  font-size: 1rem;
  font-weight: 700;
  color: var(--neon-primary);
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.subsection-desc {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
}

/* ============ Toggle Switch ============ */
.toggle-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toggle-switch {
  width: 48px;
  height: 28px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid var(--glass-border);
  border-radius: 14px;
  cursor: pointer;
  position: relative;
  transition: all 0.3s;
}

.toggle-switch:hover {
  border-color: var(--neon-primary);
}

.toggle-switch.active {
  background: var(--neon-primary);
  border-color: var(--neon-primary);
}

.toggle-switch span {
  position: absolute;
  width: 24px;
  height: 24px;
  background: white;
  border-radius: 50%;
  top: 2px;
  left: 2px;
  transition: left 0.3s;
}

.toggle-switch.active span {
  left: 22px;
}

/* ============ Checkboxes ============ */
.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  transition: all 0.3s;
}

.checkbox-item:hover {
  background: rgba(59, 130, 246, 0.05);
}

.checkbox-item input[type='checkbox'] {
  width: 20px;
  height: 20px;
  cursor: pointer;
  accent-color: var(--neon-primary);
}

.checkbox-label {
  font-weight: 600;
  color: white;
  flex: 1;
}

.checkbox-desc {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.5);
  display: block;
  margin-top: 4px;
}

/* ============ Buttons ============ */
.button-group {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.btn-action {
  padding: 12px 20px;
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid var(--neon-primary);
  border-radius: 10px;
  color: var(--neon-primary);
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 600;
}

.btn-action:hover {
  background: rgba(59, 130, 246, 0.25);
  box-shadow: 0 0 12px rgba(59, 130, 246, 0.2);
}

.btn-danger {
  padding: 12px 20px;
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.5);
  border-radius: 10px;
  color: #ef4444;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 600;
}

.btn-danger:hover {
  background: rgba(239, 68, 68, 0.25);
  border-color: #ef4444;
  box-shadow: 0 0 12px rgba(239, 68, 68, 0.2);
}

/* ============ 响应式 ============ */
@media (max-width: 1024px) {
  .settings-wrapper {
    flex-direction: column;
  }

  .settings-sidebar {
    width: 100%;
    height: auto;
    border-right: none;
    border-bottom: 1px solid var(--glass-border);
    display: grid;
    grid-template-columns: auto 1fr auto;
    align-items: center;
    gap: 20px;
    padding: 20px;
    position: static;
  }

  .sidebar-header {
    margin-bottom: 0;
  }

  .settings-menu {
    flex-direction: row;
    gap: 12px;
  }

  .menu-item {
    padding: 10px 14px;
    font-size: 0.9rem;
  }

  .menu-label {
    display: none;
  }

  .settings-content {
    padding: 30px 20px;
  }

  .subsection {
    padding: 16px;
  }
}

@media (max-width: 768px) {
  .settings-content {
    padding: 20px;
  }

  .settings-menu {
    overflow-x: auto;
    gap: 8px;
  }

  .menu-item {
    padding: 8px 12px;
    font-size: 0.85rem;
    flex-shrink: 0;
  }

  .form-group {
    gap: 6px;
  }

  .form-input {
    font-size: 0.9rem;
    padding: 10px 14px;
  }

  .button-group {
    flex-direction: column;
  }

  .btn-action,
  .btn-danger {
    width: 100%;
  }
}
</style>
