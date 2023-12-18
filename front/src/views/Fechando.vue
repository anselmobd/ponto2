<script setup>
import router from '@/router'
import { useRoute } from "vue-router";
import { ref, onMounted, watch } from 'vue'
import { getPedidoItem, saveFechamento, delFechamento, getPedidoItens } from '../api/pedidoItem.js';
import { dateTime2Text, date2InputText, inputStrDate2PtBrDate } from "../utils/date.js";
import { ptBrCurrencyFormat } from "../utils/numStr.js";
import { floatRound } from "../utils/number.js";

// TODO
// - valores: não permitir valores com fração de centavo

const route = useRoute();

// valores recebidos de DB

const pedido_item = ref('')
const inserido_em = ref(null)
const pedido_itens_bordado = ref([])
const pedido_itens_cliente = ref([])

// variaveis comuns

  // para data de entrega
const dataAtual = new Date();
const doisDiasDepois = new Date(dataAtual.getTime() + (2 * 86400000));
const strDoisDiasDepois = date2InputText(doisDiasDepois);

  // auxiliar para cálculos
var inputValorFinalFocused = false;

// valores em inputs

const data_entrega = ref(strDoisDiasDepois)
const quantidade = ref(0)
const valor_unitario = ref(0)
const programacao = ref(0)
const ajuste = ref(0)

// outros valores reativos

const valor = ref(0)
const valor_final = ref(0)
const alerta = ref('')

// DB API calls (do) and callbacks (cb)

function cbPedidoItem(data, error) {
  if (data) {
    pedido_item.value = data;
    const date = new Date(pedido_item.value.inserido_em);
    inserido_em.value = dateTime2Text(date);
    quantidade.value = pedido_item.value.quantidade;
    valor_unitario.value = parseFloat(pedido_item.value.preco);
    programacao.value = parseFloat(pedido_item.value.programacao);
    ajuste.value = parseFloat(pedido_item.value.ajuste);
    if (pedido_item.value.pedido.entrega) {
      data_entrega.value = pedido_item.value.pedido.entrega;
    } else {
      data_entrega.value = strDoisDiasDepois;
    }
  }
}

function doGetPedidoItem() {
  getPedidoItem({
    id: route.params.id,
    callBack: cbPedidoItem
  });
}

function doGetPedidoItemAndCalc() {
  doGetPedidoItem();
  calcValor();
  calcValorFinal();
}

function cbSaveFechamento(data, error) {
  if (data) {
    doGetPedidoItemAndCalc();
  }
}

function doSaveFechamento() {
  if (
    data_entrega?.value &&
    quantidade?.value &&
    valor_unitario?.value
  ) {
    saveFechamento({
      id: route.params.id,
      data_entrega: data_entrega.value,
      quantidade: quantidade.value,
      valor_unitario: valor_unitario.value,
      programacao: programacao.value,
      ajuste: ajuste.value,
      callBack: cbSaveFechamento,
    });
  }
}

function cbDelFechamento(data, error) {
  if (data) {
    doGetPedidoItemAndCalc();
  }
}

function doDelFechamento() {
  delFechamento({
    id: route.params.id,
    callBack: cbDelFechamento,
  });
}

function cbGetFirstsPedidoItensBordado(data, error) {
  if (data) {
    if (data?.results) pedido_itens_bordado.value = data.results;
  }
}

function doGetFirstsPedidoItensBordado(callBack) {
  getPedidoItens({
    cliente_apelido: pedido_item.value.pedido.cliente.apelido,
    bordado_nome: pedido_item.value.bordado.nome,
    callBack: cbGetFirstsPedidoItensBordado
  });
}

function cbGetFirstsPedidoItensCliente(data, error) {
  if (data) {
    if (data?.results) pedido_itens_cliente.value = 
      data.results.filter((item) => {
        return item.bordado.nome != pedido_item.value.bordado.nome
      });
  }
}

function doGetFirstsPedidoItensCliente(callBack) {
  getPedidoItens({
    cliente_apelido: pedido_item.value.pedido.cliente.apelido,
    callBack: cbGetFirstsPedidoItensCliente
  });
}

// events

function formGrava() {
  doSaveFechamento();
}

function handleApagaClick(event) {
  event.preventDefault();
  doDelFechamento();
}

