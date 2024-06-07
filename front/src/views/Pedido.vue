<script setup>
import router from '@/router'
import { ref, watch, nextTick, onMounted } from 'vue'
import { storeToRefs } from 'pinia';
import { dateTime2Text, date2Text, date2InputText } from "../utils/date.js";
import { useAuthStore } from '../stores/auth.js';
import { getPedidoItens, addClienteBordado, delClienteBordado } from '../api/pedidoItem.js';
import { getClientes } from '../api/cliente.js';
import { getBordados } from '../api/bordado.js';
import { getBordadoCodigos } from '../api/bordado_codigo.js';

const auth = useAuthStore();
// const { user } = storeToRefs(auth)

const pedido_itens = ref(null);
const pedido_itens_next = ref(1);
const pedido_itens_loading = ref(false);
const pedido_itens_filtro_apelido = ref(null);
const pedido_itens_filtro_data_pedido = ref(null);
var pedido_itens_index = '';

const status = ref('b'); // browsing inserting filtering
const filtro_data_pedido = ref('');
const data_pedido = ref({
  input: '',
  error: '',
});
const cliente = ref({
  input: '',
  error: '',
  list: []
});
const bordado = ref({
  input: '',
  error: '',
  list: []
});
const codigo = ref({
  input: '',
  error: '',
  list: []
});

// componentes do template que serão referenciados

const inputCliente = ref(null);
const datalistCliente = ref(null);
const inputBordado = ref(null);
const inputCodigo = ref(null);

// get set refs

function clearInputs(set_cliente_apelido = '', set_filtro_data_pedido = '') {
  filtro_data_pedido.value = set_filtro_data_pedido;
  data_pedido.value.input = '';
  cliente.value.input = set_cliente_apelido;
  bordado.value.input = '';
  codigo.value.input = '';
  pedido_itens_index = '';
}

function clearErrors() {
  data_pedido.value.error = '';
  cliente.value.error = '';
  bordado.value.error = '';
  codigo.value.error = '';
}

// DB API calls (do) and callbacks (cb)

function cbGetFirstsPedidoItens(data, error) {
  if (data) {
    if (data?.results) pedido_itens.value = data.results;
    pedido_itens_next.value = data.next;
  }
  pedido_itens_loading.value = false;
}

function doGetFirstsPedidoItens() {
  pedido_itens_next.value = 1;
  doGetPedidoItens(cbGetFirstsPedidoItens)
}

function cbGetMorePedidoItens(data, error) {
  if (data) {
    if (data?.results) pedido_itens.value = pedido_itens.value.concat(data.results);
    pedido_itens_next.value = data.next;
  }
  pedido_itens_loading.value = false;
}

function doGetMorePedidoItens() {
  doGetPedidoItens(cbGetMorePedidoItens)
}

function doGetPedidoItens(callBack) {
  pedido_itens_loading.value = true;
  getPedidoItens({
    page: pedido_itens_next.value,
    cliente_apelido: pedido_itens_filtro_apelido.value,
    data_pedido: pedido_itens_filtro_data_pedido.value,
    callBack: callBack
  });
}

function cbGetClientes(data, error) {
  if (data) cliente.value.list = data;
}

function cbGetBordado(data, error) {
  if (data) bordado.value.list = data;
}

function doGetBordados() {
  bordado.value.list = [];
  if (cliente?.value?.input) {
    getBordados(cliente.value.input, cbGetBordado)
  }
}

function cbGetBordadoCodigo(data, error) {
  if (data) codigo.value.list = data;
}

function doGetBordadoCodigos() {
  codigo.value.list = [];
  if (cliente?.value?.input && bordado?.value?.input) {
    getBordadoCodigos(cliente.value.input, bordado.value.input, cbGetBordadoCodigo)
  }
}

function cbAddClienteBordado(data, error) {
  if (data) {
    pedidoItemParaTela(data);
    clearInputs();
    doGetFirstsPedidoItens();
    status.value = 'b';
  }
  if (error) {
    console.log(error);
    if ('data_pedido' in error) {
      data_pedido.value.error = error.data_pedido.join('|');
    }
    if ('apelido' in error) {
      cliente.value.error = error.apelido.join('|');
    }
    if ('nome' in error) {
      bordado.value.error = error.nome.join('|');
    }
    if ('codigo' in error) {
      codigo.value.error = error.codigo.join('|');
    }
  };
  getClientes(cbGetClientes);
}

