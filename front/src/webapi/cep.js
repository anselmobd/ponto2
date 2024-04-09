export function buscarPorCep({
  cep=null,
  callBack=()=>{}
}) {
    fetch(`https://viacep.com.br/ws/${cep}/json/`)
      .then(response => response.json()) // Aqui você deve retornar a promessa para que o próximo .then possa lidar com o JSON
      .then(json => callBack(json))
      .catch(error => console.error('Erro ao buscar CEP:', error));
}
   