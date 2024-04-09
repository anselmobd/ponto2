import { axiosPrivate } from '../common/axiosPrivate.js';

export function getCobrancas({
  page=1,
  cliente_apelido=null,
  callBack=()=>{}
}) {
  const params = new URLSearchParams();
  params.append('format', 'json');
  if (page && page >1) {
    params.append('page', page);
  }
  if (cliente_apelido) {
    params.append('cliente__apelido', cliente_apelido);
  }
  axiosPrivate.get(
    '/bordado/api/cobranca/',
    {params: params}
  )
  .then(response => {
    callBack(response.data);
  })
  .catch(error => {
    console.error('Erro ao obter cobrancas via API:', error)
    callBack(null, error);
  });
}

export function getCobranca({
  id=null,
  callBack=()=>{}
}) {
  const params = new URLSearchParams();
  params.append('format', 'json');
  axiosPrivate.get(
    `/bordado/api/cobranca/${id}/`,
    {params: params}
  )
  .then(response => {
    callBack(response.data);
  })
  .catch(error => {
    console.error('Erro ao obter cobranca '+id+' via API:', error)
    callBack(null, error);
  });
}

export function addCobranca({
  payload={
    "cliente": {
      "apelido": null,
    },
    "tipo": null,
    "comunicacao_id": null,
    "nf": null,
    "valor": null,
    "data": null,
    "parcelamento": null,
    "pedidos_itens": []
  },  
  callBack=()=>{}
}) {
  const params = new URLSearchParams();
  params.append('format', 'json');
  console.log('addCobranca', payload);
  axiosPrivate.post(
    `/bordado/api/cobranca/`,
    payload,
    {params: params}
  )
  .then(response => {
    callBack(response.data);
  })
  .catch(error => {
    console.error('Erro ao adicionar cobranca via API:', error)
    callBack(null, error);
  });
}
