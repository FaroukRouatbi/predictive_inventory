import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getProducts, getAllInventory, recordSale } from '../api/client'
import StatCard from '../components/StatCard'
import StockBadge from '../components/StockBadge'
import LoadingSpinner from '../components/LoadingSpinner'

interface Product {
    id: string
    sku: string
    name: string
    category: string
    price_cents: number
    currency: string
}

interface InventoryItem {
    id: string
    product_id: string
    quantity_on_hand: number
    reorder_level: number
    location: string | null
}

interface SellModalProps {
    product: Product
    inventory: InventoryItem
    onClose: () => void
}

function SellModal({ product, inventory, onClose }: SellModalProps) {
    const queryClient = useQueryClient()
    const [quantity, setQuantity] = useState(1)
    const [error, setError] = useState<string | null>(null)

    const { mutate: sell, isPending } = useMutation({
        mutationFn: () => recordSale({
            product_id: product.id,
            inventory_id: inventory.id,
            quantity_sold: quantity,
            price_at_sale: product.price_cents,
        }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['inventory'] })
            queryClient.invalidateQueries({ queryKey: ['alerts'] })
            onClose()
        },
        onError: (err: any) => {
            setError(err?.response?.data?.detail ?? 'Sale failed. Please try again.')
        },
    })

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="bg-gray-900 border border-gray-700 rounded-2xl p-6 w-full max-w-md shadow-2xl">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h3 className="text-lg font-bold text-white">{product.name}</h3>
                        <p className="text-xs text-gray-400 font-mono mt-0.5">{product.sku}</p>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-gray-500 hover:text-white transition-colors text-xl leading-none"
                    >
                        ✕
                    </button>
                </div>

                <div className="grid grid-cols-2 gap-3 mb-6">
                    <div className="bg-gray-800 rounded-xl p-4">
                        <p className="text-xs text-gray-400 mb-1">Available Stock</p>
                        <p className="text-2xl font-bold text-white">{inventory.quantity_on_hand}</p>
                        <p className="text-xs text-gray-500">units</p>
                    </div>
                    <div className="bg-gray-800 rounded-xl p-4">
                        <p className="text-xs text-gray-400 mb-1">Unit Price</p>
                        <p className="text-2xl font-bold text-white">
                            ${(product.price_cents / 100).toFixed(2)}
                        </p>
                        <p className="text-xs text-gray-500">{product.currency}</p>
                    </div>
                </div>

                <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-400 mb-2">
                        Quantity to Sell
                    </label>
                    <div className="flex items-center gap-3">
                        <button
                            onClick={() => setQuantity(q => Math.max(1, q - 1))}
                            className="w-10 h-10 rounded-lg bg-gray-800 hover:bg-gray-700 text-white font-bold transition-colors"
                        >
                            −
                        </button>
                        <input
                            type="number"
                            min={1}
                            max={inventory.quantity_on_hand}
                            value={quantity}
                            onChange={e => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
                            className="flex-1 bg-gray-800 border border-gray-700 text-white text-center rounded-lg px-4 py-2.5 text-lg font-bold focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        />
                        <button
                            onClick={() => setQuantity(q => Math.min(inventory.quantity_on_hand, q + 1))}
                            className="w-10 h-10 rounded-lg bg-gray-800 hover:bg-gray-700 text-white font-bold transition-colors"
                        >
                            +
                        </button>
                    </div>
                </div>

                <div className="bg-indigo-600/10 border border-indigo-500/20 rounded-xl p-4 mb-6">
                    <div className="flex items-center justify-between">
                        <p className="text-sm text-gray-400">Total Revenue</p>
                        <p className="text-xl font-bold text-indigo-400">
                            ${((product.price_cents * quantity) / 100).toFixed(2)}
                        </p>
                    </div>
                    <div className="flex items-center justify-between mt-1">
                        <p className="text-xs text-gray-500">Stock after sale</p>
                        <p className={`text-sm font-semibold ${inventory.quantity_on_hand - quantity <= inventory.reorder_level
                                ? 'text-red-400'
                                : 'text-green-400'
                            }`}>
                            {inventory.quantity_on_hand - quantity} units
                            {inventory.quantity_on_hand - quantity <= inventory.reorder_level && (
                                <span className="ml-1 text-xs">⚠ below reorder level</span>
                            )}
                        </p>
                    </div>
                </div>

                {error && (
                    <div className="bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-3 mb-4">
                        <p className="text-red-400 text-sm">{error}</p>
                    </div>
                )}

                <div className="flex gap-3">
                    <button
                        onClick={onClose}
                        className="flex-1 px-4 py-2.5 bg-gray-800 hover:bg-gray-700 text-white text-sm font-medium rounded-lg transition-colors"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={() => sell()}
                        disabled={isPending || quantity > inventory.quantity_on_hand || quantity < 1}
                        className="flex-1 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-colors"
                    >
                        {isPending ? 'Processing...' : `Sell ${quantity} unit${quantity > 1 ? 's' : ''}`}
                    </button>
                </div>
            </div>
        </div>
    )
}