function doAddClienteBordado() {
  clearErrors();
  if (cliente?.value?.input) {
    addClienteBordado(
      data_pedido.value.input,
      cliente.value.input,
      bordado.value.input,
      codigo.value.input,
      cbAddClienteBordado
    );
  } else {
    cliente.value.error = 'Campo cliente vazio.';
  }
}

function cbDelClienteBordado(index) {
  if (index != -1) {
    apagaItemNaTela(index);
    doGetFirstsPedidoItens();
  }
}

function doDelClienteBordado(index) {
  delClienteBordado(
    index,
    pedido_itens.value[index].id,
    cbDelClienteBordado
  );
}

// event functions

function handleNovoClick(event) {
  event.preventDefault();
  clearInputs(pedido_itens_filtro_apelido.value);
  data_pedido.value.input = date2InputText(new Date());
  status.value = 'i';
}

function handleCancelaClick(event) {
  event.preventDefault();
  clearInputs();
  clearErrors();
  status.value = 'b';
}

function handleFiltraClick(event) {
  event.preventDefault();
  pedido_itens_filtro_apelido.value = cliente.value.input;
  pedido_itens_filtro_data_pedido.value = filtro_data_pedido.value;
  clearInputs();
  status.value = 'b';
  doGetFirstsPedidoItens();
}

function handleSalvaClick(event) {
  event.preventDefault();
  doAddClienteBordado();
}

function handleFiltroClick(event) {
  event.preventDefault();
  clearInputs(pedido_itens_filtro_apelido.value, pedido_itens_filtro_data_pedido.value);
  status.value = 'f';
}

function handleCancelaFiltroApelidoClick(event) {
  event.preventDefault();
  pedido_itens_filtro_apelido.value = null;
  doGetFirstsPedidoItens();
}

function handleCancelaFiltroDataPedidoClick(event) {
  event.preventDefault();
  pedido_itens_filtro_data_pedido.value = null;
  doGetFirstsPedidoItens();
}

function handleApagarClick(event) {
  event.preventDefault();
  const index = event.target.value;
  const answer = window.confirm('Confirma apagar?')
  if (answer) doDelClienteBordado(index);
}

function handleEditaDadosClienteClick(event) {
  event.preventDefault();
  const id = event.target.value;
  router.push({ name: 'cliente', params: { id: id } });
}

function handleCriaDadosClienteClick(event) {
  event.preventDefault();
  const id = event.target.value;
  router.push({ name: 'cliente', params: { id: id } });
}

function reloadPedidoItens(event) {
  event.preventDefault();
  doGetFirstsPedidoItens();
}

function handleMaisPedidosClick(event) {
  event.preventDefault();
  doGetMorePedidoItens();
}

function handleFechandoClick(event) {
  event.preventDefault();
  const id = event.target.value;
  router.push({ name: 'fechando', params: { id: id } });
}

function handleFinanceiroClick(event) {
  event.preventDefault();
  const apelido = event.target.value;
  router.push({ name: 'financeiro', params: { apelido: apelido } });
}

function checkClienteSingleOption() {
  const inputElement = inputCliente.value;
  const datalistElement = datalistCliente.value;
  console.log(inputElement.list);
  
  const input_value = inputElement.value.toLowerCase();
  console.log(input_value);
  
  const options = datalistElement.getElementsByTagName('option');
  console.log(options);

  const filteredOptions = Array.from(options).filter(option =>
    option.value.toLowerCase().includes(input_value)
  );
  console.log(filteredOptions);

  if (filteredOptions.length === 1) {
    console.log('set', filteredOptions[0].value);
    cliente.value.input = filteredOptions[0].value;
  }
}

// generic functions

function pedidoItemParaTela(pedido_item) {
  if (pedido_itens_index) {
    const index = pedido_itens_index;
    pedido_itens.value[index].pedido.cliente.apelido = cliente.value.input;
    pedido_itens.value[index].bordado.nome = bordado.value.input;
  } else {
    pedido_itens.value.unshift(pedido_item);
  }
  status.value = 'b';
}

function apagaItemNaTela(index) {
  pedido_itens.value.splice(index, 1);
}

function pedidoItemInseridoEmData(pedido_item) {
  const date = new Date(pedido_item.inserido_em)
  return dateTime2Text(date);
}

function pedidoItemData(pedido_item) {
  const data = new Date(pedido_item.data_pedido)
  return date2Text(data);
}

function inputClienteFocus() {
  nextTick(() => {
    inputCliente.value.focus();
  })
}

function inputBordadoFocus() {
  nextTick(() => {
    inputBordado.value.focus();
  })
}

