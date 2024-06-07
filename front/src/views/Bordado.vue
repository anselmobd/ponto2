<script setup>
import router from '@/router'
import { useRoute } from "vue-router";
import { ref, onMounted } from 'vue'
import { getBordadoFull, putBordado } from '../api/bordado.js';

const route = useRoute();

// valores recebidos de DB e seus controles de visualização

const bordado = ref({})
const bordado__full = ref({})
const bordado_carregando = ref(null)
const bordado_error = ref(null)
const bordado_salvo = ref(null)
const field_error = ref(null)

// Funções auxiliares

function limpaMensagensBordado() {
  bordado_error.value = null;
  bordado_salvo.value = null;
  field_error.value = null;
}

// DB API calls (do) and callbacks (cb)

function cbdoGetBordado(data, error) {
  if (data) {
    bordado__full.value = data;
    bordado.value = {
      id: data.id,
      cliente: data.cliente.id,
      nome: data.nome,
      codigo: data.codigo
    }
  }
  if (error) {
    bordado_error.value = error;
  };
  bordado_carregando.value = false;
}

function doGetBordado(callBack) {
  bordado.value = [];
  bordado_carregando.value = true;
  limpaMensagensBordado();
  getBordadoFull({
    id: route.params.id,
    callBack: cbdoGetBordado
  });
}

function cbSaveBordado(data, error) {
  if (data) {
    bordado.value = data;
    bordado_salvo.value = "As alterações nos dados do bordado foram salvas.";
  }
  if (error) {
    console.error(error);
    bordado_error.value = "As alterações nos dados do bordado não foram salvas. Por favor, corrija os problemas indicados abaixo.";
    field_error.value = error.response.data;
  };
}

function doSaveBordado() {
  limpaMensagensBordado();
  putBordado({
    id: route.params.id,
    payload: bordado.value,
    callBack: cbSaveBordado
  });
}

// event functions

function handleSaveClick(event) {
  event.preventDefault();
  doSaveBordado();
}

function handleLimpaClick(event) {
  event.preventDefault();
  doGetBordado();
}

// Lifecycle Hooks

onMounted(() => {
  doGetBordado();
})  

</script>

<template>
  <div>
    <div class="my-4 px-4 bg-white flex items-center justify-center">
      <div class="container max-w-screen-lg mx-auto">
        <div>
          
          <section id="titulo_section" class="flex place-content-between">
            <h2 v-if="bordado_carregando" class="font-semibold text-xl text-gray-600">Carregando dados do bordado <span class="text-indigo-700">{{ route.params.id }}</span></h2>

            <h2 v-if="!bordado_carregando" class="font-semibold text-xl text-gray-600">
              Dados do bordado
              <span v-if="bordado__full?.cliente?.apelido" class="text-indigo-700">{{ bordado__full.cliente.apelido_slug }}</span> -
              <span v-if="bordado__full?.nome" class="text-indigo-700">{{ bordado__full.nome }}</span> -
              <span v-if="bordado__full?.codigo" class="text-indigo-700">{{ bordado__full.codigo }}</span>
            </h2>

            <a title="Voltar" class="button text-xl cursor-pointer" @click.prevent="router.go(-1)">&#x2190;</a>
          </section>
          <!-- <p v-if="bordado?.id">bordado={{ bordado }}</p> -->

          <div class="bg-slate-100 rounded shadow-lg p-4 mb-6">
            <form>
              <div class="grid grid-cols-1 gap-4">
                <span v-if="bordado_error" class="text-red-800">{{ bordado_error }}</span>
                <span v-if="bordado_salvo" class="text-green-800">{{ bordado_salvo }}</span>

                <section id="nomes_section">
                  <div class="flex gap-4">
                    <div>
                      <label class="block" for="fansasia">Nome</label>
                      <p v-if="field_error" class="text-red-800">{{ field_error }}</p>
                      <input
                      class="h-10 border mt-1 rounded px-4 bg-white"
                      v-model="bordado.nome"
                      type="text"
                      name="nome"
                      id="nome"
                      required
                      >
                    </div>
                    <div>
                      <label class="block" for="codigo">Código</label>
                      <p v-if="field_error?.codigo" class="text-red-800">{{ field_error.codigo }}</p>
                      <input
                      class="h-10 border mt-1 rounded px-4 bg-white"
                      v-model="bordado.codigo"
                      type="text"
                      name="codigo"
                      id="codigo"
                      >
                    </div>
                  </div>
                </section>

                <section id="botoes_section" class="inline-flex gap-8 justify-center">
                  <button
                    @click="handleSaveClick"
                    type="submit"
                  >Salvar</button>
                  <button
                    @click="handleLimpaClick"
                    type="reset"
                  >Limpar</button>
                </section>

              </div> <!--div class="grid grid-cols-1 gap-4"-->
            </form>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
th, td {
  @apply border border-solid border-slate-300 text-center
}
button, .button {
  @apply mx-0.5 my-[1px] px-2 py-0.5 rounded-lg bg-sky-700 font-bold text-slate-100
}
</style>
