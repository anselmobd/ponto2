<script setup>

import { ref, onMounted, onUnmounted, watch } from 'vue';
import { useRoute } from "vue-router";
import { useFinanceiroVueStore } from '../../stores/financeiro.js';
import { inputStrDate2PtBrDate } from "../../utils/date.js";
import { ptBrCurrencyFormat } from "../../utils/numStr.js";
import { getLancamentos } from '../../api/lancamento.js';

const route = useRoute();

const financeiroVueStore = useFinanceiroVueStore();
// Cria Id de componente com nome e parâmetros (props), se houverem
const financeiroVueStoreComponentId = ref(
  financeiroVueStore.montaComponenteId(
    'financeiro/lista_lancamentos.vue', {}))

const lancamentos = ref([])
const nenhum_lancamento = ref('')
const lancamentos_carregando = ref(0)
// 0: carregado
// 1: carregando quantidade padrão
// 2: carregando mais quantidade padrão
// 3: carregando até último em aberto
const lancamentos_error = ref(null)
const tem_next_page = ref(null)
const lancamentos_ultima_data = ref(null)
const lancamentos_ultimo_id = ref(null)

function setNenhumLancamento(tipo_carregamento) {
  if (tipo_carregamento == 3) {
    nenhum_lancamento.value = 'Nenhum lançamento em aberto encontrado';
  } else {
    nenhum_lancamento.value = 'Nenhum lançamento encontrado';
  }
}

function cbGetLancamentos(data, error) {
  console.log('lista_lancementos cbGetLancamentos')
  if (data?.results) {
    console.log('lista_lancementos cbGetLancamentos', data.results)
    if ([1, 3].includes(lancamentos_carregando.value)) {
      lancamentos.value = data.results;
    } else if (lancamentos_carregando.value == 2) {
      lancamentos.value = lancamentos.value.concat(data.results);
    }
    if (lancamentos_carregando.value == 3) {
      // se "carregando até último em aberto" não sabemos se tem próxima
      // página, então assume que tem
      tem_next_page.value = 2;
    } else {
      tem_next_page.value = data.next;
    }
    if (data.results.length) {
      const ultimoLancamento = data.results[data.results.length - 1];
      lancamentos_ultima_data.value = ultimoLancamento.data;
      lancamentos_ultimo_id.value = ultimoLancamento.id;
    }
  }
  if (error) {
    lancamentos_error.value = error;
  };
  lancamentos_carregando.value = 0;
}

function doGetLancamentos(carregando) {
  console.log('lista_lancementos doGetLancamentos')
  setNenhumLancamento(carregando);
  lancamentos_carregando.value = carregando;
  if ([1, 3].includes(lancamentos_carregando.value)) {
    lancamentos.value = [];
    lancamentos_ultima_data.value = null;
    lancamentos_ultimo_id.value = null;
  }
  let page_size = null;
  let ate_ultimo_aberto = null;
  if (lancamentos_carregando.value == 3) {
    page_size = 999999;
    ate_ultimo_aberto = 's';
  }
  lancamentos_error.value = null;
  getLancamentos({
    page_size: page_size,
    cliente_apelido: route.params.apelido,
    ultima_data: lancamentos_ultima_data.value,
    ultimo_id: lancamentos_ultimo_id.value,
    ate_ultimo_aberto: ate_ultimo_aberto,
    callBack: cbGetLancamentos
  });
}

function handleRecarregaLancamentosClick(event) {
  event.preventDefault();
  doGetLancamentos(1);
}

function handleMaisLancamentosClick(event) {
  event.preventDefault();
  doGetLancamentos(2);
}

function handleLancamentosEmAbertoClick(event) {
  event.preventDefault();
  doGetLancamentos(3);
}

// registra este componente para receber eventos via financeiroVueStore

onMounted(() => {
  financeiroVueStore.registrarComponente(financeiroVueStoreComponentId.value)
});

onUnmounted(() => {
  financeiroVueStore.removerRegistroComponente(financeiroVueStoreComponentId.value)
});

watch(
  () => [
    financeiroVueStore.precisaRecarregar,
    financeiroVueStore.precisaRecarregarLancamento
  ],
  ([novoValorPrecisaRecarregar, novoValorPrecisaRecarregarLancamento]) => {
    if (novoValorPrecisaRecarregar || novoValorPrecisaRecarregarLancamento) {
      console.log('Recarregar necessário', {
        precisaRecarregar: novoValorPrecisaRecarregar,
        precisaRecarregarLancamento: novoValorPrecisaRecarregarLancamento
      });
      doGetLancamentos(1);
      financeiroVueStore.componenteConcluiuRecarregar(
        financeiroVueStoreComponentId.value);
    }
  }
);

