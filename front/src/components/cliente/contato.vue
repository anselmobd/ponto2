<script setup>
import { ref } from 'vue'

const contato = ref({
  nome: '',
  telefone: '',
  email: '',
  preferencial: false
});

defineProps({
  contato_set: Array
});

</script>

<template>
  <div>
    <table class="w-full">
      <thead>
        <tr>
          <th>Nome</th>
          <th>Telefone</th>
          <th>E-mail</th>
          <th>Preferencial</th>
          <th>Ações</th>
        </tr>
        <tr>
          <th>
            <input
              class="mx-0.5 border border-solid border-slate-500 disabled:border-slate-200 rounded"
              v-model.trim="contato.nome"
              type="text"
              size="12"
              name="nome"
              id="nome"
            >
          </th>
          <th>
            <input
              class="mx-0.5 border border-solid border-slate-500 disabled:border-slate-200 rounded"
              v-model.trim="contato.telefone"
              type="text"
              size="12"
              name="telefone"
              id="telefone"
            >
          </th>
          <th>
            <input
              class="mx-0.5 border border-solid border-slate-500 disabled:border-slate-200 rounded"
              v-model.trim="contato.email"
              type="text"
              size="12"
              name="email"
              id="email"
            >
          </th>
          <th>
            <input
              type="checkbox"
              v-model="contato.preferencial"
            />
          </th>
          <th>
            ação
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="contato in contato_set"
          :key="contato.id"
        >
          <td>{{contato.nome}}</td>
          <td>{{contato.telefone}}</td>
          <td>{{contato.email}}</td>
          <td>
            <span v-if="contato.preferencial" class="text-green-800">🗹</span>
            <span v-if="!contato.preferencial" class="text-red-800">🗷</span>
          </td>
          <td>-</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
th, td {
  @apply border border-solid border-slate-300 text-center
}
</style>
