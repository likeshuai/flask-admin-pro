import request from './request'

export function getStats(hours = 24) {
  return request({
    url: '/monitor/stats',
    method: 'get',
    params: { range: hours }
  })
}

export function getMonitorLogs(params = {}) {
  return request({
    url: '/monitor/logs',
    method: 'get',
    params
  })
}

export function getModels() {
  return request({
    url: '/models',
    method: 'get'
  })
}
