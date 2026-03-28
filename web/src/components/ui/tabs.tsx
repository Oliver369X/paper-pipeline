/* eslint-disable react-refresh/only-export-components -- envoltorios del primitivo Radix Tabs */
import * as TabsPrimitive from '@radix-ui/react-tabs'
import { cn } from '@/lib/utils'
import type { ComponentProps } from 'react'

export const Tabs = TabsPrimitive.Root

export const TabsList = ({
  className,
  ...props
}: ComponentProps<typeof TabsPrimitive.List>) => (
  <TabsPrimitive.List
    className={cn(
      'inline-flex h-10 items-center justify-start gap-1 rounded-md border border-zinc-800 bg-zinc-950/80 p-1 text-zinc-400',
      className,
    )}
    {...props}
  />
)

export const TabsTrigger = ({
  className,
  ...props
}: ComponentProps<typeof TabsPrimitive.Trigger>) => (
  <TabsPrimitive.Trigger
    className={cn(
      'inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium transition-colors',
      'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-500/50',
      'data-[state=active]:bg-zinc-800 data-[state=active]:text-zinc-100',
      'hover:text-zinc-200',
      className,
    )}
    {...props}
  />
)

export const TabsContent = ({
  className,
  ...props
}: ComponentProps<typeof TabsPrimitive.Content>) => (
  <TabsPrimitive.Content
    className={cn(
      'mt-4 outline-none focus-visible:ring-2 focus-visible:ring-violet-500/40 rounded-md',
      className,
    )}
    {...props}
  />
)
