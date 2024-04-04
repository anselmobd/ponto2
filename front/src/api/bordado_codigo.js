import { axiosPrivate } from '../common/axiosPrivate.js';

export function getBordadoCodigos(cliente_apelido, bordado, callBack) {
  const params = new URLSearchParams();
  params.append('format', 'json');
  params.append('cliente__apelido', cliente_apelido);
  params.append('nome', bordado);

  axiosPrivate.get(
    '/bordado/api/bordado/',
    {params: params}
  )
  .then(response => {
    callBack(response.data.results.map(
      bord => bord.codigo
    ));
  })
  .catch(error => {
    console.error('Erro ao obter códigos de bordado de cliente via API:', error);
    callBack(null, error);
  });
}