</script>

<template>

<table class="w-full">
  <thead>
    <tr>
      <th>Nº</th>
      <th>Data</th>
      <th>Informação</th>
      <th>Comunicação</th>
      <th>NF</th>
      <th>Cobrança</th>
      <th>Parcela</th>
      <th>Valor</th>
      <th>Status</th>
      <th>Saldo</th>
    </tr>
    <tr v-if="lancamentos_error">
      <th class="text-red-800" colspan="8">
        {{ lancamentos_error }}
      </th>
    </tr>
    <tr v-if="!lancamentos_carregando && (lancamentos.length == 0)">
      <th colspan="10">{{ nenhum_lancamento }}</th>
    </tr>
  </thead>
  <tbody v-if="lancamentos.length != 0">
    <tr
      v-for="lancamento in lancamentos"
      :key="lancamento.id"
    >
      <td>{{ lancamento.id }}</td>
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
      <td
        :class="{
          'text-orange-500':
            ( ( lancamento.cobranca &&
                ( lancamento.valor_total_recebido > 0 ) &&
                ( lancamento.valor_total_recebido < -lancamento.valor )
              ) ||
              ( !lancamento.cobranca &&
                ( lancamento.valor_total_pago > 0 ) &&
                ( lancamento.valor_total_pago < lancamento.valor )
              )
            ),
          'text-red-800':
            ( lancamento.cobranca && 
              ( lancamento.valor_total_recebido == 0 )
            ) ||
            ( !lancamento.cobranca &&
              ( lancamento.valor_total_pago == 0 )
            ),
          'text-green-800':
            ( ( lancamento.cobranca && 
                ( lancamento.valor_total_recebido == 
                  -lancamento.valor
                )
              ) ||
              ( !lancamento.cobranca &&
                ( lancamento.valor_total_pago == 
                  lancamento.valor
                )
              )
            ),
        }"
      >
      <!-- rec {{ lancamento.valor_total_recebido }}|
      pag {{ lancamento.valor_total_pago }}|
      val {{ lancamento.valor }}|
      val+rec {{ lancamento.valor + lancamento.valor_total_recebido }}|
      val-pag {{ lancamento.valor - lancamento.valor_total_pago }}|
      rec_0{{( lancamento.valor_total_recebido == 0 )}}
      rec_full{{( lancamento.valor_total_recebido == -lancamento.valor )}}
      rec_parc{{( ( lancamento.valor_total_recebido > 0 ) &&
                ( lancamento.valor_total_recebido < -lancamento.valor ) )}} -->
      {{ lancamento.cobranca ?
        ( lancamento.valor_total_recebido != 0 ? (
            lancamento.valor_total_recebido - lancamento.cobranca?.valor == 0
            ? 'Recebido'
            : 'Parcial'
          ) : 'Aberto'
        ) :
        ( lancamento.valor_total_pago != 0 ? (
            lancamento.valor_total_pago - lancamento.valor == 0
            ? 'Conciliado'
            : 'Parcial'
          ) : 'Aberto'
        )
      }}</td>
      <td class="!text-right">{{ ptBrCurrencyFormat.format(lancamento.saldo_cliente) }}</td>
    </tr>
  </tbody>
  <tfoot>
    <tr v-if="lancamentos_carregando == 1">
      <td colspan="10">Carregando lançamentos...</td>
    </tr>
    <tr v-if="lancamentos_carregando == 2">
      <td colspan="10">Carregando mais lançamentos...</td>
    </tr>
    <tr v-if="lancamentos_carregando == 3">
      <td colspan="10">Carregando lançamentos até último em aberto...</td>
    </tr>
  </tfoot>
</table>

<button
  v-if="!lancamentos_carregando"
  @click="handleMaisLancamentosClick"
  :disabled="tem_next_page == null"
>Mais lançamentos</button>
<button
  v-if="!lancamentos_carregando"
  @click="handleLancamentosEmAbertoClick"
>Até último em aberto</button>
<button
  v-if="!lancamentos_carregando"
  @click="handleRecarregaLancamentosClick"
>Recarrega</button>

</template>

<style scoped>
table  {
  @apply my-4
}
th, td {
  @apply border border-solid border-slate-300 text-center
}
tr:hover td {
  @apply bg-slate-200
}
button {
  @apply mx-0.5 my-[1px] px-2 py-0.5 rounded-lg bg-sky-700 font-bold text-slate-100
}
button:disabled {
  @apply bg-slate-500
}
</style>
