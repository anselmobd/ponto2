<script setup>
import { useRoute } from "vue-router";
import { ref, onMounted } from 'vue'
import { getLancamentos } from '../api/lancamento.js';

const route = useRoute();

// valores recebidos de DB e seus controles de visualização

const pagamentos = ref([{id:1}])
const pagamentos_carregando = ref(null)
const pagamentos_error = ref(null)

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

// Lifecycle Hooks

onMounted(() => {
  doGetPagamentos();
})

</script>

<template>
  <div>
    <section id="titulo" class="flex pt-4 place-content-between">
      <h2 class="inline font-bold text-xl">Concilia cobrança do cliente <span class="text-indigo-700">{{ route.params.apelido }}</span></h2>
      <a title="Voltar" class="button text-xl cursor-pointer" @click.prevent="router.go(-1)">&#x2190;</a>
    </section>
    
    <section id="lista_pedidos">
      <h3 class="my-4 font-bold text-lg text-center">Não conciliados</h3>
      <p class="text-sm">Ordem crescente de data</p>

      <h3 class="my-4 font-bold text-lg text-center">Pagamentos</h3>
      <table class="w-full">
        <thead>
          <tr>
            <th>Data</th>
            <th>informação</th>
            <th class="!text-right">Valor</th>
          </tr>
          <tr v-if="pagamentos_error">
            <th class="text-red-800" colspan="8">
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
            <td>{{pagamento.data}}</td>
            <td>{{ pagamento?.cobranca ? pagamento.cobranca.informacao : pagamento.informacao }}</td>
            <td class="!text-right">{{pagamento.valor}}</td>
          </tr>
        </tbody>
      </table>

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
