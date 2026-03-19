import http from './http'

export const askQuestion = async (question) => (await http.post('/nl/query', { question })).data
export const getNLStatus = async () => (await http.get('/nl/status')).data
