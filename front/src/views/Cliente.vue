<script setup>
import router from '@/router'
import { useRoute } from "vue-router";
import { ref, onMounted } from 'vue'
import { getCliente, putCliente } from '../api/cliente.js';
import { getTiposComunicacao } from '../api/tipo_comunicacao.js';
import { getFormaPagamento } from '../api/forma_pagamento.js';
import { buscarPorCep } from '../webapi/cep.js';
import contato from '../components/cliente/contato.vue';

const route = useRoute();

// valores recebidos de DB e seus controles de visualização

const cliente = ref({})
const cliente_carregando = ref(null)
const cliente_error = ref(null)
const cliente_salvo = ref(null)
const field_error = ref(null)

const tipo_comunicacao = ref([])
const tipo_comunicacao_error = ref(null)

const forma_pagamento = ref([])
const forma_pagamento_error = ref(null)

// Funções auxiliares

function limpaMensagensCliente() {
  cliente_error.value = null;
  cliente_salvo.value = null;
  field_error.value = null;
}

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
  limpaMensagensCliente();
  getCliente({
    id: route.params.id,
    callBack: cbdoGetCliente
  });
}

function cbSaveCliente(data, error) {
  if (data) {
    cliente.value = data;
    cliente_salvo.value = "As alterações nos dados do cliente foram salvas.";
  }
  if (error) {
    cliente_error.value = "As alterações nos dados do cliente não foram salvas. Por favor, corrija os problemas indicados abaixo.";
    field_error.value = error.response.data;
  };
}

function doSaveCliente() {
  limpaMensagensCliente();
  putCliente({
    id: route.params.id,
    payload: cliente.value,
    callBack: cbSaveCliente
  });
}

function cbBuscarPorCep(data) {
  if (data) {
    cliente.value.dados_cep = data;
    cliente.value.bairro = data.bairro;
    cliente.value.cidade = data.localidade;
    cliente.value.uf = data.uf;
    cliente.value.logradouro = data.logradouro;
    cliente.value.numero = data?.numero ? data.numero : '';
    cliente.value.complemento = data.complemento;
    cliente.value.cep = data.cep;
  }
}

function doBuscarPorCep() {
  if (cliente.value.cep.length === 8 && !cliente.value.cep.includes("-")) {
    buscarPorCep({
      cep: cliente.value.cep,
      callBack: cbBuscarPorCep
    });
  }
}

function cbGetTiposComunicacao(data, error) {
  if (data) {
    tipo_comunicacao.value = data.results;
  }
  if (error) {
    tipo_comunicacao_error.value = "Erro ao buscar possíveis valores para Tipos de comunicação";
  };
}

function doGetTiposComunicacao() {
  tipo_comunicacao_error.value = null;
  getTiposComunicacao({
    callBack: cbGetTiposComunicacao
  });
}

function cbGetFormaPagamento(data, error) {
  if (data) {
    forma_pagamento.value = data.results;
  }
  if (error) {
    forma_pagamento_error.value = "Erro ao buscar possíveis valores para Formas de pagamento";
  };
}

function doGetFormaPagamento() {
  forma_pagamento_error.value = null;
  getFormaPagamento({
    callBack: cbGetFormaPagamento
  });
}

// event functions

function handleSaveClick(event) {
  event.preventDefault();
  doSaveCliente();
}

function handleLimpaClick(event) {
  event.preventDefault();
  doGetCliente();
}

// Lifecycle Hooks

onMounted(() => {
  doGetFormaPagamento();
  doGetTiposComunicacao();
  doGetCliente();
})  

</script>