function handleFinanceiroClick(event) {
  event.preventDefault();
  const apelido = event.target.value;
  router.push({ name: 'financeiro', params: { apelido: apelido } });
}

// Lifecycle Hooks

onMounted(() => {
  doGetPedidoItemAndCalc();
})

// watch

watch(pedido_item, (_) => {
  if (pedido_item) {
    doGetFirstsPedidoItensBordado();
    doGetFirstsPedidoItensCliente();
  }
})

watch(quantidade, (_) => {
  calcValor();
  calcValorFinal();
})

watch(valor_unitario, (_) => {
  calcValor();
  calcValorFinal();
})

watch(programacao, (_) => {
  calcValorFinal();
})

watch(ajuste, (_) => {
  if (!inputValorFinalFocused) {
    calcValorFinal();
  }
})

watch(valor_final, (_) => {
  if (inputValorFinalFocused) {
    calcAjuste();
  }
})

// generic functions

function calcValor() {
  const calculo = quantidade.value * valor_unitario.value;
  valor.value = ptBrCurrencyFormat.format(calculo);
}

function calcValorFinal() {
  const calculo = quantidade.value * valor_unitario.value
    + programacao.value + ajuste.value;
  valor_final.value = floatRound(calculo, 2);
}

function calcAjuste() {
  const calculo = valor_final.value
    - quantidade.value * valor_unitario.value
    - programacao.value;
  ajuste.value = floatRound(calculo, 2);
}

</script>

