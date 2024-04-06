<script setup>
import router from '@/router'
import { useRoute } from "vue-router";
import { ref, onMounted } from 'vue'
import { getCliente } from '../api/cliente.js';

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

// Lifecycle Hooks

onMounted(() => {
  doGetCliente();
})

</script>

<template>
  <div>
    <span v-if="cliente_carregando">Carregando dados dos pedidos...</span><br>
    <p v-if="cliente?.id">cliente={{ cliente }}</p>
    <span v-if="cliente_error" class="text-red-800">{{ cliente_error }}</span><br>
  </div>
</template>