// Lifecycle Hooks

onMounted(() => {
  doGetFirstsPedidoItens();
})

// watch
watch(status, (newStatus) => {
  if (newStatus != 'b') {
    getClientes(cbGetClientes);
    if (newStatus == 'f') {
      inputClienteFocus();
    } else if (newStatus == 'i') {
      if (pedido_itens_filtro_apelido.value) {
        inputBordadoFocus();
      } else {
        inputClienteFocus();
      }
    }
  }
})

</script>

<template>
  <div>
    <h4 class="text-xl text-center font-bold bg-sky-900 text-slate-100">Pedido <a class="cursor-pointer" @click="reloadPedidoItens">&olarr;</a></h4>
    <table class="w-full">
      <thead>
        <tr>
          <th>Pedido</th>
          <th>Data<span v-if="pedido_itens_filtro_data_pedido" ><br/><span class="text-indigo-700">{{ pedido_itens_filtro_data_pedido }}</span><a href="#" class="button" @click="handleCancelaFiltroDataPedidoClick">&cross;</a></span></th>
          <th>Cliente<span v-if="pedido_itens_filtro_apelido" ><br/><span class="text-indigo-700">{{ pedido_itens_filtro_apelido }}</span><a href="#" class="button" @click="handleCancelaFiltroApelidoClick">&cross;</a></span></th>
          <th colspan="2">Bordado</th>
          <th>Ações</th>
          <th title="Usuário e Data/Hora da inserção/alteração">🛈</th>
        </tr>
        <tr class="table__tr-input">
          <th>
            <span class="font-bold" v-if="status == 'i'">Inserindo</span>
            <span class="font-bold" v-if="status == 'f'">Filtrando</span>
          </th>
          <th>
            <span class="text-sm text-red-700 font-bold" v-if="data_pedido.error" >{{ data_pedido.error }}<br /></span>
            <input v-if="status != 'f'"
              class="mx-0.5 border border-solid border-slate-500 disabled:border-slate-200 rounded disabled:text-gray-400"
              v-model.trim="data_pedido.input"
              :disabled="status != 'i'"
              type="date"
              name="data_pedido"
              id="data_pedido"
              ref="inputDataPedido"
            >
            <input v-if="status == 'f'"
              class="w-11/12 mx-0.5 border border-solid border-slate-500 rounded"
              v-model.trim="filtro_data_pedido"
              type="text"
              size="10"
              name="filtro_data_pedido"
              id="filtro_data_pedido"
              ref="inputFiltroDataPedido"
            >
          </th>
          <th>
            <span class="text-sm text-red-700 font-bold" v-if="cliente.error" >{{ cliente.error }}<br /></span>
            <input
              class="w-11/12 mx-0.5 border border-solid border-slate-500 disabled:border-slate-200 rounded"
              v-model.trim="cliente.input"
              :disabled="status == 'b' || (status == 'i' && pedido_itens_filtro_apelido)"
              type="text"
              size="12"
              name="cliente"
              id="cliente"
              ref="inputCliente"
              placeholder="Cliente"
              list="cliente-list"
              @blur="checkClienteSingleOption"
            >
            <datalist id="cliente-list" ref="datalistCliente">
              <option v-for="cliente1 in cliente.list">{{cliente1}}</option>
            </datalist>
          </th>
          <th>
            <span class="text-sm text-red-700 font-bold" v-if="bordado.error" >{{ bordado.error }}<br /></span>
            <input
              class="w-11/12 mx-0.5 border border-solid border-slate-500 disabled:border-slate-200 rounded"
              v-model.trim="bordado.input"
              :disabled="status != 'i'"
              @focus="doGetBordados"
              type="text"
              size="12"
              name="bordado"
              id="bordado"
              ref="inputBordado"
              placeholder="Nome"
              list="bordado-list"
            >
            <datalist id="bordado-list">
              <option v-for="bordado1 in bordado.list">{{bordado1}}</option>
            </datalist>
          </th>
          <th>
            <span class="text-sm text-red-700 font-bold" v-if="codigo.error" >{{ codigo.error }}<br /></span>
            <input
              class="w-11/12 mx-0.5 border border-solid border-slate-500 disabled:border-slate-200 rounded"
              v-model.trim="codigo.input"
              :disabled="status != 'i'"
              @focus="doGetBordadoCodigos"
              type="text"
              size="12"
              name="codigo"
              id="codigo"
              ref="inputCodigo"
              placeholder="Código"
              list="codigo-list"
            >
            <datalist id="codigo-list">
              <option v-for="codigo1 in codigo.list">{{codigo1}}</option>
            </datalist>
          </th>
          <th>
            <button
              type="button"
              @click="handleSalvaClick"
              :hidden="status != 'i'"
            >Salva</button>
            <button
              type="button"
              @click="handleFiltraClick"
              :hidden="status != 'f'"
            >Filtra</button>
            <button
              type="button"
              @click="handleCancelaClick"
              :hidden="status == 'b'"
            >Cancela</button>
            <button
              type="button"
              @click="handleNovoClick"
              :hidden="status != 'b'"
            >Novo</button>
            <button
              type="button"
              @click="handleFiltroClick"
              :hidden="status != 'b'"
            >Filtro</button>
          </th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="pedido_itens_loading">
          <td colspan="7">
            <span v-if="pedido_itens_next == 1 && !pedido_itens">Carregando</span>
            <span v-if="pedido_itens_next == 1 && pedido_itens">Recarregando</span>
            <span v-if="pedido_itens_next == 1"> os pedidos mais recentes...</span>
            <span v-if="pedido_itens_next > 1">Carregando mais pedidos...</span>
          </td>
        </tr>
        <tr
          v-for="(pedido_item, index) in pedido_itens"
          :key="pedido_item.id"
        >
          <td>
            <span
              v-if="!pedido_item.cobrancas.length || status != 'b'"
            >{{pedido_item.id}}</span>
            <router-link
              v-if="pedido_item.cobrancas.length && status == 'b'"
              :to="{ name: 'fechando', params: { id: pedido_item.id } }"
              class="router-link text-sky-800"
              title="Dados do fechamento do pedido"
            >{{pedido_item.id}}</router-link>
          </td>
          <td>{{pedidoItemData(pedido_item)}}</td>
          <td>
            <span
              v-if="!pedido_item.pedido.cliente.vazio && status != 'b'"
            >{{pedido_item.pedido.cliente.apelido}}</span>
            <router-link
              v-if="!pedido_item.pedido.cliente.vazio && status == 'b'"
              :to="{ name: 'cliente', params: { id: pedido_item.pedido.cliente.id } }"
              class="router-link text-sky-800"
              title="Edita dados de cliente"
            >{{pedido_item.pedido.cliente.apelido}}</router-link>
            <button
              v-if="pedido_item.pedido.cliente.vazio"
              class="button-text-shadow"
              :value="pedido_item.pedido.cliente.id"
              @click="handleCriaDadosClienteClick"
              :disabled="status != 'b'"
              title="Cria dados de cliente"
            >{{pedido_item.pedido.cliente.apelido}}</button>
          </td>
          <td>
            <router-link
              v-if="status == 'b'"
              :to="{ name: 'bordado', params: { id: pedido_item.bordado.id } }"
              class="router-link text-sky-800"
              title="Edita dados do bordado"
            >{{pedido_item.bordado.nome}}</router-link>
            <span v-else>{{pedido_item.bordado.nome}}</span>
          </td>
          <td>{{pedido_item.bordado.codigo}}</td>
          <td>
            <button
              v-if="!pedido_item.quantidade"
              class="button-text-shadow"
              :value="index"
              @click="handleApagarClick"
              :disabled="status != 'b'"
              title="Apaga pedido"
            >🗑️</button>
            <button
              v-if="!pedido_item.cobrancas.length"
              class="button-text-shadow"
              :value="pedido_item.id"
              @click="handleFechandoClick"
              :disabled="status != 'b'"
              title="Fecha pedido"
            >🪡</button>
            <button
              class="button-text-shadow"
              :value="pedido_item.pedido.cliente.apelido"
              @click="handleFinanceiroClick"
              :disabled="status != 'b'"
              title="Financeiro"
            >💲</button>
          </td>
          <td :title="pedido_item.usuario.username
            +' - '+pedidoItemInseridoEmData(pedido_item)">🛈</td>
        </tr>
      </tbody>
    </table>
    <button
      v-if="pedido_itens_next"
      @click="handleMaisPedidosClick"
      :disabled="status != 'b'"
    >Mais pedidos</button>
  </div>
</template>

<style scoped>
.table__tr-input th {
  @apply font-normal 
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
.button-text-shadow {
  text-shadow: 0px 0px 0.5px whitesmoke
}
.router-link:not(.router-link-active):hover {
  text-shadow: 1px 1px 2px  rgba(3, 132, 196, 0.7)
}
</style>
