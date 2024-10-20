import { axiosPrivate } from '../common/axiosPrivate.js';

export function addPagamentoCobranca({
  payload={
    "pagamento": null,
    "cobranca": null,
    "valor": null,
  },  
  callBack=()=>{}
}) {
  const params = new URLSearchParams();
  params.append('format', 'json');
  console.log('addPagamentoCobranca', payload);
  axiosPrivate.post(
    `/bordado/api/pagamento_cobranca/`,
    payload,
    {params: params}
  )
  .then(response => {
    callBack(response.data);
  })
  .catch(error => {
    console.error('Erro ao adicionar pagamento_cobranca via API:', error)
    callBack(null, error);
  });
}
