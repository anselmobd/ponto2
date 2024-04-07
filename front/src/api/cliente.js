import { axiosPrivate } from '../common/axiosPrivate.js';

export function getClientes(callBack) {
  const params = new URLSearchParams();
  params.append('format', 'json');
  params.append('page_size', '999999');

  axiosPrivate.get(
    '/bordado/api/clientes/',
    {params: params}
  )
  .then(response => {
    callBack(response.data.results.map(
      clie => clie.apelido
    ));
  })
  .catch(error => {
    console.error('Erro ao obter clientes via API:', error);
    callBack(null, error);
  });
}

export function getCliente({
  id=null,
  callBack=()=>{}
}) {
  const params = new URLSearchParams();
  params.append('format', 'json');
  axiosPrivate.get(
    `/bordado/api/clientes/${id}/`,
    {params: params}
  )
  .then(response => {
    callBack(response.data);
  })
  .catch(error => {
    console.error('Erro ao obter cliente '+id+' via API:', error)
    callBack(null, error);
  });
}

export function putCliente({
  id=null,
  payload={},  
  callBack=()=>{}
}) {
  const params = new URLSearchParams();
  params.append('format', 'json');
  console.log('addCobranca', payload);
  axiosPrivate.put(
    `/bordado/api/clientes/${id}/`,
    payload,
    {params: params}
  )
  .then(response => {
    callBack(response.data);
  })
  .catch(error => {
    console.error('Erro ao gravar dados do cliente '+id+' via API:', error)
    callBack(null, error);
  });
}

