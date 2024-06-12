import { axiosPrivate } from '../common/axiosPrivate.js';
import { ddmmyyyyToDate, date2InputText } from "../utils/date.js";


function avaliarNullComoVazio(valor) {
  return valor === null ? "" : valor;
}

export function getPedidoItens({
  page=1,
  page_size=30,
  cliente_apelido=null,
  data_pedido=null,
  bordado_nome=null,
  bordado_codigo=null,
  tem_cobranca=null,
  callBack=()=>{}
}) {
  const params = new URLSearchParams();
  params.append('format', 'json');
  if (page && page >1) {
    params.append('page', page);
  }
  params.append('page_size', page_size);
  if (cliente_apelido) {
    params.append('pedido__cliente__apelido', cliente_apelido);
  }
  if (data_pedido) {
    const barras = data_pedido.split("/");
    const quant_barras = barras.length - 1;
    if (quant_barras == 2) {
      params.append('data_pedido', date2InputText(ddmmyyyyToDate(data_pedido)));
    } else if (quant_barras == 1) {
      const year = parseInt(barras[1], 10);
      params.append('data_pedido__year', year);
      const month = parseInt(barras[0], 10);
      params.append('data_pedido__month', month);
    } else if (quant_barras == 0) {
      const year = parseInt(barras[0], 10);
      params.append('data_pedido__year', year);
    }
  }
  if (tem_cobranca !== null) {
    if (tem_cobranca) {
      params.append('cobrancas__isnull', false);
    } else {
      params.append('cobrancas__isnull', true);
    }
  }
  if (bordado_nome) {
    params.append('bordado__nome', bordado_nome);
  }
  if (bordado_codigo) {
    params.append('bordado__codigo', bordado_codigo);
  }
  axiosPrivate.get(
    '/bordado/api/pedido_item/',
    {params: params}
  )
  .then(response => {
    response.data.results.forEach(element => {
      element.pedido.cliente.vazio = (
        element.pedido.cliente.nome+
        element.pedido.cliente.fansasia+
        avaliarNullComoVazio(element.pedido.cliente.cnpj9)+
        avaliarNullComoVazio(element.pedido.cliente.cnpj4)+
        avaliarNullComoVazio(element.pedido.cliente.cnpj2)+
        element.pedido.cliente.cep+
        element.pedido.cliente.logradouro+
        avaliarNullComoVazio(element.pedido.cliente.numero)+
        element.pedido.cliente.complemento+
        element.pedido.cliente.cidade+
        element.pedido.cliente.uf
      ) == '';
    });
    callBack(response.data);
  })
  .catch(error => {
    console.error('Erro ao obter pedido_itens via API:', error)
    callBack(null, error.message);
  });
}

export function getPedidoItem({
  id=null,
  callBack=()=>{}
}) {
  const params = new URLSearchParams();
  params.append('format', 'json');
  axiosPrivate.get(
    `/bordado/api/pedido_item/${id}/`,
    {params: params}
  )
  .then(response => {
    callBack(response.data);
  })
  .catch(error => {
    console.error('Erro ao obter pedido_item '+id+' via API:', error)
    callBack(null, error);
  });
}

export function addClienteBordado(
  data_pedido,
  cliente_apelido,
  bordado_nome,
  bordado_codigo,
  callBack
) {
  const params = new URLSearchParams();
  params.append('format', 'json');
  params.append('page_size', '999999');

  axiosPrivate.post(
    '/bordado/api/pedido_item/',
    {
      data_pedido: data_pedido,
      cliente: {apelido: cliente_apelido},
      bordado: {
        nome: bordado_nome,
        codigo: bordado_codigo
      }
    },
    {params: params},
  )
  .then(response => {
    callBack(response.data);
  })
  .catch(error => {
    console.error('Erro ao gravar "cliente / bordado" via API:', error);
    callBack(null, error.response.data);
  });
}

export function delClienteBordado(
  index,
  key,
  callBack
) {
  const params = new URLSearchParams();
  params.append('format', 'json');

  axiosPrivate.delete(
    `/bordado/api/pedido_item/${key}/`,
    {params: params},
  )
  .then(response => {
    callBack(index);
  })
  .catch(error => {
    console.error('Erro ao apagar "cliente / bordado" via API:', error);
    callBack(-1);
  });
}

export function saveFechamento({
  id=null,
  data_entrega=null,
  quantidade=null,
  valor_unitario=null,
  programacao=null,
  ajuste=null,
  callBack=()=>{}
}) {
  const params = new URLSearchParams();
  params.append('format', 'json');
  params.append('tipo', 'fechamento');

  axiosPrivate.put(
    `/bordado/api/pedido_item/${id}/`,
    {
      data_entrega: data_entrega,
      quantidade: quantidade,
      valor_unitario: valor_unitario,
      programacao: programacao,
      ajuste: ajuste
    },
    {params: params},
  )
  .then(response => {
    callBack(response.data);
  })
  .catch(error => {
    console.error('Erro ao salvar dados de fechamento via API:', error);
    callBack(null, error.response.data);
  });
}

export function delFechamento({
  id=null,
  callBack=()=>{}
}) {
  const params = new URLSearchParams();
  params.append('format', 'json');
  params.append('tipo', 'fechamento');

  axiosPrivate.delete(
    `/bordado/api/pedido_item/${id}/`,
    {params: params},
  )
  .then(response => {
    callBack(response.data);
  })
  .catch(error => {
    console.error('Erro ao apagar fechamento via API:', error);
    callBack(null, error.response.data);
  });
}
