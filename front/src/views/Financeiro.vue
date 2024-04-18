<script setup>
import router from '@/router'
import { useRoute } from "vue-router";
import { ref, onMounted, watch } from 'vue'
import { getPedidoItens } from '../api/pedidoItem.js';
import { getCobrancas, addCobranca } from '../api/cobranca.js';
import { getLancamentos, addLancamento } from '../api/lancamento.js';
import { getTiposComunicacao } from '../api/tipo_comunicacao.js';
import { inputStrDate2PtBrDate, date2InputText } from "../utils/date.js";
import { ptBrCurrencyFormat } from "../utils/numStr.js";

const route = useRoute();

// valores recebidos de DB e seus controles de visualização

const pedido_itens = ref([])
const pedido_itens_carregando = ref(null)
const pedido_itens_error = ref(null)

const tipo_comunicacao = ref([])
const tipo_comunicacao_error = ref(null)

const cobrancas = ref([])
const cobrancas_carregando = ref(null)
const cobrancas_error = ref(null)

const lancamentos = ref([])
const lancamentos_carregando = ref(1)  // 0: carregado; 1: carregando; 2: carregando mais
const lancamentos_error = ref(null)
const lancamentos_next = ref(1);

// variaveis comuns

//    para inicializar com data atual

const dataAtual = new Date();
const strDataAtual = date2InputText(dataAtual);

// variáveis de inputs

const pedidos_selecionados = ref([])
const comunicado = ref({})
const lancamento = ref({})

// outros valores reativos

const status = ref('b'); // 'b' browsing; 'c' inserting comunicado; 'l' inserting lançamento

// get set refs

function clearComunicado() {
  comunicado.value = {
    valor_total: 0,
    informacao: '',
    nf: null,
    data: strDataAtual,
    parcelamento: '',
  };
}

function clearLancamento() {
  lancamento.value = {
    data: strDataAtual,
    informacao: '',
    valor: 0,
    saldo: 0,
  }
}

// DB API calls (do) and callbacks (cb)

function cbGetPedidoItens(data, error) {
  if (data) {
    if (data?.results) pedido_itens.value = data.results.map((ped_item) => {
      ped_item.valor_final =
        ped_item.quantidade * parseFloat(ped_item.preco)
        + parseFloat(ped_item.programacao) + parseFloat(ped_item.ajuste);
      ped_item.cobrado = ped_item.cobrancas.map((cobr) => {
        return parseFloat(cobr.valor)
      }).reduce((soma, valor) => soma + valor, 0);
      ped_item.cobrancas_ids = ped_item.cobrancas.map((cobr) => {
        return cobr.cobranca.id
      }).join(', ');
      ped_item.acobrar = ped_item.valor_final - ped_item.cobrado;
      return ped_item;
    });
  }
  if (error) {
    pedido_itens_error.value = error;
  };
  pedido_itens_carregando.value = false;
}

function doGetPedidoItens() {
  pedido_itens.value = [];
  pedido_itens_carregando.value = true;
  pedido_itens_error.value = null;
  getPedidoItens({
    cliente_apelido: route.params.apelido,
    callBack: cbGetPedidoItens
  });
}

function cbGetTiposComunicacao(data, error) {
  if (data) {
    tipo_comunicacao.value = data.results;
  }
  if (error) {
    tipo_comunicacao_error.value = "Erro ao buscar possíveis valores para Tipos de comunicação";
  };
}

function doGetTiposComunicacao() {
  tipo_comunicacao_error.value = null;
  getTiposComunicacao({
    callBack: cbGetTiposComunicacao
  });
}

function cbGetCobrancas(data, error) {
  if (data) {
    if (data?.results) cobrancas.value = data.results.map(cobranca => {
      cobranca.pedidos_ids = cobranca.pedidoitemcobranca_set.map( ped_item_cobr => {
        return ped_item_cobr.pedido_item.pedido.numero
      }).join(", ");
      return cobranca;
    });
    ;
  }
  if (error) {
    cobrancas_error.value = error;
  };
  cobrancas_carregando.value = false;
}

function doGetCobrancas(callBack) {
  cobrancas.value = [];
  cobrancas_carregando.value = true;
  cobrancas_error.value = null;
  getCobrancas({
    cliente_apelido: route.params.apelido,
    callBack: cbGetCobrancas
  });
}

