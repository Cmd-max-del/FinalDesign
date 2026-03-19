import http from './http'

export const getOverview = async () => (await http.get('/analytics/overview')).data
export const getTypeDistribution = async () => (await http.get('/analytics/type-distribution')).data
export const getHourDistribution = async () => (await http.get('/analytics/hour-distribution')).data
export const getDailyTrend = async () => (await http.get('/analytics/daily-trend')).data
export const getHeatPoints = async () => (await http.get('/analytics/heat-points')).data
