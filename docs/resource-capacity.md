# Resource capacity, nested boxes, and complete hierarchies

Completed 8 October 2026.

This note develops the geometric foundation of orthopolity: more resource per
unit permits fewer units within a given budget. It supplies exact statements
for capacity, complete partitions and overlapping descriptions, then connects
them to the allocation formulation in [the article](paper.md).
The mathematics uses established additive accounting. Its role here is to
identify the core that can be proved and the physical conditions under which
that core predicts observed incidence.

## 1. The finite-resource capacity theorem

Let a finite inventory have positive resource requirements $q_1,\ldots,q_N$,
accounted without duplication, and let $\sum_iq_i\le B<\infty$. For $t>0$,
define $N_{\ge t}=\#\{i:q_i\ge t\}$. Then

$$N_{\ge t}\le\left\lfloor\frac Bt\right\rfloor.$$

**Proof.** Each counted unit uses at least $t$, so
$tN_{\ge t}\le\sum_{q_i\ge t}q_i\le B$. The count is an integer.
The bound is sharp in the unrestricted additive-budget model, or whenever
$\lfloor B/t\rfloor$ units of resource $t$ are jointly feasible.
Feasibility restrictions may
lower the achievable count. This is an upper bound on realized incidence,
not an assertion that every admissible inventory saturates it.

For identical units the relation reduces to $Nq\le B$. Complete use gives
$N=B/q$ when indivisibility and other restrictions permit equality.
The resource can be volume, material mass, storage, or accumulated occupancy
over a stated observation interval. Positivity and additive accounting are
the assumptions; a particular dynamics is not needed.

A related identity is

$$\sum_iq_i=\int_0^\infty N_{>t}\,dt.$$

It follows by integrating $q_i=\int_0^\infty\mathbf1_{\{t<q_i\}}\,dt$
and exchanging a finite sum and integral. If a continuum approximation has
$N_{>t}=C/t$ on $[a,b]$, that interval alone contributes $C\ln(b/a)$.
Such a profile cannot extend through an unbounded logarithmic range with
finite additive resource. This connects the elementary capacity argument
to the finite-domain requirement in the paper.

## 2. Boxes and the difference between capacity and an inventory

Consider a cube of side $L$ in $d$ dimensions, with volume $B=L^d$.
For $\ell=L/m$ and integer $m\ge1$, an aligned tiling by cubes of side
$\ell$ has

$$N=m^d,\qquad q=\ell^d,\qquad Nq=L^d.$$

The volume bound proves optimality for this exact tiling. For arbitrary
$0<\ell\le L$, an aligned grid gives $\lfloor L/\ell\rfloor^d$ cubes,
while any nonoverlapping packing obeys $N\ell^d\le L^d$.
No claim about a general optimal packing algorithm is needed.
For this grid, its occupied volume fraction is

$$\phi(\ell)=\left(\frac{\ell\lfloor L/\ell\rfloor}{L}\right)^d,\qquad
N=\phi(\ell)\frac{L^d}{\ell^d}.$$

The inverse-volume factor and the boundary loss are now separately explicit.
For a physical population, occupancy may also depend on access, interactions,
formation, survival and observation time. Those conditions determine how
much of the capacity is used.

A completely filled mixed-size inventory illustrates the distinction.
Tile a unit cube with $4^3=64$ equal cubes and subdivide just one into eight:

| Size class | Count | Volume per unit | Total class volume |
|---|---:|---:|---:|
| Side $1/4$ | 63 | $1/64$ | $63/64$ |
| Side $1/8$ | 8 | $1/512$ | $1/64$ |

The final objects are disjoint and exhaust the volume. The construction
assigns unequal budgets to its two size classes, so their counts follow
different occupancy fractions. This is a precise example of how construction
affects incidence. It also specifies the premise needed to transfer the
capacity relation to a neutral distribution: comparable classes must receive
comparable resource allocations.

## 3. The coverage and complete-hierarchy theorem

Let $(\Omega,\nu)$ be a finite nonnegative resource measure with
$B=\nu(\Omega)>0$. The physical measure $\nu$ is different from the
comparison measure $\mu$ over classes in the article.
At level $j$, take a nonempty finite collection of measurable units $A_{ji}\subseteq\Omega$
of positive resource. Define

