import axios from 'axios';

export function checkVersion() {
  axios.get('/version.json')
    .then(response => {
      const serverVersion = response.data.version_date_time;
      console.log(serverVersion);
      const localVersion = import.meta.env.VITE_VERSION_DATE_TIME;
      console.log(localVersion);

      if (serverVersion !== localVersion) {
        console.error('Versão alterada');
        const answer = window.confirm('Versão atual "'+localVersion+'". Nova versão detectada "'+serverVersion+'". Recarregar a página agora?')
        if (answer) {
          window.location.reload(true);
        }
      } else {
        console.error('Versão mantida');
      }
    })
    .catch(error => {
      console.error('Erro ao verificar a versão:', error);
    });
};

// Verifica a versão a cada 5 minutos
// setInterval(checkVersion, 5 * 60 * 1000);

// Verifica a versão ao carregar a página
// checkVersion();
