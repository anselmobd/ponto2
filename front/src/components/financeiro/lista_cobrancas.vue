<script setup>
import { inputStrDate2PtBrDate } from "/src/utils/date.js";
import { ptBrCurrencyFormat } from "/src/utils/numStr.js";

defineProps({
  cobrancas_error: Object,
  cobrancas_carregando: Object,
  cobrancas: Object,
});

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
