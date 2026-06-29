export interface EventType {
  value: string
  label: string
  color: string
  icon: string
}

export const EVENT_TYPES: EventType[] = [
  { value: 'birth', label: '出生', color: '#3b82f6', icon: '●' },
  { value: 'war', label: '战争', color: '#ef4444', icon: '■' },
  { value: 'politics', label: '政治', color: '#a855f7', icon: '▲' },
  { value: 'major', label: '转折', color: '#10b981', icon: '★' },
]

export function eventTypeLabel(t?: string): string {
  return EVENT_TYPES.find(e => e.value === t)?.label || '未知'
}

export function eventTypeConfig(t?: string): EventType {
  return EVENT_TYPES.find(e => e.value === t) || { value: '', label: '未知', color: '#6b7280', icon: '?' }
}

export const GENDER_COLORS: Record<string, { label: string; color: string; bg: string }> = {
  male: { label: '男', color: '#3b82f6', bg: 'rgba(59,130,246,0.15)' },
  female: { label: '女', color: '#ec4899', bg: 'rgba(236,72,153,0.15)' },
}

export function genderLabel(g?: string): string {
  if (g === '男' || g === 'male') return '男'
  if (g === '女' || g === 'female') return '女'
  return g || '未知'
}

export function genderStyle(g?: string): { color: string; bg: string } {
  if (g === '男' || g === 'male') return GENDER_COLORS.male
  if (g === '女' || g === 'female') return GENDER_COLORS.female
  return { color: '#6b7280', bg: 'rgba(107,114,128,0.15)' }
}
