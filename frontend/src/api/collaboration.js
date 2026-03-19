import http from './http'

export const createAssignment = async (payload) => (await http.post('/collaboration/assignments', payload)).data
export const listAssignments = async () => (await http.get('/collaboration/assignments')).data