$$q_{ji}=\nu(A_{ji}),\qquad
\bar q_j=\frac1{N_j}\sum_iq_{ji},\qquad
m_j(x)=\sum_i\mathbf1_{A_{ji}}(x).$$

**Theorem.** The following identity holds for every such collection:

$$N_j\bar q_j=\int_\Omega m_j(x)\,d\nu(x)=B\gamma_j,\qquad
\gamma_j=\frac1B\int_\Omega m_j(x)\,d\nu(x).$$

If each level is a complete partition up to sets of zero resource, then

$$N_j\bar q_j=B,\qquad
\frac{N_j}{N_h}=\frac{\bar q_h}{\bar q_j}.$$

**Proof.** Integrate the finite sum defining $m_j$. For a complete
partition, every resource element belongs to exactly one set at that level,
so $m_j=1$ almost everywhere. The result follows at every level; dividing
the two equalities gives the ratio. The units within a level need not have
equal resource. Refinement or nesting between levels is permitted but is
not required for the result.

For a unit cube subdivided into eight subcubes at each step:

| Level $j$ | Side | Number $N_j$ | Unit volume $q_j$ | Level total |
|---|---:|---:|---:|---:|
| 0 | 1 | 1 | 1 | 1 |
| 1 | $1/2$ | 8 | $1/8$ | 1 |
| 2 | $1/4$ | 64 | $1/64$ | 1 |
| $j$ | $2^{-j}$ | $8^j$ | $8^{-j}$ | 1 |

Nesting therefore gives an exact instance of equal resource across
complete levels, and inverse resource per unit. The comparison levels
are defined by the partition before any abundance fit. Constant-ratio
refinement makes the level index proportional to logarithmic size.
These are discrete levels; a smooth density requires a further continuum
approximation. Under that approximation, counts per logarithmic length
interval proportional to $\ell^{-d}$ correspond to a density with respect
to $d\ell$ proportional to $\ell^{-(d+1)}$.

The resource is represented repeatedly across levels. Including $J$
complete levels gives assigned total $JB$, while the underlying physical
resource remains $B$. This is legitimate hierarchical accounting. It does
not describe $J$ disjoint budgets shared by a mixed-size population.
For hollow boxes, enclosed space overlaps across nesting; the material in
their walls is a different resource with its own disjoint accounting.

## 4. Quantitative corrections for missing coverage and reuse

Define uncovered fraction and excess multiplicity by

$$g_j=\frac{\nu(\{x:m_j(x)=0\})}{B},\qquad
o_j=\frac1B\int_\Omega(m_j(x)-1)_+\,d\nu(x).$$

Because integer-valued $m_j=\mathbf1_{\{m_j>0\}}+(m_j-1)_+$,

$$\gamma_j=1-g_j+o_j,\qquad
N_j\bar q_j=B(1-g_j+o_j).$$

For two nonempty levels the resulting prediction is

$$\frac{N_j}{N_h}
=\frac{\bar q_h}{\bar q_j}
\frac{1-g_j+o_j}{1-g_h+o_h}.$$

Incomplete disjoint coverage has $o_j=0$. Complete overlapping coverage
has $g_j=0$. A pointwise bound $m_j\le M$ gives the threshold bound
$N_{j,\ge t}\le\lfloor MB/t\rfloor$ by the same argument as Section 1.
Arbitrary repeated copies with no overlap bound can have arbitrarily
large counts while enclosing the same physical volume.

Coverage and overlap can be determined from independently specified geometry.
In that setting they supply a quantitative correction rather than a residual
named after observing an abundance curve. If they are computed solely from
the same count/resource accounting being compared, the relation is a
consistency identity; it provides no independent forecast.

## 5. A restriction on nonlinear effective resources

Suppose constituent resource measures $\nu_1,\ldots,\nu_m$ are additive.
Use fixed reference scales $s_\ell>0$ and assign

$$Q(A)=Q_0F(\mathbf x(A)),\qquad
x_\ell(A)=\nu_\ell(A)/s_\ell.$$

At a fixed physical object partition, any specified positive $F$ can define
an effective quantity whose object values are summed. To use the same
quantity at every resolution, a further condition is needed.

**Proportional subdivision.** If $F(c\mathbf x)=c^hF(\mathbf x)$,
then splitting a parent into $r$ identical proportional constituent vectors
gives

$$\sum_{i=1}^rQ(A_i)
=rQ_0F(\mathbf x/r)=r^{1-h}Q_0F(\mathbf x).$$

