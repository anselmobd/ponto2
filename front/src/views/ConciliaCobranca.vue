<script setup>
import { useRoute } from "vue-router";
import { ref } from 'vue'

const route = useRoute();

// valores recebidos de DB e seus controles de visualização

const pagamentos = ref([{id:1}])

</script>

<template>
  <div>
    <section id="titulo" class="flex pt-4 place-content-between">
      <h2 class="inline font-bold text-xl">Concilia cobrança do cliente <span class="text-indigo-700">{{ route.params.apelido }}</span></h2>
      <a title="Voltar" class="button text-xl cursor-pointer" @click.prevent="router.go(-1)">&#x2190;</a>
    </section>
    
    <section id="lista_pedidos">
      <h3 class="my-4 font-bold text-lg text-center">Não conciliados</h3>
      <p>Ordem crescente de data</p>

      <table class="w-full">
        <thead>
          <tr>
            <th>id</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="pagamento in pagamentos"
            :key="pagamento.id"
          >
            <td>
              {{pagamento.id}}
            </td>
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
