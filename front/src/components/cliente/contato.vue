<script setup>
import { ref, watch, nextTick, onMounted } from 'vue';
import { delContato, postContato, putContato } from '../../api/contato.js';

const status = ref('b'); // browsing inserting editing

const contato = ref({});
const contato_erro = ref({});
const acoes_mensagem = ref('');

const props = defineProps({
  cliente: Object
});

// componentes do template que serão referenciados

const inputNome = ref(null)

// get set refs

function setInputs({
  id=-1,
  cliente=props.cliente.id,
  nome='',
  telefone='',
  email='',
  preferencial=false
}) {
  contato.value = {
    id: id,
    cliente: cliente,
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
}

// generic functions

function apagaContatoNaTela(index) {
  props.cliente.contato_set.splice(index, 1);
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

function setContatoErro(data) {
  for (var prop in data) {
    if (data.hasOwnProperty(prop)) {
        contato_erro.value[prop] = data[prop].join(" & ");
    }
  }
}

function cbSalvaContato(data, error) {
  if (data) {
    if (contato.value.id == -1) {
      props.cliente.contato_set.push(data);
    } else {
      props.cliente.contato_set[contato.value.index] = data;
    }
    status.value = 'b';
  }
  if (error) {
    setContatoErro(error.response.data);
    if (contato.value.id == -1) {
      acoes_mensagem.value = "Erro ao gravar novo contato";
    } else {
      acoes_mensagem.value = "Erro ao gravar alteração de contato";
    }
  };
}

function doSalvaContato() {
  if (contato.value.id == -1) {
    postContato({
      payload: contato.value,
      callBack: cbSalvaContato
    });
  } else {
    putContato({
      payload: contato.value,
      callBack: cbSalvaContato
    });
  }
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
  const answer = window.confirm('Confirma salvar contato?')
  if (answer) {
    doSalvaContato();
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
  setInputs(props.cliente.contato_set[index]);
  contato.value.index = index;
  status.value = 'e';
}

function handleApagaClick(event) {
  event.preventDefault();
  const index = event.target.value;
  const contato_selecionado = props.cliente.contato_set[index];
  const answer = window.confirm('Confirma apagar contato?')
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
  } else {
    clearAll();
  }
})

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
        <tr v-if="acoes_mensagem" class="text-red-800">
          <th colspan="5">{{ acoes_mensagem }}</th>
        </tr>
        <tr>
          <th>
            <span class="text-sm text-red-800 font-bold" v-if="contato_erro.nome" >{{ contato_erro.nome }}<br /></span>
            <input
              class="mx-0.5 border border-solid border-slate-500 disabled:border-slate-200 rounded"
              v-model.trim="contato.nome"
              ref="inputNome"
              type="text"
              size="20"
              name="nome"
              id="nome"
              :disabled="status == 'b'"
            >
          </th>
          <th>
            <span class="text-sm text-red-800 font-bold" v-if="contato_erro.telefone" >{{ contato_erro.telefone }}<br /></span>
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
            <span class="text-sm text-red-800 font-bold" v-if="contato_erro.email" >{{ contato_erro.email }}<br /></span>
            <input
              class="mx-0.5 border border-solid border-slate-500 disabled:border-slate-200 rounded"
              v-model.trim="contato.email"
              type="text"
              size="20"
              name="email"
              id="email"
              :disabled="status == 'b'"
            >
          </th>
          <th>
            <span class="text-sm text-red-800 font-bold" v-if="contato_erro.preferencial" >{{ contato_erro.preferencial }}<br /></span>
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
          v-for="(contato, index) in cliente.contato_set"
          :key="contato.id"
        >
          <td>{{contato.nome}}</td>
          <td>{{contato.telefone}}</td>
          <td>{{contato.email}}</td>
          <td>
            <span v-if="contato.preferencial">✅</span>
            <span v-if="!contato.preferencial">🟩</span>
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
  @apply mx-0.5 my-[1px] px-2 py-0.5 rounded-lg bg-sky-800 font-bold text-slate-100
}
button:disabled {
  @apply bg-slate-500
}
.button-text-shadow {
  text-shadow: 0px 0px 0.5px whitesmoke
}
</style>
