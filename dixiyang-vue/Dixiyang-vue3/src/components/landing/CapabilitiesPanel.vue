<script setup lang="ts">
/**
 * 02 · 能力：01–05 紧凑索引行，每行配微型 DOM/SVG 演示（五种形态避免等行感）
 */
</script>

<template>
  <section
    id="panel-capabilities"
    class="ld-panel ld-p-caps"
    role="tabpanel"
    aria-labelledby="tab-capabilities"
  >
    <div class="ld-panel__head">
      <p class="ld-eyebrow" data-ld-in>
        CAPABILITIES <span class="zh">· 五件事，一条故事线</span>
      </p>
      <h2 class="ld-h2" data-ld-in>把散落的创作资料，收进同一个宇宙。</h2>
    </div>

    <ol class="ld-p-caps__list">
      <li class="ld-cap" data-ld-in>
        <span class="ld-cap__num" aria-hidden="true">01</span>
        <div>
          <h3 class="ld-cap__title">小说管理</h3>
          <p class="ld-cap__desc">
            一部小说一个宇宙：封面、列表、创建与删除，封面按 MD5 秒传去重。
          </p>
        </div>
        <div class="ld-cap__demo" aria-hidden="true">
          <div class="ld-demo-covers"><i></i><i></i><i></i></div>
        </div>
      </li>

      <li class="ld-cap" data-ld-in>
        <span class="ld-cap__num" aria-hidden="true">02</span>
        <div>
          <h3 class="ld-cap__title">角色卡</h3>
          <p class="ld-cap__desc">
            结构化设定，AI 能从对话里提取要点；角色一旦入卡，每次对话都带着它。
          </p>
        </div>
        <div class="ld-cap__demo" aria-hidden="true">
          <div class="ld-demo-chips">
            <span>姓名</span><span>动机</span><span>阵营</span><span>口头禅</span>
          </div>
        </div>
      </li>

      <li class="ld-cap" data-ld-in>
        <span class="ld-cap__num" aria-hidden="true">03</span>
        <div>
          <h3 class="ld-cap__title">时间线</h3>
          <p class="ld-cap__desc">
            主线与支线并行的层级结构，行内编辑——改设定不用再去翻文档。
          </p>
        </div>
        <div class="ld-cap__demo" aria-hidden="true">
          <svg viewBox="0 0 200 64" role="presentation">
            <path class="stroke" d="M6 32H194" />
            <path class="stroke" d="M60 32c20 0 16-18 36-18h40" />
            <circle class="fill" cx="6" cy="32" r="3.5" />
            <circle class="fill" cx="60" cy="32" r="3.5" />
            <circle class="fill" cx="140" cy="14" r="3.5" />
            <circle class="hot" cx="194" cy="32" r="4" />
            <circle class="fill" cx="100" cy="32" r="3.5" />
          </svg>
        </div>
      </li>

      <li class="ld-cap" data-ld-in>
        <span class="ld-cap__num" aria-hidden="true">04</span>
        <div>
          <h3 class="ld-cap__title">故事节点</h3>
          <p class="ld-cap__desc">
            节点挂在时间线之下，标注类型与重要性——剧情推进从此有迹可循。
          </p>
        </div>
        <div class="ld-cap__demo" aria-hidden="true">
          <svg viewBox="0 0 200 64" role="presentation">
            <path class="stroke" d="M14 44h172" />
            <rect class="stroke" x="24" y="14" width="44" height="20" />
            <rect class="stroke" x="86" y="14" width="44" height="20" />
            <rect class="hot-stroke" x="148" y="14" width="38" height="20" />
            <circle class="fill" cx="46" cy="44" r="3" />
            <circle class="fill" cx="108" cy="44" r="3" />
            <circle class="hot" cx="167" cy="44" r="3.5" />
          </svg>
        </div>
      </li>

      <li class="ld-cap" data-ld-in>
        <span class="ld-cap__num" aria-hidden="true">05</span>
        <div>
          <h3 class="ld-cap__title">RAG 智能助手</h3>
          <p class="ld-cap__desc">
            创作、讨论、分析、头脑风暴、提问五种模式，检索你的知识库后再回答。
          </p>
        </div>
        <div class="ld-cap__demo" aria-hidden="true">
          <div class="ld-demo-chips">
            <span>创作</span><span>讨论</span><span>分析</span><span>头脑风暴</span><span>提问</span>
          </div>
        </div>
      </li>
    </ol>
  </section>
</template>
