interface StockBadgeProps {
  quantity: number
  reorderLevel: number
}

export default function StockBadge({ quantity, reorderLevel }: StockBadgeProps) {
  const ratio = quantity / reorderLevel

  if (quantity === 0) {
    return (
      <span className="px-2 py-1 rounded-full text-xs font-semibold bg-red-500/20 text-red-400">
        Out of Stock
      </span>
    )
  }
  if (ratio <= 1) {
    return (
      <span className="px-2 py-1 rounded-full text-xs font-semibold bg-red-500/20 text-red-400">
        Low Stock
      </span>
    )
  }
  if (ratio <= 2) {
    return (
      <span className="px-2 py-1 rounded-full text-xs font-semibold bg-yellow-500/20 text-yellow-400">
        Monitor
      </span>
    )
  }
  return (
    <span className="px-2 py-1 rounded-full text-xs font-semibold bg-green-500/20 text-green-400">
      Healthy
    </span>
  )
}