import { reactive } from 'vue'

/** 单字段校验规则（一条不通过即报错，按数组顺序短路） */
export interface FieldRule {
  /** 必填（空串/纯空格视为未填） */
  required?: boolean
  /** 正则校验（仅在值非空时执行） */
  pattern?: RegExp
  /** 最小长度（仅在值非空时执行） */
  min?: number
  /** 校验不通过时的提示文案；纯 validator 规则可省略（错误由 validator 返回） */
  message?: string
  /** 自定义/跨字段校验，返回 null 表示通过，返回字符串表示错误 */
  validator?: (value: string, form: Record<string, string>) => string | null
}

export type FieldRules = Record<string, FieldRule[]>

/**
 * 轻量表单校验：字段级实时错误 + 提交整体校验
 *
 * - `errors` 绑定到 `<FieldError :message="errors.k" />` 内联显示
 * - `validateField(k)` 绑 `@blur`，只查当前字段
 * - `validateAll()` 绑提交，全字段查（跨字段规则在此兜底）
 * - `clearAll()` 绑面板/模式切换，避免残留上一面板的错误
 *
 * @param rules 字段规则表
 * @param form  被校验的表单对象（跨字段 validator 的第二个参数）
 */
export function useFormValidation(rules: FieldRules, form: Record<string, string>) {
  const errors = reactive<Record<string, string>>({})

  const firstError = (key: string, value: string): string | null => {
    const list = rules[key]
    if (!list) return null
    const val = value ?? ''
    for (const rule of list) {
      // 内置规则统一兜底文案；纯 validator 规则的错误取自 validator 返回值
      const msg = rule.message ?? '输入有误'
      if (rule.required && !val.trim()) return msg
      if (!val) continue
      if (rule.min !== undefined && val.length < rule.min) return msg
      if (rule.pattern && !rule.pattern.test(val)) return msg
      if (rule.validator) {
        const err = rule.validator(val, form)
        if (err) return err
      }
    }
    return null
  }

  /** 单字段校验（blur 触发）；返回是否通过 */
  const validateField = (key: string): boolean => {
    const err = firstError(key, form[key] ?? '')
    if (err) errors[key] = err
    else delete errors[key]
    return !err
  }

  /**
   * 全字段校验（提交触发）；返回是否全部通过
   * @param keys 可选：只校验指定字段（如登录按当前模式只查 username/password 或 email/code）
   */
  const validateAll = (keys?: string[]): boolean => {
    const targets = keys ?? Object.keys(rules)
    let ok = true
    for (const key of targets) {
      if (!validateField(key)) ok = false
    }
    return ok
  }

  const clearError = (key: string): void => {
    delete errors[key]
  }

  const clearAll = (): void => {
    for (const key of Object.keys(errors)) delete errors[key]
  }

  return { errors, validateField, validateAll, clearError, clearAll }
}
