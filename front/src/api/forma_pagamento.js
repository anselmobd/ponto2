import { axiosPrivate } from '../common/axiosPrivate.js';

export function getFormaPagamento({
  page=1,
  callBack=()=>{}
}) {
  const params = new URLSearchParams();
  params.append('format', 'json');
  if (page && page >1) {
    params.append('page', page);
  }
  axiosPrivate.get(
    '/bordado/api/forma_pagamento/',
    {params: params}
  )
  .then(response => {
    callBack(response.data);
  })
  .catch(error => {
    console.error('Erro ao obter Formas de pagamento via API:', error)
    callBack(null, error);
  });
}
