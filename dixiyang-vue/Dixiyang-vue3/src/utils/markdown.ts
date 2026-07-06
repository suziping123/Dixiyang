import { marked } from 'marked'
import hljs from 'highlight.js'
import DOMPurify from 'dompurify'

marked.setOptions({ gfm: true, breaks: true })

const renderer = new marked.Renderer()
renderer.code = ({ text, lang }) => {
  const language = lang && hljs.getLanguage(lang) ? lang : ''
  let highlighted = text
  if (language) {
    try { highlighted = hljs.highlight(text, { language }).value }
    catch { highlighted = hljs.highlightAuto(text).value }
  } else {
    highlighted = hljs.highlightAuto(text).value
  }
  return `<pre><code class="hljs${language ? ` language-${language}` : ''}">${highlighted}</code></pre>`
}
marked.setOptions({ renderer })

export const renderMarkdown = (text: string) => {
  const raw = marked.parse(text) as string
  return DOMPurify.sanitize(raw, {
    ADD_TAGS: ['details', 'summary'],
    ADD_ATTR: ['open']
  })
}
