<script setup>
import { ref, watch, nextTick, onMounted } from 'vue';
import { delContato } from '../../api/contato.js';

const status = ref('b'); // browsing inserting editing

const contato = ref({});
const contato_erro = ref({});
const acoes_mensagem = ref('');

const props = defineProps({
  contato_set: Array
});

// componentes do template que serão referenciados

const inputNome = ref(null)

// get set refs

function setInputs({
  id=-1,
  nome='',
  telefone='',
  email='',
  preferencial=false
}) {
  contato.value = {
    id: id,
    nome: nome,
    telefone: telefone,
    email: email,
    preferencial: preferencial
  };
}

function clearInputs() {
  setInputs({});
}

function clearErrors() {
  contato_erro.value = {
    nome: '',
    telefone: '',
    email: '',
    preferencial: ''
  }
}

function clearAcoesMensagem() {
  acoes_mensagem.value = '';
}

function clearAll() {
  clearInputs();
  clearErrors();
  clearAcoesMensagem();
}

// generic functions

function apagaContatoNaTela(index) {
  props.contato_set.splice(index, 1);
}

// DB API calls (do) and callbacks (cb)

function cbDelContato(index) {
  if (index == -1) {
    acoes_mensagem.value = "Erro ao tentar apagar contato";
  } else {
    apagaContatoNaTela(index);
  }
}

function doDelContato(index, id) {
  delContato(index, id, cbDelContato);
}

function cbAddLancamento(data, error) {
  if (data) {
    status.value = 'b';
    clearLancamento();
    doGetLancamentos(1);
  }
  if (error) {
    lancamento.value.error = error.response.data.human.join('|');
    lancamento.value.error_tech = error.response.data.tech.join('|');
  };
}

function doAddLancamento(callBack) {
  const payload= {
    "cliente": {
      "apelido": route.params.apelido,
    },
    "data": lancamento.value.data,
    "informacao": lancamento.value.informacao,
    "valor": lancamento.value.valor,
  }
  addLancamento({
    payload: payload,
    callBack: cbAddLancamento
  });
}

function cbAddContato() {

}

function doAddContato() {

}

function inputNomeFocus() {
  nextTick(() => {
    inputNome.value.focus();
  })
}

// event functions

function handleNovoClick(event) {
  event.preventDefault();
  clearAll();
  status.value = 'i';
}

function handleSalvaClick(event) {
  event.preventDefault();
  const answer = window.confirm('Confirma salvar contato "'+contato.value.nome+'"?')
  if (answer) {
    if (contato.value.id == -1) {
      doAddContato();
    }
  }
}

function handleCancelaClick(event) {
  event.preventDefault();
  clearAll();
  status.value = 'b';
}

function handleEditaClick(event) {
  event.preventDefault();
  const index = event.target.value;
  setInputs(props.contato_set[index]);
  status.value = 'e';
}

function handleApagaClick(event) {
  event.preventDefault();
  const index = event.target.value;
  const contato_selecionado = props.contato_set[index];
  const answer = window.confirm('Confirma apagar contato "'+contato_selecionado.nome+'"?')
  if (answer) doDelContato(index, contato_selecionado.id);
}

// Lifecycle Hooks

onMounted(() => {
  clearAll();
})

// watch
watch(status, (newStatus) => {
  clearAcoesMensagem();
  if (newStatus != 'b') {
    inputNomeFocus();
  }
})

</script>

<template>
  <div>
    {{ contato_set }}
    <table class="w-full">
      <thead>
        <tr>
          <th>Nome</th>
          <th>Telefone</th>
          <th>E-mail</th>
          <th>Preferencial</th>
          <th>Ações</th>
        </tr>
        <tr v-if="acoes_mensagem">
          <th colspan="5">{{ acoes_mensagem }}</th>
        </tr>
        <tr>
          <th>
            <span class="text-sm text-red-700 font-bold" v-if="contato_erro.nome" >{{ contato_erro.nome }}<br /></span>
            <input
              class="mx-0.5 border border-solid border-slate-500 disabled:border-slate-200 rounded"
              v-model.trim="contato.nome"
              ref="inputNome"
              type="text"
              size="12"
              name="nome"
              id="nome"
              :disabled="status == 'b'"
            >
          </th>
          <th>
            <span class="text-sm text-red-700 font-bold" v-if="contato_erro.telefone" >{{ contato_erro.telefone }}<br /></span>
            <input
              class="mx-0.5 border border-solid border-slate-500 disabled:border-slate-200 rounded"
              v-model.trim="contato.telefone"
              type="text"
              size="12"
              name="telefone"
              id="telefone"
              :disabled="status == 'b'"
            >
          </th>
          <th>
            <span class="text-sm text-red-700 font-bold" v-if="contato_erro.email" >{{ contato_erro.email }}<br /></span>
            <input
              class="mx-0.5 border border-solid border-slate-500 disabled:border-slate-200 rounded"
              v-model.trim="contato.email"
              type="text"
              size="12"
              name="email"
              id="email"
              :disabled="status == 'b'"
            >
          </th>
          <th>
            <span class="text-sm text-red-700 font-bold" v-if="contato_erro.preferencial" >{{ contato_erro.preferencial }}<br /></span>
            <input
              type="checkbox"
              v-model="contato.preferencial"
              :disabled="status == 'b'"
            />
          </th>
          <th>
            <button
              type="button"
              @click="handleNovoClick"
              :hidden="status != 'b'"
            >Novo</button>
            <button
              type="button"
              @click="handleSalvaClick"
              :hidden="status == 'b'"
            >Salva</button>
            <button
              type="button"
              @click="handleCancelaClick"
              :hidden="status == 'b'"
            >Cancela</button>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(contato, index) in contato_set"
          :key="contato.id"
        >
          <td>{{contato.nome}}</td>
          <td>{{contato.telefone}}</td>
          <td>{{contato.email}}</td>
          <td>
            <span v-if="contato.preferencial" class="text-green-800">🗹</span>
            <span v-if="!contato.preferencial" class="text-red-800">🗷</span>
          </td>
          <td>
            <button
              class="button-text-shadow"
              :value="index"
              @click="handleEditaClick"
              :disabled="status != 'b'"
              title="Edita contato"
            >✏️</button>
            <button
              class="button-text-shadow"
              :value="index"
              @click="handleApagaClick"
              :disabled="status != 'b'"
              title="Apaga contato"
            >🗑️</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
th, td {
  @apply border border-solid border-slate-300 text-center
}
button, .button {
  @apply mx-0.5 my-[1px] px-2 py-0.5 rounded-lg bg-sky-700 font-bold text-slate-100
}
button:disabled {
  @apply bg-slate-500
}
.button-text-shadow {
  text-shadow: 0px 0px 0.5px whitesmoke
}
</style>
