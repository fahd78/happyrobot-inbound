/**
 * HappyRobot Carrier Sales Dashboard JavaScript
 */

// Configuration
const API_BASE_URL = window.location.origin.replace('http:', 'https:') + '/api/v1';
const API_KEY = 'dev-api-key-change-in-production'; // In production, get from secure storage

// API client with authentication
class APIClient {
    constructor(baseUrl, apiKey) {
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const headers = {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
            ...options.headers
        };

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    async getCallSummary(days = 30) {
        return this.request(`/calls/analytics/dashboard?days=${days}`);
    }

    async getRecentCalls(limit = 20) {
        return this.request(`/calls/dashboard/recent?limit=${limit}`);
    }
}

// Initialize API client
const api = new APIClient(API_BASE_URL, API_KEY);

// Dashboard data management
class Dashboard {
    constructor() {
        this.data = {
            summary: null,
            recentCalls: []
        };
    }

    async loadData() {
        try {
            // Load call summary
            this.data.summary = await api.getCallSummary();
            console.log('Summary data loaded:', this.data.summary);

            // Load recent calls
            this.data.recentCalls = await api.getRecentCalls();
            console.log('Recent calls loaded:', this.data.recentCalls);

            this.updateUI();
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.showError('Failed to load dashboard data');
        }
    }

    updateUI() {
        this.updateMetricCards();
        this.updateCharts();
        this.updateRecentCallsTable();
        this.updateLastUpdated();
    }

    updateMetricCards() {
        if (!this.data.summary) return;

        const { 
            total_calls, 
            successful_bookings, 
            conversion_rate
        } = this.data.summary;

        document.getElementById('totalCalls').textContent = total_calls || 0;
        document.getElementById('successfulBookings').textContent = successful_bookings || 0;
        document.getElementById('conversionRate').textContent = 
            conversion_rate ? `${conversion_rate.toFixed(1)}%` : '0%';
        
        // Calculate unique carriers from recent calls
        const uniqueCarriers = new Set(
            this.data.recentCalls
                .filter(call => call.carrier_mc_number)
                .map(call => call.carrier_mc_number)
        ).size;
        document.getElementById('totalCarriers').textContent = uniqueCarriers || 0;
    }

    updateCharts() {
        if (!this.data.summary) return;

        this.createOutcomeChart();
        this.createSentimentChart();
    }

    createOutcomeChart() {
        const outcomeData = this.data.summary.outcome_breakdown || {};
        
        const labels = Object.keys(outcomeData).map(this.formatOutcomeLabel);
        const values = Object.values(outcomeData);
        const colors = [
            '#10B981', '#EF4444', '#F59E0B', '#8B5CF6', 
            '#06B6D4', '#84CC16', '#F97316', '#EC4899'
        ];

        const data = [{
            labels: labels,
            values: values,
            type: 'pie',
            marker: { colors: colors },
            textinfo: 'label+percent',
            textposition: 'auto',
        }];

        const layout = {
            showlegend: true,
            margin: { t: 0, l: 0, r: 0, b: 0 },
            font: { family: 'Inter, sans-serif' }
        };

        Plotly.newPlot('outcomeChart', data, layout, { responsive: true });
    }

    createSentimentChart() {
        const sentimentData = this.data.summary.sentiment_breakdown || {};
        
        const labels = Object.keys(sentimentData).map(this.formatSentimentLabel);
        const values = Object.values(sentimentData);
        const colors = {
            'Positive': '#10B981',
            'Neutral': '#6B7280', 
            'Negative': '#EF4444',
            'Frustrated': '#F59E0B',
            'Satisfied': '#8B5CF6'
        };

        const data = [{
            x: labels,
            y: values,
            type: 'bar',
            marker: {
                color: labels.map(label => colors[label] || '#6B7280')
            }
        }];

        const layout = {
            xaxis: { title: 'Sentiment' },
            yaxis: { title: 'Number of Calls' },
            margin: { t: 20, l: 50, r: 20, b: 80 },
            font: { family: 'Inter, sans-serif' }
        };

        Plotly.newPlot('sentimentChart', data, layout, { responsive: true });
    }