export default function InventoryPage() {
    const [selectedProduct, setSelectedProduct] = useState<Product | null>(null)
    const [selectedInventory, setSelectedInventory] = useState<InventoryItem | null>(null)

    const { data: products, isLoading: loadingProducts } = useQuery<Product[]>({
        queryKey: ['products'],
        queryFn: getProducts,
    })

    const { data: inventory, isLoading: loadingInventory } = useQuery<InventoryItem[]>({
        queryKey: ['inventory'],
        queryFn: getAllInventory,
    })

    if (loadingProducts || loadingInventory) return <LoadingSpinner />

    const inventoryMap = new Map(
        inventory?.map(item => [item.product_id, item])
    )

    const totalProducts = products?.length ?? 0
    const lowStockCount = inventory?.filter(
        i => i.quantity_on_hand <= i.reorder_level
    ).length ?? 0
    const outOfStockCount = inventory?.filter(
        i => i.quantity_on_hand === 0
    ).length ?? 0
    const totalUnits = inventory?.reduce(
        (sum, i) => sum + i.quantity_on_hand, 0
    ) ?? 0

    const handleSellClick = (product: Product) => {
        const inv = inventoryMap.get(product.id)
        if (inv) {
            setSelectedProduct(product)
            setSelectedInventory(inv)
        }
    }

    return (
        <div className="space-y-8">
            <div>
                <h2 className="text-2xl font-bold text-white">Inventory Overview</h2>
                <p className="text-gray-400 text-sm mt-1">
                    Real-time stock levels across all products
                </p>
            </div>

            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard label="Total Products" value={totalProducts} />
                <StatCard label="Total Units" value={totalUnits.toLocaleString()} />
                <StatCard
                    label="Low Stock"
                    value={lowStockCount}
                    sub="at or below reorder level"
                    accent={lowStockCount > 0}
                />
                <StatCard
                    label="Out of Stock"
                    value={outOfStockCount}
                    sub="needs immediate attention"
                    accent={outOfStockCount > 0}
                />
            </div>

            <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-800">
                    <h3 className="text-sm font-semibold text-white">All Products</h3>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-gray-800">
                                <th className="text-left px-6 py-3 text-xs text-gray-400 uppercase tracking-wider">Product</th>
                                <th className="text-left px-6 py-3 text-xs text-gray-400 uppercase tracking-wider">SKU</th>
                                <th className="text-left px-6 py-3 text-xs text-gray-400 uppercase tracking-wider">Category</th>
                                <th className="text-right px-6 py-3 text-xs text-gray-400 uppercase tracking-wider">Price</th>
                                <th className="text-right px-6 py-3 text-xs text-gray-400 uppercase tracking-wider">On Hand</th>
                                <th className="text-right px-6 py-3 text-xs text-gray-400 uppercase tracking-wider">Reorder At</th>
                                <th className="text-left px-6 py-3 text-xs text-gray-400 uppercase tracking-wider">Status</th>
                                <th className="text-right px-6 py-3 text-xs text-gray-400 uppercase tracking-wider">Action</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-800">
                            {products?.map(product => {
                                const inv = inventoryMap.get(product.id)
                                return (
                                    <tr
                                        key={product.id}
                                        className="hover:bg-gray-800/50 transition-colors"
                                    >
                                        <td className="px-6 py-4 font-medium text-white">{product.name}</td>
                                        <td className="px-6 py-4 text-gray-400 font-mono text-xs">{product.sku}</td>
                                        <td className="px-6 py-4 text-gray-400 capitalize">
                                            {product.category.toLowerCase()}
                                        </td>
                                        <td className="px-6 py-4 text-right text-gray-300">
                                            ${(product.price_cents / 100).toFixed(2)}
                                        </td>
                                        <td className="px-6 py-4 text-right font-semibold text-white">
                                            {inv?.quantity_on_hand ?? '—'}
                                        </td>
                                        <td className="px-6 py-4 text-right text-gray-400">
                                            {inv?.reorder_level ?? '—'}
                                        </td>
                                        <td className="px-6 py-4">
                                            {inv ? (
                                                <StockBadge
                                                    quantity={inv.quantity_on_hand}
                                                    reorderLevel={inv.reorder_level}
                                                />
                                            ) : (
                                                <span className="text-gray-600 text-xs">No inventory</span>
                                            )}
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            {inv && inv.quantity_on_hand > 0 ? (
                                                <button
                                                    onClick={() => handleSellClick(product)}
                                                    className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium rounded-lg transition-colors"
                                                >
                                                    Sell
                                                </button>
                                            ) : (
                                                <span className="text-gray-600 text-xs">—</span>
                                            )}
                                        </td>
                                    </tr>
                                )
                            })}
                        </tbody>
                    </table>
                </div>
            </div>

            {selectedProduct && selectedInventory && (
                <SellModal
                    product={selectedProduct}
                    inventory={selectedInventory}
                    onClose={() => {
                        setSelectedProduct(null)
                        setSelectedInventory(null)
                    }}
                />
            )}
        </div>
    )
}