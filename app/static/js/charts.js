/**
 * charts.js
 * Logic for initializing analytics charts using Chart.js
 */

document.addEventListener('DOMContentLoaded', () => {
    const dataElement = document.getElementById('chart-data');
    if (!dataElement) return;

    const chartData = JSON.parse(dataElement.dataset.charts);
    
    // Global Styles / Theme Colors
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#a0aec0' : '#4a5568';
    const gridColor = isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)';

    Chart.defaults.color = textColor;
    Chart.defaults.font.family = "'Inter', sans-serif";

    // 1. Income vs Expenses Trend (Grouped Bar)
    const trendCtx = document.getElementById('trendChart');
    if (trendCtx) {
        new Chart(trendCtx, {
            type: 'bar',
            data: {
                labels: chartData.trends.labels,
                datasets: [
                    {
                        label: 'Income',
                        data: chartData.trends.income,
                        backgroundColor: '#10b981', // green-500
                        borderRadius: 4
                    },
                    {
                        label: 'Expense',
                        data: chartData.trends.expense,
                        backgroundColor: '#ef4444', // red-500
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top', align: 'end' }
                },
                scales: {
                    x: { grid: { display: false } },
                    y: { grid: { color: gridColor }, beginAtZero: true }
                }
            }
        });
    }

    // 2. Spending by Category (Doughnut)
    const catCtx = document.getElementById('categoryChart');
    if (catCtx) {
        new Chart(catCtx, {
            type: 'doughnut',
            data: {
                labels: chartData.categories.labels,
                datasets: [{
                    data: chartData.categories.data,
                    backgroundColor: [
                        '#6366f1', '#f59e0b', '#ec4899', '#8b5cf6', 
                        '#10b981', '#3b82f6', '#f43f5e', '#64748b'
                    ],
                    borderWidth: 0,
                    hoverOffset: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'right' }
                },
                cutout: '70%'
            }
        });
    }

    // 3. Savings Trend (Line)
    const savingsCtx = document.getElementById('savingsChart');
    if (savingsCtx) {
        const gradient = savingsCtx.getContext('2d').createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, 'rgba(99, 102, 241, 0.2)');
        gradient.addColorStop(1, 'rgba(99, 102, 241, 0)');

        new Chart(savingsCtx, {
            type: 'line',
            data: {
                labels: chartData.savings.labels,
                datasets: [{
                    label: 'Net Savings',
                    data: chartData.savings.data,
                    borderColor: '#6366f1', 
                    backgroundColor: gradient,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: { grid: { display: false } },
                    y: { grid: { color: gridColor } }
                }
            }
        });
    }
});