<template>
  <div>
    <section id="titulo" class="flex pt-4 place-content-between">
      <h2 class="inline font-bold text-xl">Fechando pedido <span class="text-indigo-700">{{ route.params.id }}</span></h2>
      <a title="Voltar" class="button text-xl cursor-pointer" @click.prevent="router.go(-1)">&#x2190;</a>
    </section>

    <div v-if="pedido_item">
      <table class="w-full">
        <thead>
          <tr>
            <th>Usuário</th>
            <th>Data</th>
            <th>Cliente</th>
            <th>Bordado</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>{{ pedido_item.usuario.username }}</td>
            <td>{{inserido_em}}</td>
            <td>
              {{pedido_item.pedido.cliente.apelido}}
              <button
                class="button-text-shadow"
                :value="pedido_item.pedido.cliente.apelido"
                @click="handleFinanceiroClick"
                title="Financeiro"
              >💲</button>
            </td>
            <td>{{pedido_item.bordado.nome}}</td>
          </tr>
        </tbody>
      </table>

      <h3 class="my-4 font-bold text-lg">Dados do bordado</h3>
        <form @submit.prevent="formGrava()">
        <table class="w-full">
          <thead>
            <tr>
              <th><label for="data_entrega">Data de entrega</label></th>
              <th><label for="quantidade">Quantidade</label></th>
              <th><label for="valor_unitario">Valor unitário</label></th>
              <th>Valor</th>
              <th><label for="programacao">Programação</label></th>
              <th><label for="ajuste">Ajuste</label></th>
              <th>Valor final</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>
                <input
                  class="px-2 py-1 w-40 border-2 rounded"
                  type="date"
                  name="data_entrega"
                  id="data_entrega"
                  v-focus
                  v-model="data_entrega"
                  @input="alerta = ''"
                  required>
              </td>
              <td>
                <input
                  class="px-2 py-1 w-24 border-2 rounded"
                  type="number"
                  name="quantidade"
                  id="quantidade"
                  placeholder="0"
                  v-model="quantidade"
                  @input="alerta = ''"
                  required>
              </td>
              <td>
                <input
                  class="px-2 py-1 w-24 border-2 rounded"
                  type="number"
                  step="0.01"
                  name="valor_unitario"
                  id="valor_unitario"
                  placeholder="0,00"
                  v-model="valor_unitario"
                  @input="alerta = ''"
                  required>
              </td>
              <td>
                 {{ valor }}
              </td>
              <td>
                <input
                  class="px-2 py-1 w-24 border-2 rounded"
                  type="number"
                  step="0.01"
                  name="programacao"
                  id="programacao"
                  placeholder="0,00"
                  v-model="programacao"
                  @input="alerta = ''"
                  required>
              </td>
              <td>
                <input
                  class="px-2 py-1 w-24 border-2 rounded"
                  type="number"
                  step="0.01"
                  name="ajuste"
                  id="ajuste"
                  placeholder="0,00"
                  v-model="ajuste"
                  @input="alerta = ''"
                  required>
              </td>
              <td>
                 <input
                  class="px-2 py-1 w-24 border-2 rounded"
                  type="number"
                  step="0.01"
                  name="valor_final"
                  id="valor_final"
                  placeholder="0,00"
                  v-model="valor_final"
                  @focus="inputValorFinalFocused = true"
                  @blur="inputValorFinalFocused = false"
                  @input="alerta = ''"
                  required>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-if="alerta" class="my-4 text-red-600">{{ alerta }}</p>
        <p class="flex flex-row-reverse place-content-between">
          <button
            class="px-2 py-1 rounded-xl bg-sky-700 font-bold text-slate-100"
            type="submit"
          >Grava</button>
          <button
            v-if="pedido_item.quantidade"
            class="px-2 py-1 rounded-xl bg-sky-700 font-bold text-slate-100"
            @click="handleApagaClick"
          >Apaga fechamento</button>
        </p>
      </form>
    </div>

    <div v-if="pedido_itens_bordado.length > 0">
      <h3 class="my-4 font-bold text-lg">Últimos pedidos desse bordado</h3>
      <table class="w-full">
        <thead>
          <tr>
            <th>Pedido</th>
            <th>Data de entrega</th>
            <th>Quantidade</th>
            <th>Valor unitário</th>
            <th>Valor</th>
            <th>Programação</th>
            <th>Ajuste</th>
            <th>Valor final</th>
          </tr>
        </thead>
        <tbody>
          <tr
            :class="{ 'font-bold': pedido_item_bord.id == route.params.id }"
            v-for="pedido_item_bord in pedido_itens_bordado"
            :key="pedido_item_bord.id"
          >
            <td
              :class="{ 'text-indigo-700': pedido_item_bord.id == route.params.id }"
            >{{ pedido_item_bord.id }}</td>
            <td>{{ inputStrDate2PtBrDate(pedido_item_bord.pedido.entrega, empty='-') }}</td>
            <td>{{ pedido_item_bord.quantidade }}</td>
            <td>{{ ptBrCurrencyFormat.format(pedido_item_bord.preco) }}</td>
            <td>{{ ptBrCurrencyFormat.format(pedido_item_bord.quantidade * pedido_item_bord.preco) }}</td>
            <td>{{ ptBrCurrencyFormat.format(pedido_item_bord.programacao) }}</td>
            <td>{{ ptBrCurrencyFormat.format(pedido_item_bord.ajuste) }}</td>
            <td>{{ ptBrCurrencyFormat.format(
              (pedido_item_bord.quantidade * pedido_item_bord.preco)
              + parseFloat(pedido_item_bord.programacao) + parseFloat(pedido_item_bord.ajuste)
            ) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="pedido_itens_cliente.length > 0">
      <h3 class="my-4 font-bold text-lg">Últimos pedidos de outros bordados desse cliente</h3>
      <table class="w-full">
        <thead>
          <tr>
            <th>Pedido</th>
            <th>Bordado</th>
            <th>Data de entrega</th>
            <th>Quantidade</th>
            <th>Valor unitário</th>
            <th>Valor</th>
            <th>Programação</th>
            <th>Ajuste</th>
            <th>Valor final</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="pedido_item_clie in pedido_itens_cliente"
            :key="pedido_item_clie.id"
          >
            <td>{{ pedido_item_clie.id }}</td>
            <td>{{ pedido_item_clie.bordado.nome }}</td>
            <td>{{ inputStrDate2PtBrDate(pedido_item_clie.pedido.entrega, empty='-') }}</td>
            <td>{{ pedido_item_clie.quantidade }}</td>
            <td>{{ ptBrCurrencyFormat.format(pedido_item_clie.preco) }}</td>
            <td>{{ ptBrCurrencyFormat.format(pedido_item_clie.quantidade * pedido_item_clie.preco) }}</td>
            <td>{{ ptBrCurrencyFormat.format(pedido_item_clie.programacao) }}</td>
            <td>{{ ptBrCurrencyFormat.format(pedido_item_clie.ajuste) }}</td>
            <td>{{ ptBrCurrencyFormat.format(
              (pedido_item_clie.quantidade * pedido_item_clie.preco)
              + parseFloat(pedido_item_clie.programacao) + parseFloat(pedido_item_clie.ajuste)
            ) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

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
</style>
