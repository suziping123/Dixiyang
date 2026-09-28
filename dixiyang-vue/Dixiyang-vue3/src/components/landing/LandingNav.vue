<script setup lang="ts">
/**
 * 落地页顶栏：logo + GitHub/登录（单屏无滚动，无 scrolled 态）
 */
</script>

<template>
  <header class="ld-nav">
    <a class="ld-nav__logo" href="/">DIXIYANG<b>.</b></a>
    <div class="ld-nav__right">
      <a
        class="ld-nav__ext"
        href="https://github.com/suziping123/Dixiyang"
        target="_blank"
        rel="noopener noreferrer"
      >
        GitHub
        <svg viewBox="0 0 12 12" aria-hidden="true">
          <path
            d="M4.5 1.5h6v6M10.5 1.5 5 7M9 8.5v2h-7.5V3h2"
            stroke="currentColor"
            fill="none"
            stroke-width="1.2"
          />
        </svg>
        <span class="vh">（在新标签页打开）</span>
      </a>
      <RouterLink class="ld-nav__login" to="/login">登录</RouterLink>
    </div>
  </header>
</template>
