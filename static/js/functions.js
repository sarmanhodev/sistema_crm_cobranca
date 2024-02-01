async function dados_procedimentos(){
    fetch("./js/procedimentos.json")
    .then(function(resp){
      return resp.json();
    })
    .then(function(data){
        nome_procedimento='';
        escolha =`<option selected>Escolha um procedimento</option>`;
      for (i=0;i<data.length;i++){
        
        nomes =`<option value="${data[i].procedimento}">${data[i].procedimento}</option>`;
        
        nome_procedimento += nomes;
        console.log(data[i].procedimento);
        console.log("R$ " + data[i].valor);

        let container = document.querySelector('#select_procedimentos');
        container.innerHTML = escolha + nome_procedimento;
      }
      
   });
  }
  dados_procedimentos();


  


