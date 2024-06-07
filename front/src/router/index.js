import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from '@/stores/auth.js';

import Sobre from '../views/Sobre.vue'
import Pedido from '../views/Pedido.vue'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Fechando from '../views/Fechando.vue'
import Financeiro from '../views/Financeiro.vue'
import Cliente from '../views/Cliente.vue'
import Bordado from '../views/Bordado.vue'
import { checkVersion } from '../api/check_version.js';

const routes = [
    {
      path: "/",
      name: "home",
      component: Home,
    },
    {
      path: "/login",
      name: "login",
      component: Login,
    },
    {
      path: "/sobre",
      name: "sobre",
      component: Sobre,
    },
    {
      path: "/pedido",
      name: "pedido",
      component: Pedido,
    },
    {
      path: "/fechando/:id",
      name: "fechando",
      component: Fechando,
    },
    {
      path: "/financeiro/:apelido",
      name: "financeiro",
      component: Financeiro,
    },
    {
      path: "/cliente/:id",
      name: "cliente",
      component: Cliente,
    },
    {
      path: "/bordado/:id",
      name: "bordado",
      component: Bordado,
    },
];

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes,
  });

router.beforeEach(async (to, from) => {
  const auth = useAuthStore();
  checkVersion();
  let autenticado = false;
  if ( auth && auth.user && auth.user.name ) {
    autenticado = true;
  }
  if (
    !autenticado &&
    ['home', 'login', 'sobre'].indexOf(to.name) < 0
  ) {
    return { name: 'home' }
  }
})

export default router;