<template>
  <div>
    <div class="my-4 px-4 bg-white flex items-center justify-center">
      <div class="container max-w-screen-lg mx-auto">
        <div>
          
          <section id="titulo_section" class="flex place-content-between">
            <h2 v-if="cliente_carregando" class="font-semibold text-xl text-gray-600">Carregando dados do cliente <span class="text-indigo-700">{{ route.params.id }}</span></h2>
            <h2 v-if="!cliente_carregando" class="font-semibold text-xl text-gray-600">Dados do cliente <span v-if="cliente?.apelido" class="text-indigo-700">{{ cliente?.apelido }}</span></h2>

            <a title="Voltar" class="button text-xl cursor-pointer" @click.prevent="router.go(-1)">&#x2190;</a>
          </section>
          <!-- <p v-if="cliente?.id">cliente={{ cliente }}</p> -->

          <div class="bg-slate-100 rounded shadow-lg p-4 mb-6">
            <form>
              <div class="grid grid-cols-1 gap-4">
                <span v-if="tipo_comunicacao_error" class="text-red-800">{{ tipo_comunicacao_error }}</span>
                <span v-if="forma_pagamento_error" class="text-red-800">{{ forma_pagamento_error }}</span>
                <span v-if="cliente_error" class="text-red-800">{{ cliente_error }}</span>
                <span v-if="cliente_salvo" class="text-green-800">{{ cliente_salvo }}</span>

                <section id="nomes_section">
                  <div class="flex gap-4">
                    <div>
                      <label class="block" for="apelido">Apelido</label>
                      <p v-if="field_error?.apelido" class="text-red-800">{{ field_error.apelido }}</p>
                      <input
                      class="h-10 border mt-1 rounded px-4 bg-white"
                      v-model="cliente.apelido"
                      type="text"
                      name="apelido"
                      id="apelido"
                      required
                      >
                    </div>
                  </div>

                  <div class="flex gap-4">
                    <div>
                      <label class="block" for="nome">Nome/Razão Social</label>
                      <p v-if="field_error?.nome" class="text-red-800">{{ field_error.nome }}</p>
                      <input
                      class="h-10 border mt-1 rounded px-4 bg-white"
                      v-model="cliente.nome"
                      v-focus
                      type="text"
                      name="nome"
                      id="nome"
                      required
                      >
                    </div>
                    <div>
                      <label class="block" for="fansasia">Nome Fansasia</label>
                      <p v-if="field_error?.fansasia" class="text-red-800">{{ field_error.fansasia }}</p>
                      <input
                      class="h-10 border mt-1 rounded px-4 bg-white"
                      v-model="cliente.fansasia"
                      type="text"
                      name="fansasia"
                      id="fansasia"
                      required
                      >
                    </div>
                  </div>
                </section>

                <section id="cnpj_section">
                  <p class="font-semibold">
                    CNPJ
                  </p>
                  <div class="flex gap-4">
                    <div>
                      <label class="block" for="cnpj9">Raiz</label>
                      <p v-if="field_error?.cnpj9" class="text-red-800">{{ field_error.cnpj9 }}</p>
                      <input
                        class="h-10 border mt-1 rounded px-1 w-40 bg-white"
                        v-model="cliente.cnpj9"
                        type="text"
                        name="cnpj9"
                        id="cnpj9"
                      />
                    </div>
                    <div>
                      <label class="block" for="cnpj4">Filial</label>
                      <p v-if="field_error?.cnpj4" class="text-red-800">{{ field_error.cnpj4 }}</p>
                      <input
                        class="h-10 border mt-1 rounded px-1 w-20 bg-white"
                        v-model="cliente.cnpj4"
                        type="text"
                        name="cnpj4"
                        id="cnpj4"
                      />
                    </div>
                    <div>
                      <label class="block" for="cnpj2">Dígitos</label>
                      <p v-if="field_error?.cnpj2" class="text-red-800">{{ field_error.cnpj2 }}</p>
                      <input
                        class="h-10 border mt-1 rounded px-1 w-10 bg-white"
                        v-model="cliente.cnpj2"
                        type="text"
                        name="cnpj2"
                        id="cnpj2"
                      />
                    </div>
                  </div>
                </section>

                <section id="endereco_section">
                  <div class="flex gap-4">
                    <div>
                      <label class="block" for="cep">CEP <span class="text-xs">(8 dígitos, busca)</span></label>
                      <p v-if="field_error?.cep" class="text-red-800">{{ field_error.cep }}</p>
                      <input
                        class="h-10 border mt-1 rounded px-1 w-40 bg-white"
                        v-model="cliente.cep"
                        type="text"
                        name="cep"
                        id="cep"
                        @input="doBuscarPorCep()"
                      />
                    </div>
                    <div>
                      <label class="block" for="bairro">Bairro</label>
                      <p v-if="field_error?.bairro" class="text-red-800">{{ field_error.bairro }}</p>
                      <input
                        class="h-10 border mt-1 rounded px-1 bg-white"
                        v-model="cliente.bairro"
                        type="text"
                        name="bairro"
                        id="bairro"
                      />
                    </div>
                    <div>
                      <label class="block" for="cidade">Cidade</label>
                      <p v-if="field_error?.cidade" class="text-red-800">{{ field_error.cidade }}</p>
                      <input
                        class="h-10 border mt-1 rounded px-1 bg-white"
                        v-model="cliente.cidade"
                        type="text"
                        name="cidade"
                        id="cidade"
                      />
                    </div>
                    <div>
                      <label class="block" for="uf">UF</label>
                      <p v-if="field_error?.uf" class="text-red-800">{{ field_error.uf }}</p>
                      <input
                        class="h-10 border mt-1 rounded px-1 w-10 bg-white"
                        v-model="cliente.uf"
                        type="text"
                        name="uf"
                        id="uf"
                      />
                    </div>
                  </div>

                  <div class="flex gap-4">
                    <div>
                      <label class="block" for="logradouro">Logradouro</label>
                      <p v-if="field_error?.logradouro" class="text-red-800">{{ field_error.logradouro }}</p>
                      <input
                        class="h-10 border mt-1 rounded px-1 bg-white"
                        v-model="cliente.logradouro"
                        type="text"
                        name="logradouro"
                        id="logradouro"
                      />
                    </div>
                    <div>
                      <label class="block" for="numero">Número</label>
                      <p v-if="field_error?.numero" class="text-red-800">{{ field_error.numero }}</p>
                      <input
                        class="h-10 border mt-1 rounded px-1 w-20 bg-white"
                        v-model="cliente.numero"
                        type="text"
                        name="numero"
                        id="numero"
                      />
                    </div>
                    <div>
                      <label class="block" for="complemento">Complemento</label>
                      <p v-if="field_error?.complemento" class="text-red-800">{{ field_error.complemento }}</p>
                      <input
                        class="h-10 border mt-1 rounded px-1 bg-white"
                        v-model="cliente.complemento"
                        type="text"
                        name="complemento"
                        id="complemento"
                      />
                    </div>
                  </div>
                </section>

                <section id="padroes">
                  <p class="font-semibold">
                    Padrões
                  </p>
                  <div class="flex gap-4">
                    <div>
                      <label class="block" for="comunicacao">Comunicação</label>
                      <p v-if="field_error?.comunicacao" class="text-red-800">{{ field_error.comunicacao }}</p>
                      <select
                        class="h-10 border mt-1 rounded px-1 bg-white"
                        v-model="cliente.comunicacao"
                        name="comunicacao"
                        id="comunicacao"
                      >
                        <option
                          v-for="tipo_comunic in tipo_comunicacao"
                          :key="tipo_comunic.id"
                          :value="tipo_comunic.id"
                          required
                        >{{ tipo_comunic.descricao }}</option>
                      </select>
                    </div>
                    <div>
                      <label class="block" for="fansasia">Parcelamento</label>
                      <p v-if="field_error?.parcelamento" class="text-red-800">{{ field_error.parcelamento }}</p>
                      <input
                      class="h-10 border mt-1 rounded px-4 bg-white"
                      v-model="cliente.parcelamento"
                      type="text"
                      name="parcelamento"
                      id="parcelamento"
                      required
                      >
                    </div>
                    <div class="flex flex-col items-center justify-center">
                      <label class="block" for="nf">Nota Fiscal por cobrança</label>
                      <p v-if="field_error?.nf" class="text-red-800">{{ field_error.nf }}</p>
                      <input
                        class="h-10 border mt-1 rounded px-1 bg-white"
                        v-model="cliente.nf"
                        type="checkbox"
                        name="nf"
                        id="nf"
                      >
                    </div>
                  </div>
                </section>

                <section id="preferencias">
                  <p class="font-semibold">
                    Preferências
                  </p>
                  <div class="flex gap-4">
                    <div>
                      <label class="block" for="forma_pagamento">Forma de pagamento</label>
                      <p v-if="field_error?.forma_pagamento" class="text-red-800">{{ field_error.comunicacao }}</p>
                      <select
                        class="h-10 border mt-1 rounded px-1 bg-white"
                        v-model="cliente.forma_pagamento"
                        name="forma_pagamento"
                        id="forma_pagamento"
                      >
                        <option
                          v-for="forma in forma_pagamento"
                          :key="forma.id"
                          :value="forma.id"
                          required
                        >{{ forma.nome }}</option>
                      </select>
                    </div>
                    <div class="flex flex-col items-center justify-center">
                      <label class="block" for="forma_pagamento">Financeiro tipo conta corrente</label>
                      <p v-if="field_error?.conta_corrente" class="text-red-800">{{ field_error.conta_corrente }}</p>
                      <input
                        class="h-10 border mt-1 rounded px-1 bg-white"
                        v-model="cliente.conta_corrente"
                        type="checkbox"
                        name="conta_corrente"
                        id="conta_corrente"
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

                <h2 class="font-semibold text-xl text-gray-600">Contatos do cliente</h2>
                <section id="contato">
                  <contato :cliente="cliente" />
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
