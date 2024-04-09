import { axiosPrivate } from '../common/axiosPrivate.js';

export function getTiposComunicacao({
  page=1,
  callBack=()=>{}
}) {
  const params = new URLSearchParams();
  params.append('format', 'json');
  if (page && page >1) {
    params.append('page', page);
  }
  axiosPrivate.get(
    '/bordado/api/tipo_comunicacao/',
    {params: params}
  )
  .then(response => {
    callBack(response.data);
  })
  .catch(error => {
    console.error('Erro ao obter Tipos de Comunicação via API:', error)
    callBack(null, error);
  });
}
