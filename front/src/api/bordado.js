import { axiosPrivate } from '../common/axiosPrivate.js';

export function getBordados(cliente_apelido, callBack) {
  const params = new URLSearchParams();
  params.append('format', 'json');
  params.append('cliente__apelido', cliente_apelido);

  axiosPrivate.get(
    '/bordado/api/bordado/',
    {params: params}
  )
  .then(response => {
    callBack(
      Array.from(
        new Set(
          response.data.results.map(
            bord => bord.nome
          )
        )
      )
    );
  })
  .catch(error => {
    console.error('Erro ao obter bordados de cliente via API:', error);
    callBack(null, error);
  });
}

export function getBordado({
  id=null,
  callBack=()=>{}
}) {
  const params = new URLSearchParams();
  params.append('format', 'json');
  axiosPrivate.get(
    `/bordado/api/bordado/${id}/`,
    {params: params}
  )
  .then(response => {
    callBack(response.data);
  })
  .catch(error => {
    console.error('Erro ao obter bordado '+id+' via API:', error)
    callBack(null, error);
  });
}

export function getBordadoFull({
  id=null,
  callBack=()=>{}
}) {
  const params = new URLSearchParams();
  params.append('format', 'json');
  axiosPrivate.get(
    `/bordado/api/bordado__full/${id}/`,
    {params: params}
  )
  .then(response => {
    callBack(response.data);
  })
  .catch(error => {
    console.error('Erro ao obter bordado '+id+' via API:', error)
    callBack(null, error);
  });
}

export function putBordado({
  id=null,
  payload={},  
  callBack=()=>{}
}) {
  const params = new URLSearchParams();
  params.append('format', 'json');
  console.log('putBordado', payload);
  axiosPrivate.put(
    `/bordado/api/bordado/${id}/`,
    payload,
    {params: params}
  )
  .then(response => {
    callBack(response.data);
  })
  .catch(error => {
    console.error('Erro ao gravar dados do bordado '+id+' via API:', error)
    callBack(null, error);
  });
}

