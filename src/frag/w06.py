T = dict(
id='w06', week=6, tab='Factor graphs & BA', title='Robust losses, pose graphs, bundle adjustment and factor graphs',
lead='How to fix drift: use more than consecutive measurements, weight them by confidence, and solve one big (sparse, nonlinear) least-squares problem, which turns out to be the MAP estimate of a factor graph.',
docs=[dict(path='notes/Week06.pdf', title='Week 6 lecture: Factor graphs and bundle adjustment', pages=110),
      dict(path='notes/papers/VO_Part_II.pdf', title='VO Part II (Fraundorfer & Scaramuzza, 2012)', pages=13),
      dict(path='notes/papers/VO_Part_I.pdf', title='VO Part I (Scaramuzza & Fraundorfer, 2011)', pages=13)],
prac=('week-6-pose-graphs.ipynb', 'selects keyframes on KITTI, adds between-pose factors for consecutive and longer-baseline VO estimates in SymForce, and optimises the pose graph (saved before/after trajectory outputs).'),
eli5=[
 ('Springs between poses', 'Picture each camera pose as a bead and each measurement as a spring that wants a certain gap between beads. Let go, and the beads settle where the total spring tension is lowest.', 'each between-pose factor in SymForce is one of these springs.'),
 ('Confidence = spring stiffness', 'A precise measurement is a stiff spring (small σ, big weight 1/σ²); a sloppy one is a floppy spring that gives way.', None),
 ('Robust losses', 'Huber and Tukey are springs that stop pulling harder once they are stretched absurdly far, so one crazy measurement can’t drag everything.', None),
 ('Bundle adjustment', 'Move both the cameras <i>and</i> the 3D points until every point lands exactly where it was seen in every photo.', None),
 ('MAP', 'Of all possible trajectories, pick the single most believable one. You lose the “how sure am I” information unless you also keep the spread.', None),
],
svg='''<svg class="dg" viewBox="0 0 520 170" role="img" aria-label="Factor graph: poses x0 to x3 as circles, odometry factors between consecutive poses, a loop factor between x0 and x3, and a prior on x0">
<g>
<path class="ln" d="M70 90 H450"/>
<path class="ev" d="M70 90 C150 10 370 10 450 90"/>
<circle class="bx" cx="70" cy="90" r="20"/><circle class="bx" cx="197" cy="90" r="20"/><circle class="bx" cx="323" cy="90" r="20"/><circle class="bx" cx="450" cy="90" r="20"/>
<text x="61" y="95">x0</text><text x="188" y="95">x1</text><text x="314" y="95">x2</text><text x="441" y="95">x3</text>
<rect class="fi" x="127" y="84" width="12" height="12"/><rect class="fi" x="254" y="84" width="12" height="12"/><rect class="fi" x="381" y="84" width="12" height="12"/>
<rect class="fe" x="254" y="24" width="12" height="12"/><rect class="fa" x="64" y="130" width="12" height="12"/><path class="ln" d="M70 110 V130"/>
<text x="118" y="122" class="sm">odometry factors</text><text x="275" y="22" class="sm">loop-closure factor</text><text x="84" y="143" class="sm">prior (fixes gauge)</text>
<text x="300" y="150" class="sm">○ variable  ■ factor (measurement)</text>
</g></svg>''',
svgcap='A pose graph as a factor graph: bipartite (every edge joins a variable to a factor) and undirected. Solving it means finding poses that best satisfy all factors at once, weighted by their covariances.',
videos=['uuiaqGLFYa4', 'lmj2Jk5tl60'],
body=r'''
<div class="sub"><h3>1. Robust objective functions (M-estimators)</h3>
<p>PTAM tracking optimises the pose with a <b>Tukey biweight</b> loss on reprojection errors [[p21]]. Squared error lets outliers dominate, so robust losses change how much each residual can pull on the solution (its “influence”) [[p22]] [[p23]] [[p24]]:</p>
<div class="tw"><table><tr><th>Category</th><th>Examples</th><th>Behaviour</th></tr>
<tr><td>unbounded influence</td><td>quadratic (least squares)</td><td>outliers can dominate; efficient for Gaussian noise; estimates the mean</td></tr>
<tr><td>bounded influence</td><td>L1, Huber, pseudo-Huber, Fair</td><td>limits outliers but never ignores them; L1 estimates the median; Huber is quadratic up to k (≈ 1.345σ), then linear</td></tr>
<tr><td>redescending</td><td>Tukey, Cauchy, Hampel, Welsch, Andrews</td><td>influence falls for increasingly extreme residuals</td></tr>
<tr><td>finite rejection point</td><td>Tukey (cut-off ≈ 4.685σ), Hampel, Andrews</td><td>beyond the cut-off, <b>zero</b> influence</td></tr></table></div></div>

<div class="sub"><h3>2. Pose-graph optimisation</h3>
<p>Relative motion can be estimated between <b>non-consecutive</b> frames too [[p33]]. Then \({}^{x_0}T_{x_1}\,{}^{x_1}T_{x_2} \ne {}^{x_0}T_{x_2}\) in general, and the measurements have different confidence [[p36]]. Solve for all poses together [[p39]]:</p>
\[X^* = \arg\min_X \sum_{i,j}\big\| x_i - {}^{i}T_j\,x_j \big\|^2_{\Sigma_{ij}}\]
<p>The variables are the poses \(\{R_i, t_i\}\); the prediction is \({}^{i}T_j x_j\); the residual is the pose difference (a difference between SE(3) elements, computed on the manifold, not a plain minus); the objective is a weighted sum of squares. Rotations make it <b>nonlinear</b>, so it needs Gauss–Newton or Levenberg–Marquardt.</p>
<div class="ex"><b>Worked example (1-D).</b> x0 = 0 is fixed. Odometry says x1 − x0 = 1 and x2 − x1 = 1; a loop closure says x2 − x0 = 1.8; all σ = 0.1. Minimise \((x_1-1)^2 + (x_2-x_1-1)^2 + (x_2-1.8)^2\). Setting the derivatives to zero gives \(2x_1 - x_2 = 0\) and \(-x_1 + 2x_2 = 2.8\), so <b>x1 = 0.933, x2 = 1.867</b>. The 0.2 disagreement is shared equally by the three equally weighted factors (each takes 0.067). Make the loop more precise in the widget and x2 moves towards 1.8.</div>
<div class="widget" data-w="posegraph"></div></div>

<div class="sub"><h3>3. Bundle adjustment</h3>
<p>The 3D points become variables too [[p40]] [[p42]]. BA minimises the reprojection error jointly over poses and landmarks:</p>
\[P^*, X^* = \arg\min_{P,X}\sum_{i,j}\big\|y^i_j - \pi(p_j, x_i, K)\big\|^2\]
<p>Here \(y^i_j\) is the image of landmark j seen by camera i [[p43]]. The graph grows over time, so a <b>sliding-window BA</b> optimises only the last n frames [[p45]].</p>
<div class="tw"><table><tr><th></th><th>Pose graph</th><th>(Windowed) bundle adjustment</th></tr>
<tr><td>Variables</td><td>camera poses only</td><td>camera poses <b>and</b> 3D landmarks</td></tr>
<tr><td>Measurements</td><td>relative-pose estimates between frames (VO, loop closures)</td><td>2D feature observations of landmarks</td></tr>
<tr><td>Error</td><td>pose-difference residual (Mahalanobis)</td><td>image reprojection error</td></tr>
<tr><td>Needs</td><td>relative-pose estimates with covariances</td><td>feature tracks across &gt; 2 frames</td></tr>
<tr><td>Cost</td><td>small, cheap</td><td>large; window size chosen for compute, \(O((qM+lN)^3)\)</td></tr></table></div></div>

<div class="sub"><h3>4. How the solver works</h3>
<p>For a simple function, set the derivative to zero: \(f(x)=3x^2+5(x+3)\) gives \(f'(x) = 6x+5 = 0\), so \(x = -5/6\) [[p48]]. Real problems have thousands of nonlinear, vector-valued terms, so we iterate [[p49]] [[p50]]. Start from a guess and step \(x \leftarrow x + \Delta x\):</p>
<ul><li>Gradient descent: step along \(-J^\top r\) (cautious, slow).</li>
<li>Gauss–Newton: \((J^\top J)\Delta x = -J^\top r\) (fast near the minimum).</li>
<li><b>Levenberg–Marquardt</b>: \((J^\top J + \lambda I)\Delta x = -J^\top r\), which <b>interpolates between Gauss–Newton and gradient descent</b> [[p52]].</li></ul>
<p>These are all <b>normal equations</b> \(A^\top A x = A^\top b\) [[p55]]. The Jacobian is <b>sparse</b>, because each measurement touches only a few variables (the factor-graph structure), so they solve efficiently [[p54]]. Spring–mass picture: the solution is the minimum-energy configuration [[p56]].</p>
<p><b>Keep in mind</b> [[p57]] [[p58]] [[p59]]: there can be several minima, and the solution <b>depends on the initial guess</b>, which must be close (practice Q24). Least squares is vulnerable to outliers. Tools: gtsam, Ceres, SymForce (autodiff Jacobians, since hand-written Jacobians are error-prone).</p></div>

<div class="sub"><h3>5. Factor graphs, probability and MAP</h3>
<p>We estimate hidden variables from measurements and priors and fuse sensors with different noise [[p63]] [[p64]]. A Gaussian has mean μ and variance σ² (in N-D, μ and Σ: an ellipse or ellipsoid) [[p68]] [[p69]]. Kalman example [[p71]]: the prediction after motion is broad, and the measurement pulls the posterior towards whichever input is more certain.</p>
<div class="ex"><b>Worked example (fusion).</b> Prior N(5, 1²) and measurement N(6, 0.5²). The weights are 1/σ²: 1 and 4. Posterior mean = (5·1 + 6·4)/5 = <b>5.8</b>; variance = 1/5 = 0.2 (σ ≈ 0.45), smaller than either input.</div>
<div class="widget" data-w="fusion"></div>
<p>Notation [[p72]]: p(x) prior, p(x|u) prediction, p(x|u,z) posterior, p(z|x) <b>measurement likelihood = sensor model</b>. Smoothing asks for \(p(x_0..x_t|u,z)\); filtering asks for \(p(x_t|u,z)\) or recursively \(p(x_t|x_{t-1},u_{t-1},z_t)\) [[p84]].</p>
<p><b>Factor graph</b> [[p74]] [[p75]]: variable nodes (unknowns) and factor nodes (probabilistic constraints from measurements or priors). It is <b>bipartite</b> (every edge joins a variable to a factor) and <b>undirected</b>. Examples [[p77]] [[p79]] [[p81]] [[p82]]: GPS unary factors, VO binary factors, pose-graph SLAM with a loop closure, SLAM with landmarks, BA. The factors are the terms of the factorised joint distribution, \(\prod_i p(x_i|x_{i-1},u_{i-1})\prod_j p(x_j|z_j)\) [[p86]].</p>
<p><b>MAP vs the full distribution</b> [[p89]] [[p90]]: \(x^* = \arg\max p(x|\ldots)\) is easier to compute, but you lose the uncertainty. The full distribution keeps mean and variance. Two posteriors with the same MAP can have very different spreads, and so warrant different decisions (practice Q25).</p>
<p><b>The derivation</b> [[p97]]–[[p106]]: assume Gaussian factors, \(p \propto \exp\!\big(-\tfrac12 e^\top\Sigma^{-1}e\big)\) with \(e = x_i - {}^{i}T_j x_j\). Drop the constant; take the log (monotonic, so the argmax is unchanged, and products become sums); flip the sign and maximise → minimise:</p>
\[X^* = \arg\min_X\sum_{i,j}\|e_{ij}\|^2_{\Sigma_{ij}},\qquad \|e\|^2_\Sigma = e^\top\Sigma^{-1}e\ \ (\text{Mahalanobis distance})\]
<p><b>MAP estimation of a Gaussian factor graph = weighted nonlinear least squares.</b></p>
<div class="ex"><b>Worked example (practice Q23).</b> Same residual r, σ_A = 0.5, σ_B = 1.0. Contributions \((r/0.5)^2 = 4r^2\) vs \(r^2\), so <b>A contributes 4×</b>. Halving σ quadruples the weight.</div>
<div class="exam"><b>Exam angle.</b> Q22 (the pose graph balances weighted residuals instead of forcing measurements to agree), Q23 (the 1/σ² weight ratio), Q24 (initialisation), Q25 (MAP vs spread). Likely written questions: pose graph vs BA (variables, measurements, error), and why squared loss fails with outliers.</div></div>
''',
paper=dict(title='VO Part II: pose-graph optimisation and windowed BA (pp. 8–9)', sixty=r'''
<p><b>Camera pose optimisation</b> [[P:p8]]: besides \(T_{k,k-1}\), estimate \(T_{k,k-2},\ldots,T_{k,k-n}\) or any \(T_{ij}\) when frames overlap, and add them as constraints.</p>
<p><b>Pose graph</b> [[P:p9]]: nodes = camera poses, edges = rigid transforms. Cost \(\sum_{e_{ij}}\|C_i - T_{e_{ij}}C_j\|^2\). The rotation part makes it nonlinear, so the paper suggests <b>Levenberg–Marquardt</b>. Loop constraints connect far-apart nodes; they are found by visual similarity (bag of visual words), verified with the epipolar constraint, and then a rigid transform is added.</p>
<p><b>Windowed BA</b>: optimises poses <b>and 3D landmarks</b> over n frames by minimising reprojection error \(\sum\|p_k^i - g(X_i, C_k)\|^2\). It needs feature tracks over more than 2 frames and an initialisation near the minimum (two-view VO). Window size is governed by <b>computation</b>. It reduces drift compared with two-view VO.</p>
<p><b>VO vs V-SLAM</b> (Part I [[P2:p4]]): VO keeps <i>local</i> consistency; SLAM keeps <i>global</i> consistency and needs loop closure, i.e. recognising a revisited place and then correcting both map and path.</p>''',
),
tut=r'''
<p><b>From pairwise motion to refinement.</b> \(C_k = C_{k-1}T_k\). By first-order error propagation \(\Sigma_k = J_C\Sigma_{k-1}J_C^\top + J_T\Sigma_{k,k-1}J_T^\top\), so uncertainty only grows. Small rotation errors swing every later translation, which is why a 0.5° heading error becomes metres of drift after hundreds of metres.</p>
<p><b>Non-consecutive frames.</b> Each extra estimate \(T_{k,k-n}\) becomes an extra <b>edge</b> (factor) between non-adjacent nodes. That over-determines the poses, so errors in one edge can be corrected by the others. The frames must share enough visual content (overlapping view, enough common features with good parallax) for a reliable estimate.</p>
<p><b>Building the graph.</b> Nodes are camera poses; edges are relative-pose measurements with their uncertainty. The optimisation adjusts the <b>poses</b>, and the measurements stay fixed. The error is the difference between each measured relative transform and the one implied by the current poses (Mahalanobis-weighted). It is nonlinear because of rotations; the paper suggests Levenberg–Marquardt.</p>
<p><b>Uncertainty and outliers.</b> A bad relative transform corrupts every later accumulated pose; weighting each edge by its covariance limits the damage from uncertain ones. Non-consecutive pairs have a wider baseline and more appearance change, so mismatches are more likely, and a wrong edge in a least-squares graph pulls everything. Reject outlier matches (RANSAC) before estimating the edge, and use robust losses or switchable constraints for wrong loop edges.</p>
<p><b>Pose graph vs BA.</b> PGO: variables = poses; measurements = relative transforms; error = pose residual. BA: variables = poses + landmarks; measurements = 2D observations; error = reprojection error. BA needs tracks over more than two frames, otherwise a landmark is constrained by only one pair and adds nothing beyond two-view geometry. Window size is set by the computation budget.</p>
<p><b>VO or SLAM?</b> VO keeps the trajectory locally consistent; SLAM keeps it <b>globally</b> consistent, which needs detecting a return to a known place (loop closure), geometric verification, adding a loop constraint and re-optimising the whole graph (often followed by global BA).</p>''',
quiz=[
 ('Factor A has σ = 0.2 and factor B σ = 0.4, with the same residual. In weighted least squares, A contributes…', ['2× B', '4× B', '½ of B', 'the same as B'], 1, '(r/0.2)² ÷ (r/0.4)² = 4.'),
 ('Which robust loss gives exactly zero influence to residuals beyond a cut-off?', ['Quadratic', 'Huber', 'L1', 'Tukey biweight'], 3, 'Tukey has a finite rejection point; Huber and L1 have bounded but non-zero influence [[p23]].'),
 ('Compared with pose-graph optimisation, bundle adjustment additionally estimates…', ['camera intrinsics only', '3D landmark positions, using reprojection error', 'IMU biases', 'nothing, they are identical'], 1, 'BA optimises poses and landmarks jointly by minimising reprojection error [[p42]].'),
],
)
