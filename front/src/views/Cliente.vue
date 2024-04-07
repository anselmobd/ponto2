<script setup>
import router from '@/router'
import { useRoute } from "vue-router";
import { ref, onMounted } from 'vue'
import { getCliente, putCliente } from '../api/cliente.js';

const route = useRoute();

// valores recebidos de DB e seus controles de visualização

const cliente = ref({})
const cliente_carregando = ref(null)
const cliente_error = ref(null)

// DB API calls (do) and callbacks (cb)

function cbdoGetCliente(data, error) {
  if (data) {
    cliente.value = data;
  }
  if (error) {
    cliente_error.value = error;
  };
  cliente_carregando.value = false;
}

function doGetCliente(callBack) {
  cliente.value = [];
  cliente_carregando.value = true;
  cliente_error.value = null;
  getCliente({
    id: route.params.id,
    callBack: cbdoGetCliente
  });
}

function cbSaveCliente(data, error) {
  if (data) {
    cliente.value = data;
  }
  if (error) {
    lancamento.value.error = error.response.data.human.join('|');
    lancamento.value.error_tech = error.response.data.tech.join('|');
  };
}

function doSaveCliente(callBack) {
  putCliente({
    id: route.params.id,
    payload: cliente.value,
    callBack: cbSaveCliente
  });
}

// Lifecycle Hooks

onMounted(() => {
  doGetCliente();
})

</script>

<template>
  <div>
    <span v-if="cliente_carregando">Carregando dados do cliente {{ route.params.id }}</span>
    <span v-if="cliente_error" class="text-red-800">{{ cliente_error }}</span>
    <section id="titulo" class="flex pt-4 place-content-between">
      <h2 class="inline font-bold text-xl">Dados do cliente <span v-if="cliente?.apelido" class="text-indigo-700">{{ cliente?.apelido }}</span></h2>
      <a title="Voltar" class="button text-xl cursor-pointer" @click.prevent="router.go(-1)">&#x2190;</a>
    </section>
    <p v-if="cliente?.id">cliente={{ cliente }}</p>
    <form @submit.prevent="doSaveCliente()">
      <p class="my-4">
        <label for="apelido">Apelido:</label>
        <input
          class="mx-0.5 border border-solid border-slate-500 rounded"
          v-model="cliente.apelido"
          type="text"
          name="apelido"
          id="apelido"
          required
        >
      </p>
      <button
        class="px-2 py-1 rounded-xl bg-sky-700 font-bold text-slate-100"
        type="submit"
      >Salvar</button>
    </form>
  </div>
</template>