function cbAddCobranca(data, error) {
  if (data) {
    status.value = 'b';
    pedidos_selecionados.value = [];
    clearComunicado();
    doGetPedidoItens();
    doGetCobrancas();
    doGetLancamentos(1);
  }
  if (error) {
    comunicado.value.error = error.response.data.human.join('|');
    comunicado.value.error_tech = error.response.data.tech.join('|');
  };
}

function doAddCobranca(callBack) {
  if (comunicado.value.cliente_nf & !comunicado.value.nf) {
    const answer = window.confirm('Padrão de cliente é gerar uma NF por cobrança. Retorna para informar NF?')
    if (answer) {
      return
    }
  }
  const payload= {
    "cliente": {
      "apelido": route.params.apelido,
    },
    "informacao": comunicado.value.informacao,
    "comunicacao_id": comunicado.value.comunicacao_id,
    "nf": comunicado.value.nf,
    "valor": comunicado.value.valor_total,
    "data": comunicado.value.data,
    "parcelamento": comunicado.value.parcelamento,
    "pedidos_itens": pedidos_selecionados.value,
  }
  addCobranca({
    payload: payload,
    callBack: cbAddCobranca
  });
}

function cbGetLancamentos(data, error) {
  if (data) {
    if (data?.results) {
      if (lancamentos_carregando.value == 1) {
        lancamentos.value = data.results;
      } else if (lancamentos_carregando.value == 2) {
        lancamentos.value = lancamentos.value.concat(data.results);
      }
      lancamentos_next.value = data.next;
    }
  }
  if (error) {
    lancamentos_error.value = error;
  };
  lancamentos_carregando.value = 0;
}

function doGetLancamentos(carregando) {
  lancamentos_carregando.value = carregando;
  if (lancamentos_carregando.value == 1) {
    lancamentos.value = [];
    lancamentos_next.value = 1;
  }
  lancamentos_error.value = null;
  getLancamentos({
    page: lancamentos_next.value,
    cliente_apelido: route.params.apelido,
    callBack: cbGetLancamentos
  });
}

function cbAddLancamento(data, error) {
  if (data) {
    status.value = 'b';
    clearLancamento();
    doGetLancamentos(1);
  }
  if (error) {
    lancamento.value.error = error.response.data.human.join('|');
    lancamento.value.error_tech = error.response.data.tech.join('|');
  };
}

function doAddLancamento(callBack) {
  const payload= {
    "cliente": {
      "apelido": route.params.apelido,
    },
    "data": lancamento.value.data,
    "informacao": lancamento.value.informacao,
    "valor": lancamento.value.valor,
  }
  addLancamento({
    payload: payload,
    callBack: cbAddLancamento
  });
}

// events

function handleInserirComunicadoClick(event) {
  event.preventDefault();
  comunicado.value.valor_total = pedido_itens.value.map((ped_item) => {
    return pedidos_selecionados.value.includes(ped_item.id) ? ped_item.acobrar : 0
  }).reduce((soma, valor) => soma + valor, 0);
  comunicado.value.comunicacao_id = pedido_itens.value[0].pedido.cliente.comunicacao;
  comunicado.value.parcelamento = pedido_itens.value[0].pedido.cliente.parcelamento;
  comunicado.value.cliente_nf = pedido_itens.value[0].pedido.cliente.nf;
  comunicado.value.data = strDataAtual;
  status.value = 'c';
}

function handleCancelaComunicadoClick(event) {
  event.preventDefault();
  status.value = 'b';
  clearComunicado();
}

function handleSalvaComunicadoClick(event) {
  event.preventDefault();
  doAddCobranca();
}

function handleInserirLancamentoClick(event) {
  event.preventDefault();
  lancamento.value.data = strDataAtual;
  status.value = 'l';
}

function handleCancelaLancamentoClick(event) {
  event.preventDefault();
  status.value = 'b';
  clearLancamento();
}

function handleSalvaLancamentoClick(event) {
  event.preventDefault();
  doAddLancamento();
}

function handleMaisLancamentosClick(event) {
  event.preventDefault();
  doGetLancamentos(2);
}

// Lifecycle Hooks

onMounted(() => {
  doGetTiposComunicacao();
  doGetPedidoItens();
  doGetCobrancas();
  doGetLancamentos(1);
})

</script>

