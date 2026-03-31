import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { getProducts, getForecast } from '../api/client'
import StatCard from '../components/StatCard'
import LoadingSpinner from '../components/LoadingSpinner'
import {
    ComposedChart,
    Bar,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from 'recharts'

interface Product {
    id: string
    sku: string
    name: string
    category: string
}

interface ForecastResponse {
    product_id: string
    forecast_horizon_days: number
    predicted_demand: number
    daily_breakdown: number[]
    recommended_reorder_quantity: number
    safety_stock: number
    model_used: string
    model_selection_reason: string
    confidence_level: string
    risk_score: number
    risk_label: string
    trend_direction: string
    trend_strength: number
    seasonality_detected: boolean
    seasonality_strength: number
    based_on_days_of_history: number
    generated_at: string
}

const confidenceColor = (level: string) => {
    switch (level) {
        case 'high': return 'text-green-400'
        case 'medium': return 'text-yellow-400'
        default: return 'text-red-400'
    }
}

const riskColor = (label: string) => {
    switch (label) {
        case 'low': return 'text-green-400'
        case 'medium': return 'text-yellow-400'
        default: return 'text-red-400'
    }
}

const modelLabel = (model: string) => {
    switch (model) {
        case 'simple_moving_average': return 'Simple Moving Average'
        case 'weighted_moving_average': return 'Weighted Moving Average'
        case 'linear_trend': return 'Linear Trend'
        case 'seasonal': return 'Seasonal Model'
        default: return model
    }
}

const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
        return (
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-3 text-xs">
                <p className="text-gray-400 mb-1">Day {label}</p>
                {payload.map((entry: any) => (
                    <p key={entry.name} style={{ color: entry.color }}>
                        {entry.name}: {entry.value.toFixed(1)} units
                    </p>
                ))}
            </div>
        )
    }
    return null
}

