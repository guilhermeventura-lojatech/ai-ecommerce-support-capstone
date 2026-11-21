import type { SVGProps } from 'react'

type IconProps = SVGProps<SVGSVGElement>

const defaults = {
  width: 20,
  height: 20,
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.8,
  strokeLinecap: 'round' as const,
  strokeLinejoin: 'round' as const,
  'aria-hidden': true,
}

export function SparkIcon(props: IconProps) {
  return <svg {...defaults} {...props}><path d="m12 3 1.2 4.1L17 9l-3.8 1.9L12 15l-1.2-4.1L7 9l3.8-1.9L12 3Z"/><path d="m19 15 .7 2.3L22 18.5l-2.3 1.2L19 22l-.7-2.3-2.3-1.2 2.3-1.2L19 15Z"/></svg>
}

export function SendIcon(props: IconProps) {
  return <svg {...defaults} {...props}><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>
}

export function ShieldIcon(props: IconProps) {
  return <svg {...defaults} {...props}><path d="M12 22s8-3.5 8-10V5l-8-3-8 3v7c0 6.5 8 10 8 10Z"/><path d="m9 12 2 2 4-5"/></svg>
}

export function HumanIcon(props: IconProps) {
  return <svg {...defaults} {...props}><circle cx="12" cy="8" r="4"/><path d="M4 22c.7-5 3.3-7 8-7s7.3 2 8 7"/></svg>
}

export function InfoIcon(props: IconProps) {
  return <svg {...defaults} {...props}><circle cx="12" cy="12" r="9"/><path d="M12 11v5"/><path d="M12 8h.01"/></svg>
}

export function ChartIcon(props: IconProps) {
  return <svg {...defaults} {...props}><path d="M4 20V10"/><path d="M10 20V4"/><path d="M16 20v-7"/><path d="M22 20H2"/></svg>
}

export function BookIcon(props: IconProps) {
  return <svg {...defaults} {...props}><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2Z"/></svg>
}

