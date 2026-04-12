// CAIXINHA 1: Faz a tela descer até o FINAL DA PÁGINA
function fazerScroll() {
    setTimeout(function() {
        try {
            const doc = window.parent.document;
            
            // Pega o contêiner principal onde o Streamlit coloca a barra de rolagem
            const container = doc.querySelector('[data-testid="stMain"]');
            
            if (container) {
                // Rola suavemente até a altura máxima (o fundo absoluto)
                container.scrollTo({
                    top: container.scrollHeight, 
                    behavior: 'smooth'
                });
            } else {
                // Plano B (Fallback): Rola a janela inteira do navegador
                window.parent.scrollTo({
                    top: doc.body.scrollHeight, 
                    behavior: 'smooth'
                });
            }
        } catch(e) {
            console.log("Erro no scroll:", e);
        }
    }, 700); // 700ms dá tempo da planilha ser processada antes de descer
}