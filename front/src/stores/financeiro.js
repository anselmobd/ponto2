import { defineStore } from 'pinia';

export const useFinanceiroVueStore = defineStore('financeiro_vue', {
  state: () => ({
    precisaRecarregar: false,
    componentesRegistrados: {},
    componentesRecarregados: new Set(),
  }),
  actions: {
    ativarRecarregar() {
      this.precisaRecarregar = true;
      this.componentesRecarregados.clear();
    },
    registrarComponente(id) {
      // Adiciona registro do filho ao montar
      this.componentesRegistrados[id.name] = id.params;
      this.componentesRegistrados[id.name].concluido = false;
    },
    montaComponenteId(name, params) {
      const sufixo = Object.values(params).join('-');
      if (sufixo) {
        name = [name, sufixo].join('-');
      }
      return {
        name: name,
        params: params
      }
    
    },
    removerRegistroComponente(id) {
      // Remove o registro do filho ao desmontar
      delete this.componentesRegistrados[id.name];
    },
    componenteConcluiuRecarregar(id) {
      if (this.componentesRegistrados[id.name]) {
        this.componentesRegistrados[id.name].concluido = true;
        this.componentesRecarregados.add(id.name);
      }
      if (Object.values(this.componentesRegistrados).every(filho => filho.concluido)) {
        this.precisaRecarregar = false;
      }
    },
  },
});
