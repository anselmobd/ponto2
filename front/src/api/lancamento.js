import { axiosPrivate } from '../common/axiosPrivate.js';

export function getLancamentos({
  page=1,
  cliente_apelido=null,
  tipo_lancamento=null,
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
  if (tipo_lancamento) {
    params.append('tipo_lancamento', tipo_lancamento);
  }
  axiosPrivate.get(
    '/bordado/api/lancamento/',
    {params: params}
  )
  .then(response => {
    callBack(response.data);
  })
  .catch(error => {
    console.error('Erro ao obter lançamentos via API:', error)
    callBack(null, error);
  });
}

export function addLancamento({
  payload={
    "cliente": {
      "apelido": null,
    },
    "data": null,
    "informacao": null,
    "valor": null,
  },  
  callBack=()=>{}
}) {
  const params = new URLSearchParams();
  params.append('format', 'json');
  console.log('addCobranca', payload);
  axiosPrivate.post(
    `/bordado/api/lancamento/`,
    payload,
    {params: params}
  )
  .then(response => {
    callBack(response.data);
  })
  .catch(error => {
    console.error('Erro ao adicionar lancamento via API:', error)
    callBack(null, error);
  });
}
