import axios from 'axios'

const http = axios.create({
  baseURL: '/api/v1',
  timeout: 12000
})

export default http
