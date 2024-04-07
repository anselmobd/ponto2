<script setup>
import router from '@/router'
import { useRoute, onBeforeRouteUpdate } from "vue-router";
import { ref, onMounted, watch } from 'vue'
import { getPedidoItem, saveFechamento, delFechamento, getPedidoItens } from '../api/pedidoItem.js';
import { dateTime2Text, date2InputText, inputStrDate2PtBrDate } from "../utils/date.js";
import { ptBrCurrencyFormat } from "../utils/numStr.js";
import { floatRound } from "../utils/number.js";

// TODO
// - valores: não permitir valores com fração de centavo

const route = useRoute();

const fechando_id = ref(route.params.id);
// console.log('fechando_id', fechando_id);

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
    id: fechando_id.value,
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
      id: fechando_id.value,
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
    id: fechando_id.value,
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
    bordado_codigo: pedido_item.value.bordado.codigo,
    callBack: cbGetFirstsPedidoItensBordado
  });
}

function cbGetFirstsPedidoItensCliente(data, error) {
  if (data) {
    if (data?.results) pedido_itens_cliente.value = 
      data.results.filter((item) => {
        return (
          item.bordado.nome != pedido_item.value.bordado.nome  ||
          item.bordado.codigo != pedido_item.value.bordado.codigo
        )
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

function handleFechandoClick(event) {
  event.preventDefault();
  const id = event.target.value;
  console.log(id);
  router.push({ name: 'fechando', params: { id: id } });
}

// Lifecycle Hooks

onMounted(() => {
  doGetPedidoItemAndCalc();
})

// Navigation Guards

onBeforeRouteUpdate(async (to, from, next) => {
  console.log('onBeforeRouteUpdate');
  if (to.params.id !== from.params.id) {
    console.log('next');
    fechando_id.value = to.params.id;
    doGetPedidoItemAndCalc();
    next();
  }
});

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
      <h2 class="inline font-bold text-xl">Fechando pedido <span class="text-indigo-700">{{ fechando_id }}</span></h2>
      <a title="Voltar" class="button text-xl cursor-pointer" @click.prevent="router.go(-1)">&#x2190;</a>
    </section>

    <div v-if="pedido_item">
      <table class="w-full">
        <thead>
          <tr>
            <th rowspan="2">Usuário</th>
            <th rowspan="2">Data</th>
            <th rowspan="2">Cliente</th>
            <th colspan="2">Bordado</th>
          </tr>
          <tr>
            <th>Nome</th>
            <th>Código</th>
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
            <td>{{pedido_item.bordado.codigo}}</td>
          </tr>
        </tbody>
      </table>

      <form
        v-if="!pedido_item.cobrancas.length"
        @submit.prevent="formGrava()"
      >
        <h3 class="my-4 font-bold text-lg">Dados do pedido</h3>
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
            <th>Cobrado</th>
            <th>Ação</th>
          </tr>
        </thead>
        <tbody>
          <tr
            :class="{
              'font-bold': pedido_item_bord.id == fechando_id,
              'bg-slate-100': pedido_item_bord.id == fechando_id
            }"
            v-for="pedido_item_bord in pedido_itens_bordado"
            :key="pedido_item_bord.id"
          >
            <td>
              <span
                v-if="pedido_item_bord.id == fechando_id"
                class="text-indigo-700"
              >
                {{ pedido_item_bord.id }}
              </span>
              <router-link
                v-if="pedido_item_bord.id != fechando_id"
                :to="{ name: 'fechando', params: { id: pedido_item_bord.id } }"
                class="router-link text-sky-800"
                title="Dados do fechamento do pedido"
              >{{pedido_item_bord.id}}</router-link>
            </td>
            <td>{{ inputStrDate2PtBrDate(pedido_item_bord.pedido.entrega, empty='-') }}</td>
            <td>{{ pedido_item_bord.quantidade }}</td>
            <td>{{ ptBrCurrencyFormat.format(pedido_item_bord.preco) }}</td>
            <td>{{ ptBrCurrencyFormat.format(pedido_item_bord.quantidade * pedido_item_bord.preco) }}</td>
            <td>{{ ptBrCurrencyFormat.format(pedido_item_bord.programacao) }}</td>
            <td>{{ ptBrCurrencyFormat.format(pedido_item_bord.ajuste) }}</td>
            <td>
              {{
                ptBrCurrencyFormat.format(
                  (pedido_item_bord.quantidade * pedido_item_bord.preco)
                  + parseFloat(pedido_item_bord.programacao) + parseFloat(pedido_item_bord.ajuste)
                )
              }}
            </td>
            <td>
              {{ pedido_item_bord.cobrancas.length ? 'Sim' : ( pedido_item_bord.pedido.entrega ? 'Não' : '-' ) }}
            </td>
            <td>
              <button
                v-if="pedido_item_bord.id != fechando_id"
                class="button-text-shadow"
                :value="pedido_item_bord.id"
                @click="handleFechandoClick"
                title="Fechamento"
              >🪡</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="pedido_itens_cliente.length > 0">
      <h3 class="my-4 font-bold text-lg">Últimos pedidos de outros bordados desse cliente</h3>
      <table class="w-full">
        <thead>
          <tr>
            <th rowspan="2">Pedido</th>
            <th colspan="2">Bordado</th>
            <th rowspan="2">Data de entrega</th>
            <th rowspan="2">Quantidade</th>
            <th rowspan="2">Valor unitário</th>
            <th rowspan="2">Valor</th>
            <th rowspan="2">Programação</th>
            <th rowspan="2">Ajuste</th>
            <th rowspan="2">Valor final</th>
            <th rowspan="2">Cobrado</th>
            <th rowspan="2">Ação</th>
          </tr>
          <tr>
            <th>Nome</th>
            <th>Código</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="pedido_item_clie in pedido_itens_cliente"
            :key="pedido_item_clie.id"
          >
            <td>
              <router-link
                :to="{ name: 'fechando', params: { id: pedido_item_clie.id } }"
                class="router-link text-sky-800"
                title="Dados do fechamento do pedido"
              >{{pedido_item_clie.id}}</router-link>
            </td>
            <td>{{ pedido_item_clie.bordado.nome }}</td>
            <td>{{ pedido_item_clie.bordado.codigo }}</td>
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
            <td>
              {{ pedido_item_clie.cobrancas.length ? 'Sim' : ( pedido_item_clie.pedido.entrega ? 'Não' : '-' ) }}
            </td>
            <td>
              <button
                class="button-text-shadow"
                :value="pedido_item_clie.id"
                @click="handleFechandoClick"
                title="Fechamento"
              >🪡</button>
            </td>
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
.router-link:not(.router-link-active):hover {
  text-shadow: 1px 1px 2px  rgba(3, 132, 196, 0.7)
}
</style>
