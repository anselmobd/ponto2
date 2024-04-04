<script setup>
import { storeToRefs } from 'pinia';
import { useAuthStore } from '@/stores/auth.js';
import router from '@/router'

const auth = useAuthStore()
const { user } = storeToRefs(auth)
const { encerrar } = auth
</script>

<template>
  <div id="nav" class="px-4 flex row items-center justify-between border-b border-solid border-slate-800 shadow-[0_2px_2px_-1px] shadow-slate-700">
    <router-link
      class="router-link text-2xl font-bold"
      :to="{ name: 'home' }"
      :exact-active-class="'text-sky-600'"
    >RPR - Ponto2</router-link>

    <div>
      <router-link 
        class="router-link px-1 border-l border-sky-600"
        v-if="user.name"
        :to="{ name: 'bordado' }"
        :exact-active-class="'text-sky-600 font-bold'"
      >Pedido</router-link>
      <router-link
        class="router-link px-1 border-l border-sky-600"
        :to="{ name: 'sobre' }"
        :exact-active-class="'text-sky-600 font-bold'"
      >Sobre</router-link>
      <span class="border-l border-sky-600"></span>
    </div>

    <div>
      <span v-if="user.name">{{user.name}}&ThickSpace;</span>
      <router-link
        class="px-2 py-0.5 rounded-lg bg-sky-700 font-bold text-slate-100 block"
        v-if="!user.name"
        :to="{ name: 'login' }"
      >Identificar-se</router-link>
      <button
        type="button"
        class="px-2 py-0.5 rounded-lg bg-sky-700 font-bold text-slate-100"
        v-if="user.name" 
        @click.stop="encerrar(); router.push({ name: 'home' })"
      >Encerrar</button>
    </div>
  </div>
</template>

<style scoped>

.router-link:not(.router-link-active):hover {
  text-shadow: 1px 1px 2px  rgba(3, 132, 196, 0.7)
}

</style>