export default function ForecastPage() {
    const [selectedProductId, setSelectedProductId] = useState<string>('')

    const { data: products, isLoading: loadingProducts } = useQuery<Product[]>({
        queryKey: ['products'],
        queryFn: getProducts,
    })

    const { data: forecast, isLoading: loadingForecast } = useQuery<ForecastResponse>({
        queryKey: ['forecast', selectedProductId],
        queryFn: () => getForecast(selectedProductId),
        enabled: !!selectedProductId,
    })

    if (loadingProducts) return <LoadingSpinner />

    const chartData = forecast?.daily_breakdown.map((val, i) => ({
        day: i + 1,
        demand: parseFloat(val.toFixed(2)),
        trend: parseFloat(val.toFixed(2)),
    })) ?? []

    return (
        <div className="space-y-8">
            <div>
                <h2 className="text-2xl font-bold text-white">Demand Forecast</h2>
                <p className="text-gray-400 text-sm mt-1">
                    AI-powered demand prediction with automatic model selection
                </p>
            </div>

            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                <label className="block text-sm font-medium text-gray-400 mb-2">
                    Select a product to forecast
                </label>
                <select
                    value={selectedProductId}
                    onChange={e => setSelectedProductId(e.target.value)}
                    className="w-full bg-gray-800 border border-gray-700 text-white rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                    <option value="">Choose a product...</option>
                    {products?.map(p => (
                        <option key={p.id} value={p.id}>
                            {p.name} ({p.sku})
                        </option>
                    ))}
                </select>
            </div>

            {loadingForecast && <LoadingSpinner />}

            {forecast && !loadingForecast && (
                <div className="space-y-6">
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                        <StatCard
                            label="Predicted Demand"
                            value={Math.round(forecast.predicted_demand)}
                            sub={`next ${forecast.forecast_horizon_days} days`}
                            accent
                        />
                        <StatCard
                            label="Reorder Quantity"
                            value={forecast.recommended_reorder_quantity}
                            sub="units to order"
                        />
                        <StatCard
                            label="Safety Stock"
                            value={forecast.safety_stock}
                            sub="buffer units"
                        />
                        <StatCard
                            label="History Used"
                            value={`${forecast.based_on_days_of_history} days`}
                            sub="of sales data"
                        />
                    </div>

                    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                        <h3 className="text-sm font-semibold text-white mb-6">
                            Daily Demand Forecast — Next {forecast.forecast_horizon_days} Days
                        </h3>
                        <ResponsiveContainer width="100%" height={300}>
                            <ComposedChart data={chartData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                                <XAxis
                                    dataKey="day"
                                    tick={{ fill: '#6b7280', fontSize: 11 }}
                                    label={{
                                        value: 'Day',
                                        position: 'insideBottom',
                                        offset: -2,
                                        fill: '#6b7280',
                                        fontSize: 11
                                    }}
                                />
                                <YAxis
                                    tick={{ fill: '#6b7280', fontSize: 11 }}
                                    label={{
                                        value: 'Units',
                                        angle: -90,
                                        position: 'insideLeft',
                                        fill: '#6b7280',
                                        fontSize: 11
                                    }}
                                />
                                <Tooltip content={<CustomTooltip />} />
                                <Legend wrapperStyle={{ color: '#9ca3af', fontSize: 12 }} />
                                <Bar
                                    dataKey="demand"
                                    name="Daily Demand"
                                    fill="#4f46e5"
                                    fillOpacity={0.7}
                                    radius={[2, 2, 0, 0]}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="trend"
                                    name="Trend"
                                    stroke="#a78bfa"
                                    strokeWidth={2}
                                    dot={false}
                                />
                            </ComposedChart>
                        </ResponsiveContainer>
                    </div>

                    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-4">
                        <h3 className="text-sm font-semibold text-white">Model Selection</h3>
                        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
                            <div>
                                <p className="text-xs text-gray-400 mb-1">Model Used</p>
                                <p className="text-sm font-medium text-indigo-400">
                                    {modelLabel(forecast.model_used)}
                                </p>
                            </div>
                            <div>
                                <p className="text-xs text-gray-400 mb-1">Confidence</p>
                                <p className={`text-sm font-semibold capitalize ${confidenceColor(forecast.confidence_level)}`}>
                                    {forecast.confidence_level}
                                </p>
                            </div>
                            <div>
                                <p className="text-xs text-gray-400 mb-1">Risk Level</p>
                                <p className={`text-sm font-semibold capitalize ${riskColor(forecast.risk_label)}`}>
                                    {forecast.risk_label} ({forecast.risk_score.toFixed(2)})
                                </p>
                            </div>
                            <div>
                                <p className="text-xs text-gray-400 mb-1">Trend</p>
                                <p className="text-sm font-medium text-gray-300 capitalize">
                                    {forecast.trend_direction} (R²={forecast.trend_strength.toFixed(2)})
                                </p>
                            </div>
                        </div>
                        <div>
                            <p className="text-xs text-gray-400 mb-1">Selection Reason</p>
                            <p className="text-xs text-gray-500 leading-relaxed">
                                {forecast.model_selection_reason}
                            </p>
                        </div>
                    </div>

                    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                        <h3 className="text-sm font-semibold text-white mb-4">Seasonality</h3>
                        <div className="flex items-center gap-4">
                            <span className={`text-sm font-semibold ${forecast.seasonality_detected ? 'text-indigo-400' : 'text-gray-500'
                                }`}>
                                {forecast.seasonality_detected ? '✓ Detected' : '✗ Not Detected'}
                            </span>
                            {forecast.seasonality_detected && (
                                <span className="text-xs text-gray-400">
                                    Strength: {(forecast.seasonality_strength * 100).toFixed(1)}%
                                </span>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {!selectedProductId && (
                <div className="text-center py-16 text-gray-600">
                    <p className="text-4xl mb-3">📈</p>
                    <p className="text-sm">Select a product to generate a forecast</p>
                </div>
            )}
        </div>
    )
}