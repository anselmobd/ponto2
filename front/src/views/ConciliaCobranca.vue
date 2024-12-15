<script setup>
import router from '@/router'
import { useRoute } from "vue-router";
import { ref, onMounted, watch } from 'vue'
import { getLancamentos } from '../api/lancamento.js';
import { addPagamentoCobranca } from '../api/pagamento_cobranca.js';
import { inputStrDate2PtBrDate } from "../utils/date.js";
import { ptBrCurrencyFormat } from "../utils/numStr.js";

const route = useRoute();

// valores recebidos de DB e seus controles de visualização

const pagamentos = ref([])
const pagamentos_carregando = ref(null)
const pagamentos_error = ref(null)

const cobrancas = ref([])
const cobrancas_carregando = ref(null)
const cobrancas_error = ref(null)

// variaveis comuns

const pagamento_selecionado = ref({})
const pagamento_valores_para_soma = ref({})
const pagamento_soma_auxiliar = ref(0)
const cobranca_selecionada = ref({})
const valor_conciliacao = ref(0)
const conciliando = ref({})

// DB API calls (do) and callbacks (cb)

function cbGetPagamentos(data, error) {
  if (data) {
    if (data?.results) {
      pagamentos.value = data.results
    }
  }
  if (error) {
    pagamentos_error.value = error;
  }
  pagamentos_carregando.value = false;
}

function doGetPagamentos() {
  pagamento_valores_para_soma.value = {};
  pagamentos_carregando.value = true;
  pagamentos_error.value = null;
  getLancamentos({
    page_size: 999999,
    cliente_apelido: route.params.apelido,
    tipo_lancamento: 'pagamento',
    conciliada: 'nao',
    callBack: cbGetPagamentos
  });
}

function cbGetCobrancas(data, error) {
  if (data) {
    if (data?.results) {
      cobrancas.value = data.results
    }
  }
  if (error) {
    cobrancas_error.value = error;
  }
  cobrancas_carregando.value = false;
}

function doGetCobrancas() {
  cobrancas_carregando.value = true;
  cobrancas_error.value = null;
  getLancamentos({
    page_size: 999999,
    cliente_apelido: route.params.apelido,
    tipo_lancamento: 'cobranca',
    conciliada: 'nao',
    callBack: cbGetCobrancas
  });
}

function cbAddConciliacao(data, error) {
  if (data) {
    limpaConciliando();
    doGetAll();
  }
  if (error) {
    conciliando.value.error = 'Erro ao adicionar conciliação';
    conciliando.value.error_tech = error.message;
  };
}

function doAddConciliacao() {
  limpaConciliandoError();
  const payload= {
    "pagamento": pagamento_selecionado.value.id,
    "cobranca": cobranca_selecionada.value.id,
    "valor": valor_conciliacao.value,
  }
  addPagamentoCobranca({
    payload: payload,
    callBack: cbAddConciliacao
  });
}

// Events

function handlePagamentoCtrlClick(pagamento) {
  if (pagamento.id in pagamento_valores_para_soma.value) {
    delete pagamento_valores_para_soma.value[pagamento.id];
  } else {
    pagamento_valores_para_soma.value[pagamento.id] = (
      pagamento.valor - pagamento.valor_total_pago
    );
  }
}

function handlePagamentoClick(pagamento, event) {
  console.log(event);
  if (event.ctrlKey) {
    return
  }
  cobranca_selecionada.value = {}
  if (pagamento_selecionado.value?.id === pagamento.id) {
    limpaConciliando();
    return;
  };
  pagamento_selecionado.value = pagamento;

  // Filtra os registros com o valor desejado
  const cobrancasValor = cobrancas.value.filter(
    row => (
      -Number(row.valor) -
      Number(row.valor_total_recebido)
    ) == (
      Number(pagamento_selecionado.value.valor) -
      Number(pagamento_selecionado.value.valor_total_pago)
    )
  );
  console.log(cobrancasValor);

  // Obtém o último registro filtrado com valor desejado
  if (cobrancasValor.length > 0) {
    cobranca_selecionada.value = cobrancasValor[cobrancasValor.length-1];
    setValorConciliacao();
    scrollToRow('cobranca_' + cobranca_selecionada.value.id)
    return
  }

}