For a positive parent and $r>1$, invariance requires $h=1$.
A product $F(\mathbf x)=\prod_\ell x_\ell^{\theta_\ell}$ has
$h=\sum_\ell\theta_\ell$. This supplies an exact restriction on applying
that product unchanged across complete proportional subdivisions.

**Arbitrary subdivision.** Assume every vector in $\mathbb R_+^m$
and every split into two such vectors are admissible, $F$ is finite and
nonnegative there, and $F(0)=0$. Invariance under every split or merge is
equivalent to

$$F(\mathbf x+\mathbf y)=F(\mathbf x)+F(\mathbf y).$$

It forces

$$F(\mathbf x)=\sum_{\ell=1}^m c_\ell x_\ell,\qquad c_\ell\ge0.$$

**Proof.** Additivity gives $F(\mathbf x)=\sum_\ell F(x_\ell\mathbf e_\ell)$.
For each axis $g_\ell(t)=F(t\mathbf e_\ell)$ is additive and nonnegative.
It is monotone since $g_\ell(t+s)-g_\ell(t)=g_\ell(s)\ge0$.
Rational arguments give $g_\ell(r)=r g_\ell(1)$; bounding a real argument
above and below by rationals gives $g_\ell(t)=t g_\ell(1)$.
Set $c_\ell=g_\ell(1)$.

Degree one is necessary but insufficient for arbitrary heterogeneous splits.
For $F(x,y)=\sqrt{xy}$, parents with vectors $(9,1)$ and $(1,9)$ each
contribute 3, while their merged vector $(10,10)$ contributes 10.
If attainable vectors are restricted to common constituent proportions,
a nonlinear homogeneous degree-one form can remain invariant on that
restricted family. The full-cone assumption must not be omitted.

This result preserves the programme's nonlinear resources while identifying
their physical domain. They can describe assembly-dependent requirements at
a specified object partition. Applying them across arbitrary partitions needs
additional interaction accounting or the additivity property above.
The restriction does not apply to the linguistic study merely because its
fitted product has a degree different from one: that study fixes word types
and makes no claim of invariance under arbitrary splitting and merging.

## 6. From exact geometry to the general natural-law claim

Three statements now have explicit roles:

| Statement | What establishes it | What remains to be determined |
|---|---|---|
| Inverse resource-capacity bound | A finite positive additive budget | Which feasible units occur and how fully capacity is used |
| Exact equality across complete levels | Each level accounts for the same resource once | Whether the observed units form such complete descriptions |
| Equal allocation among coexisting classes | A specified physical condition, symmetry, dynamics or empirical regularity | The domain and predictive accuracy of that condition |

The first two statements are the exact mathematical foundation. The third
is the general physical extension advanced by orthopolity. For disjoint
mixed classes, independently characterized fractions $f_j$ yield
$N_j\bar q_j=Bf_j$ with $\sum_jf_j\le1$. Equal $f_j$ gives the neutral
inverse-cost form for equally weighted classes. For unequal class comparison
weights $w_j$, neutrality instead means $f_j$ proportional to $w_j$.
The [exchange mechanism](class-exchange.md) supplies one dynamical route
to that allocation, including a quantified departure and recovery.

The simple foundation can organize a substantial scientific contribution
through physical identification and transferable predictions. Its elementary
proof does not make all proposed empirical extensions established, nor does
it claim the underlying accounting mathematics as a new discovery.

## Established mathematical foundations

Additivity, indicator integrals and their extension to nonnegative sums are
standard measure theory; see [Tao, *An Introduction to Measure Theory*
(2011), Exercise 1.4.34](https://terrytao.wordpress.com/wp-content/uploads/2012/12/gsm-126-tao5-measure-book.pdf).
The arguments above are supplied directly so that their assumptions are visible.

Covering counts and geometric scaling have an established theory; see
[Bishop and Peres, *Fractals in Probability and Analysis*
(2017), Section 1.1](https://www.math.stonybrook.edu/~bishop/fractalbook.pdf).
Existence of a box dimension $D$ gives a logarithmic scaling limit, commonly
written $N(\epsilon)=\epsilon^{-D+o(1)}$ in normalized units. It does not
by itself imply an exact constant $N(\epsilon)\epsilon^D$.
The exact equalities here follow from the declared complete resource partitions.