<template>
  <div>
    <section id="titulo" class="flex pt-4 place-content-between">
      <h2 class="inline font-bold text-xl">Financeiro do cliente <span class="text-indigo-700">{{ route.params.apelido }}</span></h2>
      <a title="Voltar" class="button text-xl cursor-pointer" @click.prevent="router.go(-1)">&#x2190;</a>
    </section>

    <section id="preferencias_cliente" class="bg-slate-100 rounded p-4">
      <h3 class="font-bold text-center">Preferências do cliente</h3>
      <div class="flex items-center justify-around">
        <p>Forma de pagamento: <span class="font-bold">{{ pedido_itens?.length >0 ? pedido_itens[0].pedido.cliente.forma_pagamento_obj.nome : '...' }}</span></p>
        <p>Financeiro tipo conta corrente: <span class="font-bold">{{ pedido_itens?.length >0 ? (pedido_itens[0].pedido.cliente.conta_corrente ? 'Sim' : 'Não') : '...' }}</span></p>
      </div>
    </section>

    <section id="lista_pedidos">
      <h3 class="my-4 font-bold text-lg text-center">Pedidos</h3>
      <table class="w-full">
        <thead>
          <tr>
            <th rowspan="2">Seleção</th>
            <th rowspan="2">Data entrega</th>
            <th rowspan="2">Pedido</th>
            <th colspan="2">Bordado</th>
            <th rowspan="2">Valor</th>
            <th rowspan="2">Cobrado</th>
            <th rowspan="2">Cobrança</th>
            <th rowspan="2">A cobrar</th>
          </tr>
          <tr>
            <th>Nome</th>
            <th>Código</th>
          </tr>
          <tr v-if="pedido_itens_error">
            <th class="text-red-800" colspan="8">
              {{ pedido_itens_error }}
            </th>
          </tr>
          <tr v-if="tipo_comunicacao_error">
            <th class="text-red-800" colspan="8">
              {{ tipo_comunicacao_error }}
            </th>
          </tr>
          <tr v-if="pedido_itens_carregando">
            <td colspan="8">Carregando dados dos pedidos...</td>
          </tr>
          <tr v-if="!pedido_itens_carregando && (pedido_itens.length == 0)">
            <td colspan="8">Nenhum pedido encontrado</td>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="pedido_item in pedido_itens"
            :key="pedido_item.id"
          >
            <td>
              <input
                v-if="pedido_item.acobrar > 0"
                :disabled="status != 'b'"
                type="checkbox"
                :id="`pedido_item_${pedido_item.id}`"
                :name="`pedido_item_${pedido_item.id}`"
                :value="pedido_item.id"
                v-model="pedidos_selecionados"
              >
            </td>
            <td>{{ inputStrDate2PtBrDate(pedido_item.pedido.entrega) }}</td>
            <td>
              <router-link
                :to="{ name: 'fechando', params: { id: pedido_item.id } }"
                class="router-link text-sky-800"
                title="Dados do fechamento do pedido"
              >{{pedido_item.id}}</router-link>
            </td>
            <td>{{pedido_item.bordado.nome}}</td>
            <td>{{pedido_item.bordado.codigo}}</td>
            <td class="!text-right">{{ ptBrCurrencyFormat.format(pedido_item.valor_final) }}</td>
            <td class="!text-right">{{ ptBrCurrencyFormat.format(pedido_item.cobrado) }}</td>
            <td>{{ pedido_item.cobrancas_ids }}</td>
            <td class="!text-right">{{ ptBrCurrencyFormat.format(pedido_item.acobrar) }}</td>
          </tr>
        </tbody>
      </table>
    </section>

    <section id="insere_cobranca">
      <button
        :disabled="(!pedidos_selecionados.length) || (status != 'b')"
        class="px-2 py-1 rounded-xl bg-sky-700 font-bold text-slate-100"
        @click="handleInserirComunicadoClick"
      >Inserir/comunicar cobrança</button>
      <div v-if="status == 'c'">
        <h3 class="my-4 font-bold text-lg text-center">Inserindo/comunicando cobrança</h3>
        <table class="w-full">
          <thead>
            <tr>
              <th>Informação</th>
              <th>Comunicação</th>
              <th>NF</th>
              <th>Valor</th>
              <th>Data</th>
              <th>Parcelamento</th>
            </tr>
            <tr v-if="comunicado.error">
              <th class="text-red-800" colspan="5" :title="comunicado.error_tech">
                {{ comunicado.error }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>
                <input
                  class="mx-0.5 border border-solid border-slate-500 rounded"
                  v-model.trim="comunicado.informacao"
                  type="text"
                  name="informacao"
                  id="informacao"
                  placeholder="Informação"
                  v-focus
                >
              </td>
              <td>
                <select
                  class="mx-0.5 border border-solid border-slate-500 rounded"
                  v-model="comunicado.comunicacao_id"
                  name="comunicacao_id"
                  id="comunicacao_id"
                >
                  <option
                    v-for="tipo_comunic in tipo_comunicacao"
                    :key="tipo_comunic.id"
                    :value="tipo_comunic.id"
                    required
                  >{{ tipo_comunic.descricao }}</option>
                </select>
              </td>
              <td>
                <input
                  class="w-20 mx-0.5 border border-solid border-slate-500 rounded"
                  v-model="comunicado.nf"
                  type="number"
                  name="nf"
                  id="nf"
                  placeholder="999"
                >
              </td>
              <td>
                <input
                  class="w-36 mx-0.5 border border-solid border-slate-500 rounded"
                  v-model="comunicado.valor_total"
                  type="number"
                  step="0.01"
                  name="valor_total"
                  id="valor_total"
                  placeholder="0,00"
                  required
                >
              </td>
              <td>
                <input
                  class="mx-0.5 border border-solid border-slate-500 rounded"
                  v-model="comunicado.data"
                  type="date"
                  name="data"
                  id="data"
                  required
                >
              </td>
              <td>
                <input
                  class="mx-0.5 border border-solid border-slate-500 rounded"
                  v-model.trim="comunicado.parcelamento"
                  type="text"
                  name="parcelamento"
                  id="parcelamento"
                  placeholder="10 30 60"
                  list="parcelamento-list"
                  required
                >
                <datalist id="parcelamento-list">
                  <option>0</option>
                  <option>10</option>
                  <option>10 30 60</option>
                  <option>30 60 90</option>
                </datalist>
              </td>
            </tr>
          </tbody>
        </table>
        <p class="flex flex-row-reverse place-content-between">
          <button
            type="button"
            @click="handleSalvaComunicadoClick"
          >Grava</button>
          <button
            type="button"
            @click="handleCancelaComunicadoClick"
          >Cancela</button>
        </p>
      </div>
    </section>

    <section id="lista_comunicados">
      <h3 class="my-4 font-bold text-lg text-center">Comunicados de cobrança</h3>
      <table class="w-full">
        <thead>
          <tr>
            <th>Nº</th>
            <th>Informação</th>
            <th>Tipo</th>
            <th>NF</th>
            <th>Valor</th>
            <th>Pedido</th>
            <th>Data</th>
            <th>Parcelamento</th>
          </tr>
          <tr v-if="cobrancas_error">
            <th class="text-red-800" colspan="7">
              {{ cobrancas_error }}
            </th>
          </tr>
          <tr v-if="cobrancas_carregando">
            <td colspan="7">Carregando dados dos comunicados de cobrança...</td>
          </tr>
          <tr v-if="!cobrancas_carregando && (cobrancas.length == 0)">
            <td colspan="7">Nenhum comunicado de cobrança encontrado</td>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="cobranca in cobrancas"
            :key="cobranca.id"
          >
            <td>{{ cobranca.id }}</td>
            <td>{{ cobranca.informacao }}</td>
            <td>{{ cobranca.comunicacao.descricao }}</td>
            <td>{{ cobranca.nf }}</td>
            <td class="!text-right">{{ ptBrCurrencyFormat.format(cobranca.valor) }}</td>
            <td>{{ cobranca.pedidos_ids }}</td>
            <td>{{ inputStrDate2PtBrDate(cobranca.data) }}</td>
            <td>{{ cobranca.parcelamento }}</td>
          </tr>
        </tbody>
      </table>
    </section>
    
    <section id="insere_lancamento">
      <button
        :disabled="status != 'b'"
        class="px-2 py-1 rounded-xl bg-sky-700 font-bold text-slate-100"
        @click="handleInserirLancamentoClick"
      >Inserir lançamento</button>

      <div v-if="status == 'l'">
        <h3 class="my-4 font-bold text-lg text-center">Inserindo lançamento</h3>
        <table class="w-full">
          <thead>
            <tr>
              <th>Data</th>
              <th>Informação</th>
              <th>Valor</th>
            </tr>
            <tr v-if="lancamento.error">
              <th class="text-red-800" colspan="5" :title="lancamento.error_tech">
                {{ lancamento.error }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>
                <input
                  class="mx-0.5 border border-solid border-slate-500 rounded"
                  v-model="lancamento.data"
                  type="date"
                  name="data"
                  id="data"
                  required
                >
              </td>
              <td>
                <input
                  class="mx-0.5 border border-solid border-slate-500 rounded"
                  v-model.trim="lancamento.informacao"
                  type="text"
                  name="informacao"
                  id="informacao"
                  placeholder=""
                  list="informacao-list"
                  required
                  v-focus
                >
                <datalist id="informacao-list">
                  <option>boleto</option>
                  <option>depósito</option>
                  <option>dinheiro</option>
                </datalist>
              </td>
              <td>
                <input
                  class="w-36 mx-0.5 border border-solid border-slate-500 rounded"
                  v-model="lancamento.valor"
                  type="number"
                  step="0.01"
                  name="valor"
                  id="valor"
                  placeholder="0,00"
                  required
                >
              </td>
            </tr>
          </tbody>
        </table>
        <p class="flex flex-row-reverse place-content-between">
          <button
            type="button"
            @click="handleSalvaLancamentoClick"
          >Grava</button>
          <button
            type="button"
            @click="handleCancelaLancamentoClick"
          >Cancela</button>
        </p>
      </div>
    </section>

    <section id="lista_lancamentos">
      <h3 class="my-4 font-bold text-lg text-center">Lançamentos</h3>
      <table class="w-full">
        <thead>
          <tr>
            <th>Data</th>
            <th>Informação</th>
            <th>Comunicação</th>
            <th>NF</th>
            <th>Cobrança</th>
            <th>Parcela</th>
            <th>Valor</th>
            <th>Saldo</th>
          </tr>
          <tr v-if="lancamentos_error">
            <th class="text-red-800" colspan="8">
              {{ lancamentos_error }}
            </th>
          </tr>
          <tr v-if="!lancamentos_carregando && (lancamentos.length == 0)">
            <th colspan="8">Nenhum lançamento encontrado</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="lancamento in lancamentos"
            :key="lancamento.id"
          >
            <td>{{ inputStrDate2PtBrDate(lancamento.data) }}</td>
            <td>{{ lancamento?.cobranca ? lancamento.cobranca.informacao : lancamento.informacao }}</td>
            <td>{{ lancamento?.cobranca?.comunicacao?.descricao ? lancamento.cobranca.comunicacao.descricao : '-' }}</td>
            <td>{{ lancamento?.cobranca?.nf ? lancamento.cobranca.nf : '-' }}</td>
            <td>{{ lancamento?.cobranca?.id ? lancamento.cobranca.id : '-' }}</td>
            <td>{{ lancamento?.n_parcelas > 1 ? lancamento.parcela+'/'+lancamento.n_parcelas : lancamento?.n_parcelas == 1 ? 'única' : '-' }}</td>
            <td class="!text-right"
              :class="{
                'text-red-800': lancamento.cobranca,
                'text-green-800': !lancamento.cobranca,
              }"
            >{{ ptBrCurrencyFormat.format(lancamento.valor) }}</td>
            <td class="!text-right">{{ ptBrCurrencyFormat.format(lancamento.saldo_cliente) }}</td>
          </tr>
        </tbody>
        <tfoot>
          <tr v-if="lancamentos_carregando == 1">
            <td colspan="8">Carregando lançamentos...</td>
          </tr>
          <tr v-if="lancamentos_carregando == 2">
            <td colspan="8">Carregando mais lançamentos...</td>
          </tr>
        </tfoot>
      </table>
      <button
        v-if="lancamentos_next && !lancamentos_carregando"
        @click="handleMaisLancamentosClick"
      >Mais lançamentos</button>
    </section>

  </div>
</template>

<style scoped>
table  {
  @apply my-4
}
th, td {
  @apply border border-solid border-slate-300 text-center
}
button, .button {
  @apply mx-0.5 my-[1px] px-2 py-0.5 rounded-lg bg-sky-700 font-bold text-slate-100
}
button:disabled {
  @apply bg-slate-500
}
.router-link:not(.router-link-active):hover {
  text-shadow: 1px 1px 2px  rgba(3, 132, 196, 0.7)
}
</style>
