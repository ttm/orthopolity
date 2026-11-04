# Uma TV para cada cidadão: igualdade na entrega, desigualdade nos recebimentos

4 de novembro de 2026. **Derivação própria; exemplo construído e exploratório.**
Os valores abaixo são hipóteses didáticas, não estimativas do setor de televisores.
O exemplo mostra que igualdade de um benefício direto pode coexistir com
desigualdade dos recebimentos associados à sua produção e comercialização.
Não demonstra que toda doação universal aumenta a desigualdade patrimonial de
um país, nem constitui confirmação empírica da ortopolidade.

## 1. Dois critérios diferentes de igualdade

O governo compra uma TV para cada um dos $N$ cidadãos, ao preço unitário $p$.
O gasto público é

$$B=Np.$$

Todos recebem exatamente um aparelho. Para somar aparelhos e dinheiro numa
mesma unidade contábil, convencionamos que cada TV tem valor $p$ para seu
recebedor. Isso não pressupõe igual utilidade subjetiva e pode ser substituído
por uma valoração comum $v$, sem mudar os recebimentos monetários da cadeia.

Uma fração $m$ do gasto remunera os grupos explicitamente representados no
modelo: comissões, remunerações adicionais e lucros atribuídos à encomenda.
O restante paga outros custos de produção e distribuição:

$$M=mB,\qquad C=(1-m)B,\qquad B=C+M.$$

Aqui $M$ é um agregado contábil dos recebimentos selecionados, **não o lucro
de todo o setor**. Os lucros dos proprietários são considerados depois dos
custos e pagamentos já contabilizados. A parcela $C$ pode incluir insumos,
salários não representados, depreciação e fornecedores; seus beneficiários e
suas contrapartidas reais não são modelados individualmente.

Há cinco grupos disjuntos: vendedores, gerentes, donos de lojas, donos de redes
e donos de fábricas. Cada pessoa representada pertence a um único grupo e
também recebe sua TV. Essa simplificação evita contar a mesma pessoa duas
vezes; participações societárias cruzadas exigiriam uma matriz explícita de
propriedade. Os grupos contêm $n_j$ pessoas e recebem frações $a_j$ de $M$,
com

$$n_j\geq1,\quad \sum_j n_j\leq N,\quad a_j\geq0,\quad\sum_j a_j=1.$$

O recebimento adicional de cada integrante do grupo $j$ e o benefício bruto
contabilizado são

$$y_j=\frac{Ma_j}{n_j},\qquad g_j=p+y_j.$$

Os demais $N-\sum_jn_j$ cidadãos têm $y_0=0$ e $g_0=p$ neste recorte.
Assim,

$$\sum_jn_jy_j=M,\qquad \sum_i g_i=Np+M.$$

O último total soma **o valor dos aparelhos recebidos** e **recebimentos
monetários selecionados**; não representa o orçamento público nem a criação
líquida de riqueza. O orçamento continua sendo $B$, particionado uma única
vez entre $C$ e $M$. Não se somam como lucro as vendas brutas da fábrica,
da rede e da loja: isso contaria várias vezes o mesmo dinheiro.

Subir na hierarquia aumenta o recebimento individual somente quando
$a_{j+1}/n_{j+1}>a_j/n_j$. Uma encomenda universal, por si só, não estabelece
essa condição. O cenário seguinte a fixa explicitamente.

## 2. Um cenário ortopólico com grupos de tamanhos diferentes

Distribuímos $M$ igualmente entre os $L=5$ níveis: $a_j=1/L$. Então

$$R_j=n_jy_j=\frac{M}{L},\qquad n_j=\frac{M}{Ly_j}.$$

Cada nível recebe a mesma verba, mas essa verba é dividida entre números
diferentes de pessoas. Esta é a ortopolidade **discreta por nível previamente
definido**, na terminologia do [glossário](glossary.md). O recurso é o
recebimento monetário adicional $y$, não a TV, o faturamento bruto ou o
patrimônio total.

Para conectar essa identidade à medida logarítmica, fixamos antes do cálculo
uma hierarquia geométrica:

$$n_j=f b^{L-1-j},\qquad j=0,\ldots,L-1,\qquad b>1.$$

Para cidadãos inteiros, $f$ e $b$ são inteiros positivos, com $b\geq2$, e
$f(b^L-1)/(b-1)\leq N$. O cenário implica

$$y_j=\frac{M}{Lf b^{L-1}}b^j,\qquad
\ln y_{j+1}-\ln y_j=\ln b.$$

Se $M>0$, os recebimentos positivos ocupam classes igualmente espaçadas em
$\ln y$, com o mesmo recurso em cada classe. A referência é, portanto,
**log-orthopolic no recebimento adicional positivo**, em uma grade finita e
discreta; não é linear-orthopolic em $y$. Os cidadãos com $y=0$ formam uma
massa separada, fora da coordenada logarítmica. Se $M=0$, não há espectro
positivo nem essa interpretação logarítmica.

Uma extensão contínua idealizada da mesma hipótese, em domínio positivo
finito $[y_{\min},y_{\max}]$, satisfaria

$$y\frac{dN}{d\ln y}=K
\quad\Longrightarrow\quad
\frac{dN}{dy}=\frac{K}{y^2}.$$

Essa densidade contínua não é ajustada nem observada no exemplo de cinco
grupos. Sob referência linear-orthopolic, a hipótese diferente
$y\,dN/dy=K$ produziria $dN/dy\propto y^{-1}$. Não se deve confundir a
contagem discreta $n_j\propto1/y_j$ por classe logarítmica com a densidade
contínua por unidade de dinheiro.

