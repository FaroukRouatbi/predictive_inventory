import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getUnresolvedAlerts, getAllAlerts, resolveAlert, unresolveAlert } from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'

interface ReorderAlert {
    id: string
    product_id: string
    quantity_on_hand: number
    reorder_level: number
    recommended_reorder_quantity: number
    is_resolved: boolean
    resolved_at: string | null
    notes: string | null
    created_at: string
}

export default function AlertsPage() {
    const [tab, setTab] = useState<'active' | 'resolved'>('active')
    const queryClient = useQueryClient()

    const { data: activeAlerts, isLoading: loadingActive } = useQuery<ReorderAlert[]>({
        queryKey: ['alerts', 'active'],
        queryFn: getUnresolvedAlerts,
        refetchInterval: 30000,
    })

    const { data: allAlerts, isLoading: loadingAll } = useQuery<ReorderAlert[]>({
        queryKey: ['alerts', 'all'],
        queryFn: getAllAlerts,
    })

    const resolvedAlerts = allAlerts?.filter(a => a.is_resolved) ?? []

    const { mutate: resolve, isPending: resolving } = useMutation({
        mutationFn: (alertId: string) => resolveAlert(alertId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['alerts'] })
        },
    })

    const { mutate: revert, isPending: reverting } = useMutation({
        mutationFn: (alertId: string) => unresolveAlert(alertId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['alerts'] })
        },
    })

    const isLoading = loadingActive || loadingAll
    if (isLoading) return <LoadingSpinner />

    const currentAlerts = tab === 'active' ? activeAlerts ?? [] : resolvedAlerts

    return (
        <div className="space-y-8">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-white">Reorder Alerts</h2>
                    <p className="text-gray-400 text-sm mt-1">
                        Products that have dropped below their reorder threshold
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${(activeAlerts?.length ?? 0) > 0 ? 'bg-red-500 animate-pulse' : 'bg-green-500'
                        }`} />
                    <span className="text-sm text-gray-400">
                        {(activeAlerts?.length ?? 0) > 0
                            ? `${activeAlerts!.length} active alert${activeAlerts!.length > 1 ? 's' : ''}`
                            : 'All clear'}
                    </span>
                </div>
            </div>

            <div className="flex gap-1 bg-gray-900 border border-gray-800 rounded-lg p-1 w-fit">
                <button
                    onClick={() => setTab('active')}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${tab === 'active'
                            ? 'bg-indigo-600 text-white'
                            : 'text-gray-400 hover:text-white'
                        }`}
                >
                    Active
                    {(activeAlerts?.length ?? 0) > 0 && (
                        <span className="ml-2 bg-red-500 text-white text-xs rounded-full px-1.5 py-0.5">
                            {activeAlerts!.length}
                        </span>
                    )}
                </button>
                <button
                    onClick={() => setTab('resolved')}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${tab === 'resolved'
                            ? 'bg-indigo-600 text-white'
                            : 'text-gray-400 hover:text-white'
                        }`}
                >
                    Resolved
                    {resolvedAlerts.length > 0 && (
                        <span className="ml-2 bg-gray-600 text-white text-xs rounded-full px-1.5 py-0.5">
                            {resolvedAlerts.length}
                        </span>
                    )}
                </button>
            </div>

            {currentAlerts.length === 0 && (
                <div className="text-center py-24 bg-gray-900 border border-gray-800 rounded-xl">
                    <p className="text-4xl mb-3">{tab === 'active' ? '✅' : '📭'}</p>
                    <p className="text-white font-medium">
                        {tab === 'active' ? 'All stock levels are healthy' : 'No resolved alerts yet'}
                    </p>
                    <p className="text-gray-500 text-sm mt-1">
                        {tab === 'active'
                            ? 'No products are below their reorder threshold'
                            : 'Resolved alerts will appear here'}
                    </p>
                </div>
            )}

            <div className="space-y-4">
                {currentAlerts.map(alert => (
                    <div
                        key={alert.id}
                        className={`bg-gray-900 rounded-xl p-6 border ${alert.is_resolved ? 'border-gray-700 opacity-75' : 'border-red-500/20'
                            }`}
                    >
                        <div className="flex items-start justify-between gap-4">
                            <div className="space-y-3 flex-1">
                                <div className="flex items-center gap-3">
                                    <span className={`w-2 h-2 rounded-full ${alert.is_resolved ? 'bg-green-500' : 'bg-red-500 animate-pulse'
                                        }`} />
                                    <span className="text-xs text-gray-500 font-mono">
                                        {alert.product_id}
                                    </span>
                                    {alert.is_resolved && (
                                        <span className="text-xs text-green-500 font-medium">
                                            Resolved {alert.resolved_at
                                                ? new Date(alert.resolved_at).toLocaleString()
                                                : ''}
                                        </span>
                                    )}
                                </div>

                                <div className="grid grid-cols-3 gap-4">
                                    <div>
                                        <p className="text-xs text-gray-400 mb-1">Stock at Alert</p>
                                        <p className={`text-2xl font-bold ${alert.is_resolved ? 'text-gray-400' : 'text-red-400'
                                            }`}>
                                            {alert.quantity_on_hand}
                                        </p>
                                        <p className="text-xs text-gray-500">units remaining</p>
                                    </div>
                                    <div>
                                        <p className="text-xs text-gray-400 mb-1">Reorder Level</p>
                                        <p className="text-2xl font-bold text-yellow-400">
                                            {alert.reorder_level}
                                        </p>
                                        <p className="text-xs text-gray-500">minimum threshold</p>
                                    </div>
                                    <div>
                                        <p className="text-xs text-gray-400 mb-1">Recommended Order</p>
                                        <p className="text-2xl font-bold text-indigo-400">
                                            {alert.recommended_reorder_quantity}
                                        </p>
                                        <p className="text-xs text-gray-500">units to restock</p>
                                    </div>
                                </div>

                                {alert.notes && (
                                    <p className="text-xs text-gray-500 leading-relaxed border-t border-gray-800 pt-3">
                                        {alert.notes}
                                    </p>
                                )}

                                <p className="text-xs text-gray-600">
                                    Triggered: {new Date(alert.created_at).toLocaleString()}
                                </p>
                            </div>

                            {alert.is_resolved ? (
                                <button
                                    onClick={() => revert(alert.id)}
                                    disabled={reverting}
                                    className="shrink-0 px-4 py-2 bg-gray-700 hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-colors"
                                >
                                    Revert
                                </button>
                            ) : (
                                <button
                                    onClick={() => resolve(alert.id)}
                                    disabled={resolving}
                                    className="shrink-0 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-colors"
                                >
                                    Mark Resolved
                                </button>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}