import request from './request'

export function getStats(hours = 24) {
  return request({
    url: '/v1/stats',
    method: 'get',
    params: { hours }
  })
}

export function getHourlyStats(hours = 24) {
  return request({
    url: '/v1/stats/hourly',
    method: 'get',
    params: { hours }
  })
}