function handleCobrancaClick(cobranca) {
  console.log('handleCobrancaClick')
  console.log(pagamento_selecionado.value)
  if (Object.keys(pagamento_selecionado.value).length != 0) {
    console.log(cobranca)
    if (cobranca_selecionada.value?.id === cobranca.id) {
      cobranca_selecionada.value = {};
      valor_conciliacao.value = null;
      return;
    };
    cobranca_selecionada.value = cobranca;
    setValorConciliacao();
  }
}

function handleVoltarClick(event) {
  router.push({
    name: 'financeiro',
    params: { apelido: route.params.apelido }
  });
}

function handleConciliaClick(event) {
  event.preventDefault();
  doAddConciliacao();
}

// Utilitarios

function setValorConciliacao() {
  valor_conciliacao.value = Math.min(
    pagamento_selecionado.value?.valor
    - pagamento_selecionado.value?.valor_total_pago
  , - cobranca_selecionada.value?.valor
    - cobranca_selecionada.value?.valor_total_recebido
  );
}

function scrollToRow(rowId) {
  const row = document.getElementById(rowId);
  if (row) {
    row.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
}

function limpaConciliandoSelecoes() {
  pagamento_selecionado.value = {};
  cobranca_selecionada.value = {};
}

function limpaConciliandoError() {
  conciliando.value = {};
}

function limpaConciliando() {
  limpaConciliandoSelecoes();
  limpaConciliandoError();
  valor_conciliacao.value = null;
}

function doGetAll() {
  limpaConciliando()
  doGetPagamentos();
  doGetCobrancas();
}

// Watcher

watch(pagamento_valores_para_soma, (newValue, oldValue) => {
  pagamento_soma_auxiliar.value = Object.values(newValue).reduce(
    (total, valor) => total + valor, 0);
}, { deep: true });

// Lifecycle Hooks

onMounted(() => {
  doGetAll();
})

</script>

<template>
  <div>
    <section id="titulo" class="flex pt-4 place-content-between">
      <h2 class="inline font-bold text-xl">Conciliação de cobrança do cliente <span class="text-indigo-700">{{ route.params.apelido }}</span></h2>
      <a title="Voltar" class="button text-xl cursor-pointer"
        @click.prevent="handleVoltarClick"
      >&#x2190;</a>
    </section>
    
    <section id="lancamentos">
      <h3 class="my-1 font-bold text-lg text-center bg-slate-100 rounded">Não conciliados</h3>
      <p class="text-center">Clique em um pagamento e em uma cobrança para concilia-los.<br>Control-clique para somar valores em aberto.
      </p>

      <section class="flex justify-between" id="lista_lancamentos">

        <section id="lista_pagamentos">
          <h3 class="my-1 font-bold text-lg text-center">Pagamentos</h3>

          <section id="tabela_pagamentos"
            class="flex-1 ml-2 max-h-[calc(25*1.25rem)] overflow-y-auto border border-gray-300 pl-1 pr-4 text-right">
            <table>
              <thead>
                <tr>
                  <th class="sticky top-0 bg-slate-100">Lançamento</th>
                  <th class="sticky top-0 bg-slate-100">Data</th>
                  <th class="sticky top-0 bg-slate-100">Informação</th>
                  <th class="sticky top-0 bg-slate-100 !text-right">Valor</th>
                  <th class="sticky top-0 bg-slate-100 !text-right">Em aberto</th>
                </tr>
                <tr v-if="pagamentos_error">
                  <th class="text-red-800" colspan="5">
                    {{ pagamentos_error }}
                  </th>
                </tr>
                <tr v-if="pagamentos_carregando">
                  <th colspan="5">Carregando...</th>
                </tr>
                <tr v-if="!pagamentos_carregando && (pagamentos.length == 0)">
                  <th colspan="5">Nenhum encontrado</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="pagamento in pagamentos"
                  :key="pagamento.id"
                  :class="{'bg-yellow-300': pagamento.id == pagamento_selecionado.id}"
                  @click="handlePagamentoClick(pagamento, $event)"
                >
                  <td>{{pagamento.id}}</td>
                  <td>{{inputStrDate2PtBrDate(pagamento.data)}}</td>
                  <td>{{pagamento.informacao}}</td>
                  <td class="!text-right">{{
                    ptBrCurrencyFormat.format(pagamento.valor)
                  }}</td>
                  <td class="!text-right"
                    @click.ctrl="handlePagamentoCtrlClick(pagamento)"
                    :class="{'font-bold':
                      pagamento.id in pagamento_valores_para_soma}"
                  >{{
                    ptBrCurrencyFormat.format(
                      pagamento.valor - pagamento.valor_total_pago)
                  }}</td>
                </tr>
              </tbody>
            </table>
            <p
              class="font-bold"
              v-if="pagamento_soma_auxiliar"
              @click.ctrl="pagamento_valores_para_soma = {}"
            >Soma auxiliar = {{ ptBrCurrencyFormat.format(
              pagamento_soma_auxiliar) }}</p>
          </section>
        </section>

        <section id="lista_cobrancas">
          <h3 class="my-1 font-bold text-lg text-center">Cobranças</h3>

          <section id="tabela_cobrancas"
            class="flex-1 ml-2 max-h-[calc(25*1.25rem)] overflow-y-auto border border-gray-300 pl-1 pr-4 text-right">
            <table>
              <thead>
                <tr>
                  <th class="sticky top-0 bg-slate-100">Lançamento</th>
                  <th class="sticky top-0 bg-slate-100">Data</th>
                  <th class="sticky top-0 bg-slate-100">Informação</th>
                  <th class="sticky top-0 bg-slate-100">NF</th>
                  <th class="sticky top-0 bg-slate-100">Cobrança</th>
                  <th class="sticky top-0 bg-slate-100">Parcela</th>
                  <th class="sticky top-0 bg-slate-100 !text-right">Valor</th>
                  <th class="sticky top-0 bg-slate-100 !text-right">Em aberto</th>
                </tr>
                <tr v-if="cobrancas_error">
                  <th class="text-red-800" colspan="8">
                    {{ cobrancas_error }}
                  </th>
                </tr>
                <tr v-if="cobrancas_carregando">
                  <th colspan="8">Carregando...</th>
                </tr>
                <tr v-if="!cobrancas_carregando && (cobrancas.length == 0)">
                  <th colspan="8">Nenhuma encontrada</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="cobranca in cobrancas"
                  :key="cobranca.id"
                  :class="{'bg-yellow-300': cobranca.id == cobranca_selecionada.id}"
                  :id="'cobranca_' + cobranca.id"
                  @click="handleCobrancaClick(cobranca)"
                >
                  <td>{{ cobranca.id }}</td>
                  <td>{{inputStrDate2PtBrDate(cobranca.data)}}</td>
                  <td>{{cobranca.cobranca.informacao }}</td>
                  <td>{{
                    cobranca?.cobranca?.nf ? cobranca.cobranca.nf : '-'
                  }}</td>
                  <td>{{
                    cobranca?.cobranca?.id ? cobranca.cobranca.id : '-'
                  }}</td>
                  <td>{{
                    cobranca?.n_parcelas > 1 ? cobranca.parcela+'/'+cobranca.n_parcelas : cobranca?.n_parcelas == 1 ? 'única' : '-'
                  }}</td>
                  <td class="!text-right">{{
                    ptBrCurrencyFormat.format(-cobranca.valor)
                  }}</td>
                  <td class="!text-right">{{
                    ptBrCurrencyFormat.format(-cobranca.valor - cobranca.valor_total_recebido)
                  }}</td>
                </tr>
              </tbody>
            </table>
          </section>
        </section>

      </section>

    </section>

    <section 
      id="conciliando"
      v-if="Object.keys(pagamento_selecionado).length > 0"
    >
      <h3 class="my-1 font-bold text-lg text-center bg-slate-100 rounded">Conciliação</h3>
    
      <section class="flex justify-between" id="tabelas_conciliando">
        
        <section id="conciliando_pagamento">
          <h3 class="my-1 font-bold text-lg text-center">Pagamento</h3>
          <table>
            <thead>
              <tr>
                <th class="sticky top-0 bg-slate-100">Lançamento</th>
                <th class="sticky top-0 bg-slate-100">Data</th>
                <th class="sticky top-0 bg-slate-100">Informação</th>
                <th class="sticky top-0 bg-slate-100 !text-right">Valor</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>{{pagamento_selecionado.id}}</td>
                <td>{{inputStrDate2PtBrDate(pagamento_selecionado.data)}}</td>
                <td>{{pagamento_selecionado.informacao}}</td>
                <td class="!text-right">{{
                  ptBrCurrencyFormat.format(pagamento_selecionado.valor)
                }}</td>
              </tr>
            </tbody>
          </table>
        </section>
        
        <section id="conciliando_botoes" class="text-center border-x-8 border-white">
          <h3 class="my-1 font-bold text-lg text-center">Valor</h3>
          <p>&nbsp;</p>
          <p class="text-2xl">{{ valor_conciliacao ? ptBrCurrencyFormat.format(valor_conciliacao) : '-' }}</p>
          <button
            type="button"
            @click="handleConciliaClick"
            :disabled="!Object.keys(cobranca_selecionada).length"
            >Conciliar</button>
          <p
            v-if="conciliando.error"
            class="text-red-800"
            :title="conciliando.error_tech"
          >
            {{ conciliando.error }}
          </p>
        </section>

        <section id="conciliando_cobrancas">
          <h3 class="my-1 font-bold text-lg text-center">Cobrança</h3>
          <table>
            <thead>
              <tr>
                <th class="sticky top-0 bg-slate-100">Lançamento</th>
                <th class="sticky top-0 bg-slate-100">Data</th>
                <th class="sticky top-0 bg-slate-100">Informação</th>
                <th class="sticky top-0 bg-slate-100">NF</th>
                <th class="sticky top-0 bg-slate-100">Cobrança</th>
                <th class="sticky top-0 bg-slate-100">Parcela</th>
                <th class="sticky top-0 bg-slate-100 !text-right">Valor</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>{{ cobranca_selecionada.id }}</td>
                <td>{{inputStrDate2PtBrDate(cobranca_selecionada.data)}}</td>
                <td>{{cobranca_selecionada?.cobranca?.informacao }}</td>
                <td>{{
                  cobranca_selecionada?.cobranca?.nf ? cobranca_selecionada.cobranca.nf : '-'
                }}</td>
                <td>{{
                  cobranca_selecionada?.cobranca?.id ? cobranca_selecionada.cobranca.id : '-'
                }}</td>
                <td>{{
                  cobranca_selecionada?.n_parcelas > 1 ? cobranca_selecionada.parcela+'/'+cobranca_selecionada.n_parcelas : cobranca_selecionada?.n_parcelas == 1 ? 'única' : '-'
                }}</td>
                <td class="!text-right">{{ cobranca_selecionada.valor ?
                  ptBrCurrencyFormat.format(-cobranca_selecionada.valor) : '-'
                }}</td>
              </tr>
            </tbody>
          </table>
        </section>

      </section>

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
