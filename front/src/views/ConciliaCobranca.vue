<script setup>
import { useRoute } from "vue-router";
import { ref, onMounted } from 'vue'
import { getLancamentos } from '../api/lancamento.js';
import { inputStrDate2PtBrDate, date2InputText } from "../utils/date.js";
import { ptBrCurrencyFormat } from "../utils/numStr.js";

const route = useRoute();

// valores recebidos de DB e seus controles de visualização

const pagamentos = ref([])
const pagamentos_carregando = ref(null)
const pagamentos_error = ref(null)

const cobrancas = ref([])
const cobrancas_carregando = ref(null)
const cobrancas_error = ref(null)

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
  pagamentos.value = [];
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
  cobrancas.value = [];
  cobrancas_carregando.value = true;
  cobrancas_error.value = null;
  getLancamentos({
    page_size: 999999,
    cliente_apelido: route.params.apelido,
    tipo_lancamento: 'cobranca',
    callBack: cbGetCobrancas
  });
}

// Lifecycle Hooks

onMounted(() => {
  doGetPagamentos();
  doGetCobrancas();
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

      <section class="flex justify-between" id="lista_lancamentos">

        <section id="lista_pagamentos">

          <h3 class="my-1 font-bold text-lg text-center">Pagamentos</h3>
          <table>
            <thead>
              <tr>
                <th>Data</th>
                <th>Informação</th>
                <th class="!text-right">Valor</th>
              </tr>
              <tr v-if="pagamentos_error">
                <th class="text-red-800" colspan="3">
                  {{ pagamentos_error }}
                </th>
              </tr>
              <tr v-if="pagamentos_carregando">
                <th colspan="3">Carregando dados dos pagamentos...</th>
              </tr>
              <tr v-if="!pagamentos_carregando && (pagamentos.length == 0)">
                <th colspan="3">Nenhum pagamento encontrado</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="pagamento in pagamentos"
                :key="pagamento.id"
              >
                <td>{{inputStrDate2PtBrDate(pagamento.data)}}</td>
                <td>{{pagamento.informacao}}</td>
                <td class="!text-right">{{
                  ptBrCurrencyFormat.format(pagamento.valor)
                }}</td>
              </tr>
            </tbody>
          </table>
        </section>

        <section id="lista_cobrancas">
          <h3 class="my-1 font-bold text-lg text-center">Cobranças</h3>
          <table>
            <thead>
              <tr>
                <th>Data</th>
                <th>Informação</th>
                <th>Comunicação</th>
                <th>NF</th>
                <th>Cobrança</th>
                <th>Parcela</th>
                <th class="!text-right">Valor</th>
              </tr>
              <tr v-if="cobrancas_error">
                <th class="text-red-800" colspan="7">
                  {{ cobrancas_error }}
                </th>
              </tr>
              <tr v-if="cobrancas_carregando">
                <th colspan="7">Carregando dados das cobranças...</th>
              </tr>
              <tr v-if="!cobrancas_carregando && (cobrancas.length == 0)">
                <th colspan="7">Nenhuma cobrança encontrada</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="cobranca in cobrancas"
                :key="cobranca.id"
              >
                <td>{{inputStrDate2PtBrDate(cobranca.data)}}</td>
                <td>{{cobranca.cobranca.informacao }}</td>
                <td>{{
                  cobranca?.cobranca?.comunicacao?.descricao ? cobranca.cobranca.comunicacao.descricao : '-'
                }}</td>
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
