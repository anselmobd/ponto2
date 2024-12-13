import { axiosPrivate } from '../common/axiosPrivate.js';

export function getLancamentos({
  page=1,
  page_size=null,
  cliente_apelido=null,
  tipo_lancamento=null,
  conciliada=null,
  ultima_data=null,
  ultimo_id=null,
  ate_ultimo_aberto=null,
  callBack=()=>{}
}) {
  const params = new URLSearchParams();
  params.append('format', 'json');
  if (page && page >1) {
    params.append('page', page);
  }
  if (page_size) {
    params.append('page_size', page_size);
  }
  if (cliente_apelido) {
    params.append('cliente__apelido', cliente_apelido);
  }
  if (tipo_lancamento) {
    params.append('tipo_lancamento', tipo_lancamento);
  }
  if (conciliada) {
    params.append('conciliada', conciliada);
  }
  if (ultima_data) {
    params.append('ultima_data', ultima_data);
  }
  if (ultimo_id) {
    params.append('ultimo_id', ultimo_id);
  }
  if (ate_ultimo_aberto) {
    params.append('ate_ultimo_aberto', ate_ultimo_aberto);
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
