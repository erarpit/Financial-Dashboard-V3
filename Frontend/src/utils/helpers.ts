export const formatPrice = (price: number): string => {
  if (price >= 1000) {
    return `₹${price.toFixed(0)}`
  } else if (price >= 100) {
    return `₹${price.toFixed(1)}`
  } else {
    return `₹${price.toFixed(2)}`
  }
}

export const formatPercentage = (change: number): string => {
  const sign = change > 0 ? '+' : ''
  return `${sign}${change.toFixed(2)}%`
}

export const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`
  } else if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}K`
  } else {
    return num.toString()
  }
}

export const formatDate = (dateString: string): string => {
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return dateString
  }
}