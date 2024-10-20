<script setup>
import { useRoute } from "vue-router";
import { ref, onMounted } from 'vue'
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
const cobrancas_selecionadas = ref({})
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
  // pagamentos.value = [];
  pagamentos_carregando.value = true;
  pagamentos_error.value = null;
  getLancamentos({
    page_size: 999999,
    cliente_apelido: route.params.apelido,
    tipo_lancamento: 'pagamento',
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
  // cobrancas.value = [];
  cobrancas_carregando.value = true;
  cobrancas_error.value = null;
  getLancamentos({
    page_size: 999999,
    cliente_apelido: route.params.apelido,
    tipo_lancamento: 'cobranca',
    callBack: cbGetCobrancas
  });
}

function cbAddConciliacao(data, error) {
  if (data) {
    limpaConciliando();
    doGetAll();
  }
  if (error) {
    // conciliando.value.error = error.response.data.human.join('|');
    // conciliando.value.error_tech = error.response.data.tech.join('|');
    conciliando.value.error = 'Erro ao adicionar conciliação';
    conciliando.value.error_tech = error.message;
  };
}

function doAddConciliacao() {
  limpaConciliandoError();
  // const payload= {
  //   "pagamento": 123,
  //   "cobrancas": [
  //     {
  //       "cobranca": 234,
  //       "valor": 345,
  //     }
  //   ]
  // }
  const primeiro_id_cobranca = Object.keys(cobrancas_selecionadas.value)[0];
  const payload= {
    "pagamento": pagamento_selecionado.value.id,
    "cobranca": cobrancas_selecionadas.value[primeiro_id_cobranca].cobranca.id,
    "valor": -cobrancas_selecionadas.value[primeiro_id_cobranca].valor
  }
  addPagamentoCobranca({
    payload: payload,
    callBack: cbAddConciliacao
  });
  // cbAddConciliacao(null, {
  //   response: {
  //     data: {
  //       human: ['h'],
  //       tech: ['t']
  //     }
  //   }
  // });
}


// Events

function handlePagamentoClick(pagamento) {
  cobrancas_selecionadas.value = {};
  if (pagamento_selecionado.value?.id === pagamento.id) {
    limpaConciliando();
    return;
  };
  pagamento_selecionado.value = pagamento;

  // Filtra os registros com o valor desejado
  const cobrancasValor = cobrancas.value.filter(row => row.valor === '-'+ pagamento_selecionado.value.valor);
  console.log(cobrancasValor);

  // Obtém o último registro filtrado com valor desejado
  if (cobrancasValor.length > 0) {
    const id = cobrancasValor[cobrancasValor.length-1].id;
    cobrancas_selecionadas.value[id] = cobrancasValor[cobrancasValor.length-1];
    scrollToRow('cobranca_' + id)
    return
  }

  // busca últimos registros até somar o valor desejado
  // WIP

}

function handleConciliaClick(event) {
  event.preventDefault();
  doAddConciliacao();
}

// Utilitarios

function scrollToRow(rowId) {
  const row = document.getElementById(rowId);
  if (row) {
    row.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
}

function limpaConciliandoTabelas() {
  pagamento_selecionado.value = {};
  cobrancas_selecionadas.value = {};
}

function limpaConciliandoError() {
  conciliando.value = {};
}

function limpaConciliando() {
  limpaConciliandoTabelas();
  limpaConciliandoError();
}

function doGetAll() {
  limpaConciliando()
  doGetPagamentos();
  doGetCobrancas();
}

// Lifecycle Hooks

onMounted(() => {
  doGetAll();
})

</script>

<template>
  <div>
    <section id="titulo" class="flex pt-4 place-content-between">
      <h2 class="inline font-bold text-xl">Conciliação de cobrança do cliente <span class="text-indigo-700">{{ route.params.apelido }}</span></h2>
      <a title="Voltar" class="button text-xl cursor-pointer" @click.prevent="router.go(-1)">&#x2190;</a>
    </section>
    
    <section id="lancamentos">
      <h3 class="my-1 font-bold text-lg text-center bg-slate-100 rounded">Não conciliados</h3>
      <p class="text-sm">Clique em um pagamento para iniciar a conciliação com as cobranças</p>

      <section class="flex justify-between" id="lista_lancamentos">

        <section id="lista_pagamentos">
          <h3 class="my-1 font-bold text-lg text-center">Pagamentos</h3>

          <section id="tabela_pagamentos"
            class="flex-1 ml-2 max-h-[calc(25*1.25rem)] overflow-y-auto border border-gray-300 pl-1 pr-4 text-right">
            <table>
              <thead>
                <tr>
                  <th class="sticky top-0 bg-slate-100">Nº</th>
                  <th class="sticky top-0 bg-slate-100">Data</th>
                  <th class="sticky top-0 bg-slate-100">Informação</th>
                  <th class="sticky top-0 bg-slate-100 !text-right">Valor</th>
                </tr>
                <tr v-if="pagamentos_error">
                  <th class="text-red-800" colspan="4">
                    {{ pagamentos_error }}
                  </th>
                </tr>
                <tr v-if="pagamentos_carregando">
                  <th colspan="4">Carregando...</th>
                </tr>
                <tr v-if="!pagamentos_carregando && (pagamentos.length == 0)">
                  <th colspan="4">Nenhum encontrado</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="pagamento in pagamentos"
                  :key="pagamento.id"
                  :class="{'bg-yellow-300': pagamento.id == pagamento_selecionado.id}"
                  @click="handlePagamentoClick(pagamento)"
                >
                  <td>{{pagamento.id}}</td>
                  <td>{{inputStrDate2PtBrDate(pagamento.data)}}</td>
                  <td>{{pagamento.informacao}}</td>
                  <td class="!text-right">{{
                    ptBrCurrencyFormat.format(pagamento.valor)
                  }}</td>
                </tr>
              </tbody>
            </table>
          </section>
        </section>

        <section id="lista_cobrancas">
          <h3 class="my-1 font-bold text-lg text-center">Cobranças</h3>

          <section id="tabela_cobrancas"
            class="flex-1 ml-2 max-h-[calc(25*1.25rem)] overflow-y-auto border border-gray-300 pl-1 pr-4 text-right">
            <table>
              <thead>
                <tr>
                  <th class="sticky top-0 bg-slate-100">Data</th>
                  <th class="sticky top-0 bg-slate-100">Informação</th>
                  <th class="sticky top-0 bg-slate-100">NF</th>
                  <th class="sticky top-0 bg-slate-100">Cobrança</th>
                  <th class="sticky top-0 bg-slate-100">Parcela</th>
                  <th class="sticky top-0 bg-slate-100 !text-right">Valor</th>
                </tr>
                <tr v-if="cobrancas_error">
                  <th class="text-red-800" colspan="6">
                    {{ cobrancas_error }}
                  </th>
                </tr>
                <tr v-if="cobrancas_carregando">
                  <th colspan="6">Carregando...</th>
                </tr>
                <tr v-if="!cobrancas_carregando && (cobrancas.length == 0)">
                  <th colspan="6">Nenhuma encontrada</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="cobranca in cobrancas"
                  :key="cobranca.id"
                  :class="{'bg-yellow-300': cobranca.id in cobrancas_selecionadas}"
                  :id="'cobranca_' + cobranca.id"
                >
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
      <h3 class="my-1 font-bold text-lg text-center bg-slate-100 rounded">Conciliando</h3>
    
      <section class="flex justify-between" id="tabelas_conciliando">
        
        <section id="conciliando_pagamento">
          <h3 class="my-1 font-bold text-lg text-center">Pagamento</h3>
          <table>
            <thead>
              <tr>
                <th class="sticky top-0 bg-slate-100">Nº</th>
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

        <section id="conciliando_cobrancas">
          <h3 class="my-1 font-bold text-lg text-center">Cobranças</h3>
          <table>
            <thead>
              <tr>
                <th class="sticky top-0 bg-slate-100">Data</th>
                <th class="sticky top-0 bg-slate-100">Informação</th>
                <th class="sticky top-0 bg-slate-100">NF</th>
                <th class="sticky top-0 bg-slate-100">Cobrança</th>
                <th class="sticky top-0 bg-slate-100">Parcela</th>
                <th class="sticky top-0 bg-slate-100 !text-right">Valor</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="cobranca in Object.values(cobrancas_selecionadas)"
                :key="cobranca.id"
              >
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
              </tr>
            </tbody>
          </table>
        </section>

      </section>

      <section id="conciliando_botoes" class="text-center">
        <button
          type="button"
          @click="handleConciliaClick"
        >Concilia</button>
        <p
          v-if="conciliando.error"
          class="text-red-800"
          :title="conciliando.error_tech"
        >
          {{ conciliando.error }}
        </p>
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