Somar o aparelho muda o recurso: $n_jg_j=n_jp+M/L$, que não é constante
quando os $n_j$ diferem. Portanto o cenário é ortopólico nos recebimentos
adicionais dos níveis, **não nos benefícios brutos $g$**. Tampouco a mera
doação igual de TVs demonstra ortopolidade entre classes de renda.

## 3. Cem milhões de TVs e um único dono de fábrica

Fixamos $N=100\,000\,000$, $p=\text{R\$ }2\,000$, $m=10\%$, $L=5$,
$f=1$ e $b=10$. O orçamento é R$ 200 bilhões; R$ 20 bilhões remuneram
os cinco grupos, com R$ 4 bilhões para cada nível. Os demais R$ 180 bilhões
constituem $C$. Os números exemplificam a estrutura, não margens comerciais
realistas.

| Grupo | Pessoas | Recebimento adicional por pessoa | Total adicional do grupo |
|---|---:|---:|---:|
| Demais cidadãos | 99.988.889 | R$ 0 | R$ 0 |
| Vendedores | 10.000 | R$ 400 mil | R$ 4 bilhões |
| Gerentes | 1.000 | R$ 4 milhões | R$ 4 bilhões |
| Donos de lojas | 100 | R$ 40 milhões | R$ 4 bilhões |
| Donos de redes | 10 | R$ 400 milhões | R$ 4 bilhões |
| Dono da fábrica | 1 | R$ 4 bilhões | R$ 4 bilhões |

Todos recebem, além desses valores, uma TV. O dono da fábrica recebe
20% de $M$, equivalentes a 2% da encomenda total. Seu recebimento adicional
é o lucro atribuído ao seu nível, não a receita de R$ 200 bilhões. Seu
benefício bruto contabilizado é R$ 4.000.002.000, ou 2.000.001 vezes o
benefício de um cidadão que recebe apenas a TV.

É possível definir outras partilhas $a_j$, inclusive concentração maior no
último nível. Nesse caso pode haver mais desigualdade individual, mas
$n_jy_j=Ma_j$ deixa de ser constante: a igualdade ortopólica discreta entre
níveis já não se mantém. A desigualdade e a ortopolidade são propriedades
distintas, e devem ser mostradas separadamente.

## 4. Desigualdade de qual distribuição?

Para valores não negativos $x_i$ de média positiva, o índice de Gini é

$$G(x)=\frac{\sum_i\sum_k|x_i-x_k|}{2N\sum_i x_i}.$$

Na versão agrupada, cada diferença $|x_r-x_s|$ recebe peso $n_rn_s$;
isso permite calcular o índice sem gerar cem milhões de registros.
Com $g_i=p+y_i$, as diferenças absolutas não mudam, mas a média aumenta:

$$G(g)=\frac{M}{Np+M}G(y)=\frac{m}{1+m}G(y).$$

No cenário da tabela,

$$G(y)=0{,}999972842,\qquad G(g)=0{,}090906622.$$

A renda adicional é extremamente concentrada; o Gini do benefício bruto é
menor porque todos recebem um aparelho de mesmo valor. A razão entre os
extremos e o Gini respondem a perguntas diferentes. Para $m=0$, todos os
benefícios brutos são iguais e $G(g)=0$; $G(y)$ é indefinido porque todos os
recebimentos adicionais são zero.

Se o financiamento for um imposto uniforme imediato de $p$ por cidadão,
o saldo individual **desta conta parcial** será $g_i-p=y_i$. A troca de
indicador remove o componente comum, mas não altera quem recebe os
pagamentos da cadeia. Isso não constitui uma estimativa de bem-estar ou
incidência fiscal completa: os custos reais, seus recebedores, a tributação
efetiva, o patrimônio anterior e os usos alternativos do gasto também
importam.

O modelo estabelece desigualdade dos recebimentos incrementais. Para
afirmar aumento da desigualdade patrimonial final, é necessário especificar
o patrimônio inicial e todas as demais variações. Sob saldos iniciais
iguais e nenhum outro fluxo no recorte, acrescentar $y_i$ distintos produz
desigualdade; sob saldos iniciais diferentes, o sinal da mudança no índice
de desigualdade não é garantido.

## 5. Variações que a interface pode testar

- Multiplicar $p$ por um fator multiplica $B$, $M$ e todos os recebimentos
  pelo mesmo fator, sem alterar o Gini ou as razões entre recebimentos.
- Aumentar o número $f$ de proprietários finais, mantendo $b$, $N$, $p$ e
  $m$, multiplica todos os grupos por esse fator e divide seus recebimentos
  individuais por ele. A verba de cada nível permanece constante, enquanto
  houver cidadãos suficientes para grupos disjuntos.
- Aumentar $m$ amplia os pagamentos selecionados e reduz $C$. Com a
  estrutura e a partilha fixas, $G(y)$ não muda para $m>0$, mas
  $G(g)=mG(y)/(1+m)$ aumenta.
- Alterar as frações $a_j$ altera a distribuição de recurso entre os níveis;
  a interface pode mostrar simultaneamente o recebimento por pessoa e a
  verba total de cada nível, evidenciando se a igualdade entre níveis existe.

Essas relações são consequências verificáveis das hipóteses fixadas, e
servem para testar o cálculo da interface. Não são previsões empíricas
independentes. Um teste real precisaria fixar população, preço, custos,
propriedade, remunerações e financiamento antes de observar o resultado,
e avaliar outra previsão em dados separados. O exemplo respeita a
[distinção entre demonstração e conclusão social](not-worth-pursuing.md):
não extrai do espectro uma avaliação moral ou uma recomendação de política.