    updateRecentCallsTable() {
        const tbody = document.getElementById('recentCallsTable');
        tbody.innerHTML = '';

        if (!this.data.recentCalls.length) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="px-6 py-4 text-center text-gray-500">
                        No recent calls found
                    </td>
                </tr>
            `;
            return;
        }

        this.data.recentCalls.forEach(call => {
            const row = this.createCallTableRow(call);
            tbody.appendChild(row);
        });
    }

    createCallTableRow(call) {
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50';

        const formatTime = (timeStr) => {
            if (!timeStr) return '--';
            return new Date(timeStr).toLocaleString();
        };

        const formatDuration = (seconds) => {
            if (!seconds) return '--';
            return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`;
        };

        const getOutcomeBadge = (outcome) => {
            if (!outcome) return '<span class="text-gray-500">--</span>';
            
            const badges = {
                'successful_booking': '<span class="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">Success</span>',
                'rejected_by_carrier': '<span class="bg-red-100 text-red-800 px-2 py-1 rounded-full text-xs">Rejected</span>',
                'failed_verification': '<span class="bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs">Failed Verification</span>',
                'no_suitable_loads': '<span class="bg-gray-100 text-gray-800 px-2 py-1 rounded-full text-xs">No Loads</span>',
                'negotiation_failed': '<span class="bg-orange-100 text-orange-800 px-2 py-1 rounded-full text-xs">Negotiation Failed</span>',
                'transferred_to_sales': '<span class="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">Transferred</span>'
            };
            
            return badges[outcome] || `<span class="text-gray-500">${outcome}</span>`;
        };

        const getSentimentBadge = (sentiment) => {
            if (!sentiment) return '<span class="text-gray-500">--</span>';
            
            const badges = {
                'positive': '<span class="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">Positive</span>',
                'neutral': '<span class="bg-gray-100 text-gray-800 px-2 py-1 rounded-full text-xs">Neutral</span>',
                'negative': '<span class="bg-red-100 text-red-800 px-2 py-1 rounded-full text-xs">Negative</span>',
                'frustrated': '<span class="bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs">Frustrated</span>',
                'satisfied': '<span class="bg-purple-100 text-purple-800 px-2 py-1 rounded-full text-xs">Satisfied</span>'
            };
            
            return badges[sentiment] || `<span class="text-gray-500">${sentiment}</span>`;
        };

        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${formatTime(call.start_time)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                ${call.carrier_mc_number || '--'}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${call.final_negotiated_rate ? '$' + parseFloat(call.final_negotiated_rate).toFixed(0) : '--'}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${getOutcomeBadge(call.outcome)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${getSentimentBadge(call.sentiment)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${call.discussed_load_id || '--'}
            </td>
        `;

        return row;
    }

    formatOutcomeLabel(outcome) {
        const labels = {
            'successful_booking': 'Successful Booking',
            'rejected_by_carrier': 'Rejected by Carrier',
            'failed_verification': 'Failed Verification',
            'no_suitable_loads': 'No Suitable Loads',
            'negotiation_failed': 'Negotiation Failed',
            'transferred_to_sales': 'Transferred to Sales',
            'call_dropped': 'Call Dropped',
            'system_error': 'System Error'
        };
        return labels[outcome] || outcome;
    }

    formatSentimentLabel(sentiment) {
        const labels = {
            'positive': 'Positive',
            'neutral': 'Neutral',
            'negative': 'Negative',
            'frustrated': 'Frustrated',
            'satisfied': 'Satisfied'
        };
        return labels[sentiment] || sentiment;
    }

    updateLastUpdated() {
        const now = new Date();
        document.getElementById('lastUpdated').textContent = now.toLocaleTimeString();
    }

    showError(message) {
        // Simple error display - could be enhanced with toast notifications
        console.error('Dashboard error:', message);
        
        // Show error in metric cards
        document.getElementById('totalCalls').textContent = 'Error';
        document.getElementById('successfulBookings').textContent = 'Error';
        document.getElementById('conversionRate').textContent = 'Error';
        document.getElementById('totalCarriers').textContent = 'Error';
    }
}

// Initialize dashboard
const dashboard = new Dashboard();

// Global functions
window.refreshData = function() {
    dashboard.loadData();
};

// Auto-refresh every 30 seconds
setInterval(() => {
    dashboard.loadData();
}, 30000);

// Load initial data when page loads
document.addEventListener('DOMContentLoaded', () => {
    dashboard.loadData();
});