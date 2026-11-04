# Ortopolidade: processos, distribuições e exploração interativa

4 de novembro de 2026. Síntese dos mecanismos e exemplos do repositório,
acompanhada de um laboratório didático na
[página pública](https://ttm.github.io/orthopolity/).

## Em que sentido a formulação está correta?

Sim, com uma precisão: a ortopolidade designa uma **relação de alocação e uma
hipótese de tendência à equalização**, que diferentes processos podem realizar.
Não é, por definição, uma lista de processos. A ideia comum é a igualdade de
recurso **por unidade de uma medida de referência entre classes de objetos**.
Os objetos podem ser pessoas, organismos, partículas ou outros portadores de
recurso. “Concentrações” precisa, portanto, indicar quais classes estão sendo
comparadas, e “equânime” significa igualdade quantitativa nesse critério,
sem estabelecer um juízo de justiça.

Se cada objeto da classe $i$ contém ou exige $q_i>0$ unidades de recurso, a
classe tem abundância $N_i$, estoque $R_i=q_iN_i$ e peso de referência $w_i>0$.
A assinatura neutra é

$$\frac{R_i}{w_i}=C,\qquad \frac{N_i}{w_i}=\frac{C}{q_i}.$$

Assim, classes com maior recurso por objeto têm **menor abundância por unidade
da medida de referência**. A igualdade entre classes é compatível com recursos
individuais diferentes. Não implica que toda dinâmica aumente um índice de
desigualdade, nem que toda desigualdade tenha essa origem. Se os $q_i$ forem
iguais, não há diferença de recurso por objeto a explicar. Se os pesos das
classes forem diferentes, seus totais $R_i$ também podem ser diferentes.

Há duas leituras que convém separar:

- **Recurso por objeto fixado:** redistribuir $R_i$ muda $N_i=R_i/q_i$;
  montagem, desmonte ou substituição dos objetos fica implícita na descrição
  contínua. O total de recurso pode permanecer fixo enquanto o número de
  objetos muda.
- **Número de pessoas por grupo fixado:** repartir uma verba igualmente entre
  grupos de tamanhos diferentes produz recebimentos individuais diferentes.
  Aqui o recebimento $q_i=R_i/N_i$ muda. É a leitura do exemplo das TVs.

A definição e suas fronteiras estão no [glossário](glossary.md) e em
[conceitos e limites](concept.md).

## Igual em qual medida?

| Referência fixada antes do cálculo | Peso de uma classe $[a_i,b_i]$ | O que fica igual |
| --- | --- | --- |
| **log-orthopolic** em tamanho $k$ | $w_i=\ln(b_i/a_i)$, com $a_i>0$ | Recurso por intervalo logarítmico de tamanho |
| **linear-orthopolic** em tamanho $k$ | $w_i=b_i-a_i$ | Recurso por intervalo linear de tamanho |
| Discreta por classe previamente definida | $w_i=1$ | Recurso por classe |

Com requisito $q(k)\propto k^d$, a densidade de abundância por tamanho linear
$dN/dk$ é proporcional a $k^{-(d+1)}$ na referência **log-orthopolic**, e a
$k^{-d}$ na referência **linear-orthopolic**. Uma abundância por classe não é
a mesma grandeza que essa densidade. Em classes finitas, $q_i$ é o requisito
representativo adotado para a classe; isso não determina a distribuição dentro
dela. Com outro requisito positivo, o perfil inverso pode não ser uma lei de
potência.

Conservação do recurso não escolhe a medida. Escolher a medida ou o recurso
depois de observar uma curva pode produzir uma hipótese, mas não confirma essa
hipótese com a própria curva.

## Processos e construções que realizam a relação

A lista distingue mecanismos dinâmicos, construções de alocação e realizações
físicas. Eles não têm todos os mesmos objetos, recursos ou estatutos de evidência.

1. **Relaxação global dos estoques de classes.** Cada classe cede ou recebe
   recurso a uma taxa proporcional ao desvio de sua parcela neutra. Para
   $B=\sum_iR_i$ e $W=\sum_iw_i$,
   $\dot R_i=\lambda(Bw_i/W-R_i)$, com $\lambda>0$.
   O estoque conserva-se, a positividade preserva-se e qualquer estado inicial
   admissível converge exponencialmente para $R_i^*=Bw_i/W$. É um operador
   didático explícito de equalização; usar a meta na regra não descobre sua
   ocorrência espontânea na natureza. Pode representar tanto a referência
   **log-orthopolic** quanto **linear-orthopolic**, conforme os pesos fixados.

2. **Trocas locais entre classes conectadas.** O fluxo entre duas classes é
   proporcional à diferença $R_i/w_i-R_j/w_j$. Condutâncias simétricas e uma
   rede conectada levam ao mesmo estado neutro, com uma trajetória que depende
   da rede. Classes inicialmente vazias podem receber recurso. A versão com
   pacotes aleatórios de recurso tem essa dinâmica em sua média; um número
   finito de pacotes deixa flutuações em cada realização. O modelo existente
   usa referência **log-orthopolic** em tamanho e contagens equivalentes
   contínuas de objetos. Ver [troca entre classes](class-exchange.md).

3. **Equalização por encontros de pares.** Em cada encontro de dois reservatórios
   de classe, combina-se seu recurso e reparte-se em proporção aos pesos
   $w_i,w_j$. Isso iguala $R_i/w_i$ e $R_j/w_j$ naquele par. Encontros repetidos
   que conectam todas as classes produzem a alocação neutra. A ordem dos
   encontros pode ser aleatória sem tornar aleatória a regra de partilha.
   Esta é outra realização didática, compatível com referência
   **log-orthopolic** ou **linear-orthopolic**. Uma partilha aleatória diferente
   precisa de outra análise: igualdade na média não significa um retrato
   instantâneo plano.

4. **Partilhas aleatórias entre reservatórios de classe.** Sorteiam-se um par
   e sua divisão, mantendo o orçamento do par. A interface usa
   $U\sim\operatorname{Beta}(Kw_i/W,Kw_j/W)$ e
   $R_i'=U(R_i+R_j)$, com $R_j'=(1-U)(R_i+R_j)$, $K$ classes e
   $W=\sum_iw_i$. A distribuição estacionária das parcelas é
   $\operatorname{Dirichlet}(Kw_1/W,\ldots,Kw_K/W)$: a média tem o perfil
   neutro, mas a variância permanece positiva. Os pontos da interface mostram
   a esperança matemática exata após o número de encontros, não uma média
   temporal da realização exibida. A escolha de pesos permite tanto
   **log-orthopolic** quanto **linear-orthopolic**; uma divisão uniforme só
   tem a média desejada quando os dois pesos são iguais.

5. **Montagem e desmonte de objetos inteiros.** Monômeros formam dímeros,
   dímeros formam tetrâmeros, e as reações inversas devolvem integralmente o
   material. No modelo construído com taxas constantes por canal viável e
   razões de taxas neutras, as massas médias das três classes aproximam-se
   da igualdade quando o orçamento cresce. A referência é **log-orthopolic
   na massa física**, nas classes fixas 1, 2 e 4. Há correção exata para
   orçamento finito, e cada retrato permanece flutuante. Cinética de ação das
   massas, com o mesmo material e as mesmas reações, dá outra distribuição.
   Ver [montagem de objetos inteiros](whole-object-assembly-2026-10-31.md).

6. **Partilha de verbas entre níveis com populações diferentes.** Uma verba
   igual por nível, dividida entre números diferentes de pessoas, dá
   recebimentos por pessoa inversamente proporcionais à população do nível.
   O [exemplo das TVs](tv-distribution-model.md) fixa cinco grupos disjuntos
   e um orçamento contabilizado uma única vez. A referência é discreta por
   nível e, na hierarquia geométrica declarada, **log-orthopolic nos
   recebimentos adicionais positivos**. Não é linear-orthopolic nesses
   recebimentos, nem implica ortopolidade no benefício “TV mais dinheiro”.
   Trata-se de uma construção contábil, não de uma estimativa da economia.

7. **Equalização de potencial em reservatórios.** Vasos comunicantes ou uma
   rede de armazenadores passivos podem trocar recurso até igualar altura,
   concentração ou outro potencial apropriado ao sistema. Se as curvas de
   armazenamento forem proporcionais, $R_i=w_i f(x_i)$, o potencial comum
   implica $R_i/w_i$ comum. Os pesos são capacidades físicas previamente
   medidas: **não são automaticamente log-orthopolic nem linear-orthopolic
   em tamanho**. Curvas não proporcionais podem igualar potencial sem
   equalizar recurso por esses pesos. Alterar apenas conexões muda a trajetória;
   alterar o armazenamento pode mudar o destino. Ver
   [intervenção no armazenamento](storage-intervention-design-2026-10-25.md).

8. **Transporte radial de energia em meio transparente.** Uma fonte
   estacionária fornece a mesma potência através de esferas sucessivas;
   a densidade média de fluxo diminui como $1/r^2$. Essa potência conta a
   passagem da mesma energia, não parcelas independentes de um estoque.
   Com propagação radial a velocidade constante, cascas disjuntas de igual
   espessura guardam igual energia: uma relação **linear-orthopolic em
   raio**, não log-orthopolic em raio. Absorção e sua remoção produzem
   partidas e recuperações calculáveis. Não é uma lei de abundância de objetos.
   Ver [realização eletromagnética](physical-realizations.md).

9. **Equipartição térmica clássica entre modos.** Em equilíbrio canônico,
   cada modo harmônico tem a mesma energia média, embora suas coordenadas
   e energias instantâneas variem. A referência é a contagem de modos,
   **nem log-orthopolic nem linear-orthopolic em tamanho**; intervalos de
   frequência contêm quantidades diferentes de modos. A quantização produz
   uma partida calculável da igualdade clássica. A fórmula de equilíbrio
   sozinha não especifica como ocorre a termalização. Ver
   [radiação térmica](thermal-radiation.md).

Essas entradas não afirmam que qualquer redistribuição produz ortopolidade.
Por exemplo, trocas aleatórias de dinheiro **entre pessoas** podem produzir
uma distribuição exponencial de riqueza, sem igualdade de dinheiro entre
classes logarítmicas de riqueza. Igualdade esperada entre pessoas identificadas
não é igualdade entre classes de concentração. Do mesmo modo, cortes
espaciais uniformes conservam massa, mas não igualam a massa entre classes de
tamanho dos fragmentos. Ver os [modelos de comparação](model-sources.md#3-conservative-pair-exchange)
e a [fronteira de fragmentação](supporting-material.md#s38-fragmentation-conserves-mass-without-equal-logarithmic-allocation).

## O que significa transformar uma distribuição qualquer?

No laboratório de classes, “qualquer” significa um vetor finito de entradas
não negativas, de soma positiva, sobre as classes disponíveis. Requisitos e
pesos são positivos e finitos. A escolha de domínio, classes, medida e
requisitos precede a transformação. Isso inclui classes vazias, picos e
distribuições multimodais; não inclui números negativos, recurso infinito,
um domínio ilimitado ou entradas sem significado físico.

Para abundâncias iniciais $N_i(0)$, calcula-se

$$R_i(0)=q_iN_i(0),\quad B=\sum_iR_i(0),\quad
R_i^*=\frac{Bw_i}{W},\quad N_i^*=\frac{Bw_i}{Wq_i}.$$

A transformação conserva **$B$**, não geralmente $\sum_iN_i$. Os números
finais podem ser fracionários: são abundâncias equivalentes, não uma simulação
de pessoas ou partículas indivisíveis. Impor simultaneamente orçamento,
população, requisitos e igualdade pode tornar a meta inviável. Se o objetivo
for somente uma distribuição de probabilidade, a normalização final é

$$p_i^*=\frac{w_i/q_i}{\sum_jw_j/q_j};$$

normalizar não cria uma segunda lei de conservação. Um vetor inteiramente
nulo tem orçamento zero e não define uma distribuição de probabilidade nem
a assinatura neutra positiva.

Para comparar as etapas de uma dinâmica, uma medida simples é a distância
de variação total entre as parcelas atuais e as neutras:

$$D=\frac12\sum_i\left|\frac{R_i}{B}-\frac{w_i}{W}\right|.$$

Ela vale zero exatamente na meta de alocação. Não é um índice de desigualdade
de pessoas. A igualdade deve aparecer no gráfico de $R_i/w_i$; mostrar apenas
abundância, apenas estoques por classes de larguras diferentes ou apenas uma
reta em escala logarítmica pode esconder a comparação correta.

## Por que os operadores convergem?

Na relaxação global, a solução explícita é

$$R_i(t)=R_i^*+[R_i(0)-R_i^*]e^{-\lambda t}.$$

Ela é uma combinação convexa da condição inicial e da meta. A troca local usa
$x_i=R_i/w_i$ e condutâncias simétricas $g_{ij}\ge0$:

$$\dot R_i=\sum_jg_{ij}(x_j-x_i).$$

Com $\bar x=B/W$, a dispersão ponderada
$V=\frac12\sum_iw_i(x_i-\bar x)^2$ satisfaz

$$\dot V=-\sum_{\{i,j\}}g_{ij}(x_i-x_j)^2\le0.$$

Em uma rede conectada, o único estado sem diferenças nas arestas tem
$x_i=\bar x$ em todas as classes. Se a rede for desconectada, cada componente
retém seu próprio orçamento; não se promete equalização global.

A implementação usa pesos normalizados $\pi_i=w_i/W$ e
$g_{i,i+1}=((K-1)^2/8)\pi_i\pi_{i+1}/(\pi_i+\pi_{i+1})$ na equação
em $R_i/\pi_i$. Essa escolha apenas define o relógio didático. A exponencial
da matriz geradora é calculada com matrizes estocásticas não negativas,
preservando positividade e orçamento até arredondamento numérico.

Na equalização de um par, escreve-se $S=R_i+R_j$ e substitui-se

$$R_i'=\frac{w_iS}{w_i+w_j},\qquad
R_j'=\frac{w_jS}{w_i+w_j}.$$

O orçamento do par conserva-se, os estoques permanecem não negativos, e a
queda de $V$ é
$\frac{w_iw_j}{2(w_i+w_j)}(x_i-x_j)^2$. Seleção independente de pares com
probabilidades positivas numa rede conectada dá convergência quase certa.
Uma sequência que deixa classes permanentemente isoladas não a garante.

Na interface, encontros por pares usam $\lfloor tK\rfloor$ eventos e uma
semente reproduzível. O botão **Ver alvo** mostra o alvo analítico diretamente,
sem afirmar que uma realização aleatória chegou a ele. O gráfico de quantidades
pode usar $\log_{10}(1+n)$ para incluir zeros; isso não muda a medida de referência.
O laboratório limita a entrada a 2–24 classes e a um milhão de objetos equivalentes
por classe, com $1\le k\le k_{\max}\le10.000$ e $0\le d\le3$.

Tempo da animação e número de atualizações são unidades de modelo. Uma taxa
física ou um prazo real exigem calibração independente. Para dinâmicas
estocásticas com partilha flutuante, a convergência pode ser da distribuição
ou da média, e não de cada estado a uma curva sem flutuações.

## Exploração e confirmação

O laboratório permite verificar consequências de regras declaradas e comparar
caminhos até uma mesma alocação. Ele é uma demonstração matemática e
computacional. Levar uma entrada à meta por uma regra criada para isso não é
evidência de que essa regra descreva um fenômeno observado.

Uma aplicação empírica precisa fixar objetos, recurso, requisitos, medida,
domínio, orçamento, restrições e critério de avaliação antes dos resultados;
depois, testar uma previsão separada, idealmente uma intervenção que distinga
mecanismos. O [estado do projeto](status.md) conserva tanto os resultados
favoráveis quanto as comparações negativas e inconclusivas. Esta interface
não acrescenta uma confirmação empírica ao registro.
