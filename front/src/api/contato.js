import { axiosPrivate } from '../common/axiosPrivate.js';

export function delContato(
  index,
  key,
  callBack
) {
  console.log(
    index,
    key,
    callBack
  );
  axiosPrivate.delete(
    `/bordado/api/contato/${key}/`,
  )
  .then(response => {
    callBack(index);
  })
  .catch(error => {
    console.error('Erro ao apagar "contato" via API:', error);
    callBack(-1);
  });
}

export function postContato({
  payload={},  
  callBack=()=>{}
}) {
  const params = new URLSearchParams();
  params.append('format', 'json');
  axiosPrivate.post(
    `/bordado/api/contato/`,
    payload,
    {params: params}
  )
  .then(response => {
    callBack(response.data);
  })
  .catch(error => {
    console.error('Erro ao adicionar contato via API:', error)
    callBack(null, error);
  });
}
