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
