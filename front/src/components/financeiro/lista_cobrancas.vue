<script setup>
import { useRoute } from "vue-router";
import { useFinanceiroVueStore } from '../../stores/financeiro.js';
import { inputStrDate2PtBrDate } from "../../utils/date.js";
import { ptBrCurrencyFormat } from "../../utils/numStr.js";
import { getCobrancas } from '../../api/cobranca.js';
import { ref, onMounted, onUnmounted, watch } from 'vue';

// defineProps({
//   cobrancas_error: Object,
//   cobrancas_carregando: Boolean,
//   cobrancas: Array,
// });

const route = useRoute();

const financeiroVueStore = useFinanceiroVueStore();
// Cria Id de componente com nome e parâmetros (props), se houverem
const financeiroVueStoreComponentId = ref(
  financeiroVueStore.montaComponenteId(
    'financeiro/lista_cobrancas.vue', {}))

const cobrancas = ref([])
const cobrancas_carregando = ref(null)
const cobrancas_error = ref(null)

// DB API calls (do) and callbacks (cb)
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

async function doGetCobrancas(callBack) {
  cobrancas.value = [];
  cobrancas_carregando.value = true;
  cobrancas_error.value = null;
  await getCobrancas({
    cliente_apelido: route.params.apelido,
    callBack: cbGetCobrancas
  });
}

onMounted(() => {
  financeiroVueStore.registrarComponente(financeiroVueStoreComponentId.value)
});

onUnmounted(() => {
  financeiroVueStore.removerRegistroComponente(financeiroVueStoreComponentId.value)
});

watch(
  () => financeiroVueStore.precisaRecarregar,
  async (novoValor) => {
    if (novoValor) {
      await doGetCobrancas();
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
        <th>Informação</th>
        <th>Tipo</th>
        <th>NF</th>
        <th>Valor</th>
        <th>Pedido</th>
        <th>Data</th>
        <th>Parcelamento</th>
      </tr>
      <tr v-if="cobrancas_error">
        <th colspan="8" class="text-red-800">
          {{ cobrancas_error }}
        </th>
      </tr>
      <tr v-if="cobrancas_carregando">
        <td colspan="8">Carregando dados das cobranças...</td>
      </tr>
      <tr v-if="!cobrancas_carregando && (cobrancas.length == 0)">
        <td colspan="8">Nenhuma cobrança encontrada</td>
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
</style>
