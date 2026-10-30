T = dict(
id='w13', week=13, tab='When DL fails', title='When deep learning for robotic vision fails',
lead='Distribution shift and open-set inputs, why softmax confidence misleads, calibration and temperature scaling, aleatoric vs epistemic uncertainty, OOD detection, and turning all of this into safe robot decisions (selective prediction).',
docs=[dict(path='notes/Week13.pdf', title='Week 13 lecture: When deep learning fails', pages=52),
      dict(path='notes/papers/Kendall-Gal-Uncertainty.pdf', title='Kendall & Gal, What uncertainties do we need? (NeurIPS 2017)', pages=12)],
prac=None,
eli5=[
 ('Calibration', 'A weather forecaster is calibrated if it really rains on 70% of the days they say “70%”. Many networks are over-confident forecasters.', None),
 ('Aleatoric vs epistemic', 'Aleatoric: the photo itself is blurry, and no amount of studying fixes that. Epistemic: you never saw this kind of photo in class, and more study (data) would fix it.', None),
 ('OOD', 'A dog classifier shown a toaster still has to pick a dog breed. OOD detection asks “does this even look like my training data?”', None),
 ('Selective prediction', 'A good student may skip the questions they would probably get wrong. Answering fewer (lower coverage) can mean being wrong less often (lower risk).', None),
],
svg='''<svg class="dg" viewBox="0 0 520 200" role="img" aria-label="Reliability diagram: accuracy against confidence; points below the diagonal are overconfident">
<g transform="translate(40,15)">
<path class="ln" d="M0 0 V160 H200"/><path class="ln dash" d="M0 160 L200 0" style="stroke:var(--muted)"/>
<text x="60" y="185" class="sm">confidence</text><text x="-30" y="8" class="sm">acc.</text>
''' + ''.join(f'<rect class="sk" x="{i*20+2}" y="{160-h}" width="16" height="{h}"/>' for i,h in enumerate([10,20,30,40,50,62,72,86,100,118])) + '''
<text x="120" y="60" class="sm">gap = over-confidence</text>
</g>
<g transform="translate(300,20)">
<text x="0" y="10">Practice Q38</text>
<text x="0" y="34" class="sm">bin: mean confidence 0.60</text>
<text x="0" y="52" class="sm">8 of 10 correct → accuracy 0.80</text>
<text x="0" y="70" class="sm">accuracy &gt; confidence</text>
<text x="0" y="88">→ under-confident by 0.20</text>
<text x="0" y="122" class="sm">Bars under the diagonal (left plot)</text>
<text x="0" y="140" class="sm">= accuracy below confidence</text>
<text x="0" y="158" class="sm">= over-confident (typical of modern nets)</text>
</g></svg>''',
svgcap='Reliability diagram: bin predictions by confidence and plot accuracy per bin. On the diagonal = calibrated; below = over-confident; above = under-confident.',
videos=['AunotauS5yI', 'Osju20L6Z3I'],
body=r'''
<div class="sub"><h3>1. The problem: closed-set training, open-world deployment</h3>
<p>Mistakes range from annoying to life-threatening [[p4]]. Models are trained under closed-set conditions and deployed under open-set / OOD conditions [[p5]]. The typical failure is that <b>unknown objects are confidently misclassified as a known class</b> [[p8]].</p>
<p><b>Definitions</b> [[p10]]: <b>OOD</b> means the input comes from a different distribution (where \(p_{train}(x)\) is tiny or zero); <b>open-set recognition</b> means unseen classes appear at test time and should be recognised as unknown; <b>open-world</b> recognition also learns those new classes over time. An OOD input need not be a new class: a known class in heavy fog, or seen by a new sensor, is OOD too.</p>
<p>Assumption: \(p_{train}(x,y) = p_{deploy}(x,y)\) [[p11]]. The types of <b>shift</b> [[p12]]:</p>
<div class="tw"><table><tr><th>Shift</th><th>What changes</th><th>Example</th></tr>
<tr><td>covariate</td><td>\(p(x)\) changes, \(p(y|x)\) same</td><td>lighting, weather, camera, corruption</td></tr>
<tr><td>label / prior</td><td>\(p(y)\) changes, \(p(x|y)\) same</td><td>some classes become much more common</td></tr>
<tr><td>concept</td><td>\(p(y|x)\) changes</td><td>the meaning of an appearance changes</td></tr>
<tr><td>novel classes (open set)</td><td>\(p_{train}(x,y^*)=0\), \(p_{deploy}&gt;0\)</td><td>a new object type</td></tr></table></div>
<p>Confidence feeds downstream decisions (fusion, trust, fallback, weighting in estimation), so miscalibration makes those decisions systematically wrong [[p13]]. Three different questions [[p14]]: <b>failure / risk estimation</b> (“should the robot trust this prediction?”, decision-centric), <b>OOD detection</b> (“how unfamiliar is the input?”, data-centric), <b>uncertainty estimation</b> (“how unsure is the model?”, model-centric).</p></div>

<div class="sub"><h3>2. Confidence and calibration</h3>
<p>Softmax outputs look like probabilities but carry no guarantee [[p17]]. <b>Calibrated</b>: n% of predictions made with n% confidence are correct [[p18]]. Reliability diagram [[p19]]: store correctness and confidence, bin confidences (e.g. 10 bins), plot mean accuracy per bin. Modern networks are often accurate but poorly calibrated, usually over-confident [[p20]].</p>
<div class="ex"><b>Worked example (practice Q38).</b> A bin of 10 predictions with mean confidence 0.60; 8 correct → accuracy 0.80 &gt; 0.60 → <b>under-confident by 0.20</b>. A bin at confidence 0.90 with 70/100 correct → over-confident by 0.20.</div>
<div class="widget" data-w="calib"></div>
<p class="note">Expected calibration error (not on the slides, but standard): ECE = Σ (n_b/N)·|acc_b − conf_b|. Bins (conf 0.95, acc 0.80, n 40), (0.75, 0.70, 30), (0.55, 0.60, 30) give ECE = 0.4·0.15 + 0.3·0.05 + 0.3·0.05 = 0.09.</p>
<p><b>Temperature scaling</b> [[p21]]: \(p_i = \frac{e^{z_i/T}}{\sum_j e^{z_j/T}}\), with one scalar T learned on <b>held-out validation</b> data. T &gt; 1 softens over-confident predictions; T &lt; 1 sharpens. All logits are scaled equally, so the <b>predicted class never changes</b>. It is cheap, but calibration fitted in-distribution may not hold under shift.</p>
<div class="ex"><b>Worked example.</b> Logits (2, 1, 0): T = 1 → (0.665, 0.245, 0.090); T = 2 → (0.506, 0.307, 0.186). The argmax is still class 1, and the entropy rises from 0.83 to 1.02 nats.</div>
<div class="widget" data-w="temp"></div>
<p>Confidence is the simplest signal [[p22]]: maximum softmax probability or detector score, rejecting low maximum confidence or high entropy. It is surprisingly good, but networks can still be confidently wrong under shift, and even calibrated confidence is <b>not a reliable OOD detector</b>.</p></div>

<div class="sub"><h3>3. Uncertainty: aleatoric and epistemic</h3>
<div class="tw"><table><tr><th>Epistemic</th><th>Aleatoric</th></tr><tr><td>lack of knowledge (model uncertainty)</td><td>noise inherent in the observations</td></tr><tr><td><b>reduced by more data</b></td><td><b>not</b> reduced by more data</td></tr><tr><td>high on unfamiliar inputs</td><td>high on boundaries, distant objects, featureless surfaces</td></tr></table></div>
<p class="note">Definitions from [[p30]] (Kendall & Gal).</p>
<p><b>Learning aleatoric uncertainty</b> [[p31]]: the network predicts \(\hat x_i\) and \(\sigma_i^2\) with loss \(\mathcal L = \frac1D\sum_i\frac{\|x_i-\hat x_i\|^2}{2\sigma_i^2} + \frac12\log\sigma_i^2\). A large σ down-weights the error, but the log term penalises claiming large σ everywhere.</p>
<p><b>Estimating uncertainty</b> [[p32]]–[[p35]]: <b>predictive entropy</b> \(H(p) = -\sum_c p_c\log p_c\) (high = spread out); <b>deep ensembles</b> (train several models from different initialisations, average; their disagreement captures epistemic uncertainty); <b>MC dropout</b> (keep dropout on at test time, run many passes; the spread measures uncertainty). Uncertainty can be high even for an ambiguous <i>in-distribution</i> image.</p></div>

<div class="sub"><h3>4. Out-of-distribution detection</h3>
<p>OOD detection is <b>input-centric</b>: is this input atypical relative to the training data [[p38]]? Ideas [[p39]] [[p40]]: the max-softmax baseline (low max → maybe unfamiliar, but it can be confidently wrong); <b>feature-space distance</b> to training examples or class prototypes; the <b>energy score</b> \(E(x) = -\log\sum_c \exp z_c(x)\) on raw logits. Softmax discards the absolute logit scale, so two inputs can have the same softmax confidence but very different energy; low energy means strong evidence for known classes.</p>
<div class="ex"><b>Worked example.</b> Logits (2, 1, 0) and (6, 5, 4) give the <i>same</i> softmax, but energies of −2.41 and −6.41. The second input has much stronger evidence and is more in-distribution.</div>
<p><b>OOD ≠ failure</b> [[p41]]: an OOD input can still be classified correctly, an in-distribution input can be wrong, and high uncertainty, OOD-ness and failure are related but not the same.</p></div>

<div class="sub"><h3>5. Decision making</h3>
<p>Perception gives a prediction plus confidence, uncertainty and OOD signals → an estimated risk → an action [[p43]]. When reliability is <b>low</b>: abstain, fall back to safe behaviour, ask a human, stop or defer; if it persists, collect data and retrain. When it is <b>uncertain</b>: slow down, take another observation, change viewpoint, use temporal evidence, consult another sensor or model. When it is <b>high</b>: act normally [[p44]]. <i>Uncertainty is only useful if it changes behaviour.</i></p>
<p><b>Selective prediction</b> [[p45]] [[p46]]: if \(r(x) &lt; \tau\), predict; else abstain. <b>Coverage</b> = the fraction of inputs predicted on; <b>(selective) risk</b> = the error rate on accepted predictions. Lowering coverage can lower risk (the risk–coverage curve).</p>
<div class="ex"><b>Worked example (practice Q39).</b> 50 inputs, 10 abstained, 40 predictions, 4 wrong → coverage 40/50 = <b>0.80</b>, selective risk 4/40 = <b>0.10</b>. (Not 4/50 = 0.08: risk is measured on accepted predictions only.)</div>
<div class="widget" data-w="selective"></div>
<p><b>There is no universal threshold</b> [[p47]]: it depends on the consequence and reversibility of a failure, whether more information is available, time constraints and the ability to recover. Warehouse classification: accept moderate uncertainty. Grasping: take another view or replan. Obstacle detection: favour high recall. Autonomous driving: slow down, stop or hand over.</p>
<div class="exam"><b>Exam angle.</b> Five practice questions: Q27 (lower the threshold → fewer misses, more false stops), Q28 (aggregate accuracy hides rare hazards and latency), Q38 (reliability bin), Q39 (coverage and risk), Q40 (don’t tune on the test set). Expect paper-excerpt questions with uncertainty tables like Kendall & Gal’s Table 3.</div></div>
''',
paper=dict(title='What Uncertainties Do We Need in Bayesian Deep Learning for Computer Vision? (Kendall & Gal, NeurIPS 2017)', sixty=r'''
<p><b>Problem.</b> Vision networks give no sense of when they’re wrong. Which uncertainty should we model? <b>Epistemic</b> (model; explained away by data) or <b>aleatoric</b> (observation noise; homoscedastic = constant, heteroscedastic = input-dependent) [[P:p2]].</p>
<p><b>Key ideas.</b> <b>MC dropout</b> for epistemic uncertainty: keep dropout at test time, sample T stochastic passes (they used 50), and the spread is the uncertainty (approximate variational inference). <b>Heteroscedastic aleatoric</b>: the network outputs σ² and uses \(\frac1D\sum\tfrac12 e^{-s_i}\|y_i-\hat y_i\|^2 + \tfrac12 s_i\) with \(s = \log\sigma^2\), i.e. <b>learned loss attenuation</b> (like a robust loss). Noisy inputs get less weight, and the \(s\) term stops it predicting high uncertainty everywhere [[P:p5]]. Combining both gives state-of-the-art segmentation (CamVid, NYUv2) and depth (Make3D, NYUv2).</p>
<p><b>Headline evidence</b> (Table 3b [[P:p9]], segmentation; train → test, IoU, aleatoric entropy, epistemic variance ×10⁻³):</p>
<div class="tw"><table><tr><th>train</th><th>test</th><th>IoU</th><th>aleatoric</th><th>epistemic</th></tr>
<tr><td>CamVid/4</td><td>CamVid</td><td>57.2</td><td>0.106</td><td>1.96</td></tr><tr><td>CamVid/2</td><td>CamVid</td><td>62.9</td><td>0.156</td><td>1.66</td></tr><tr><td>CamVid</td><td>CamVid</td><td>67.5</td><td>0.111</td><td>1.36</td></tr>
<tr><td>CamVid/4</td><td>NYUv2</td><td>–</td><td>0.247</td><td>10.9</td></tr><tr><td>CamVid</td><td>NYUv2</td><td>–</td><td>0.264</td><td>11.8</td></tr></table></div>
<p><b>Reading it.</b> More training data → epistemic uncertainty <b>falls</b> (1.96 → 1.36) while aleatoric stays roughly flat (no trend). On OOD data (NYUv2 indoor, trained on CamVid streets), epistemic uncertainty <b>jumps about 5–9×</b>. The paper says aleatoric does not increase for out-of-data inputs; in this table it roughly doubles, a useful point if asked to critique the claim. Runtime: aleatoric is nearly free; MC dropout costs ~50× for 50 samples (Sec. 5.3).</p>''',
),
tut=r'''
<p><b>1. Aleatoric vs epistemic, with examples.</b> Aleatoric: sensor noise and inherent ambiguity, e.g. depth at object boundaries, a motion-blurred image, distant small pedestrians, reflective floors. Epistemic: lack of knowledge, e.g. a warehouse robot trained indoors driving outside at night, or a new type of forklift never seen in training.</p>
<p><b>2. Behaviour with more data.</b> Epistemic uncertainty falls as data covers the input space (the model becomes sure which function fits). Aleatoric uncertainty stays, because noise in the observation can’t be removed by more examples of the same noise. Table 3 confirms this: epistemic 1.96 → 1.36 as data grows ×4; aleatoric roughly constant.</p>
<p><b>3. Estimating epistemic uncertainty.</b> Bayesian NN approximated by <b>MC dropout</b>: dropout before every weight layer during training <i>and</i> at test time; T stochastic forward passes sample weights from the approximate posterior; the variance (or entropy) of the outputs is the epistemic uncertainty. At test time, dropout turns one network into an ensemble of thinned networks.</p>
<p><b>4. Heteroscedastic regression.</b> The network predicts a mean and a per-input variance and is trained with the Gaussian negative log-likelihood. The residual is divided by σ², so noisy inputs matter less (learned attenuation). The \(\tfrac12\log\sigma^2\) term grows with σ, so predicting huge uncertainty everywhere is penalised. Predicting tiny σ on a large residual is penalised too, through the first term.</p>
<p><b>5. Unfamiliar inputs.</b> Section 5.2 / Table 3: models trained on CamVid and tested on NYUv2 show much higher <b>epistemic</b> uncertainty, so epistemic is what flags situations never seen. The authors state aleatoric does not increase for out-of-data examples (although the table shows a moderate rise).</p>
<p><b>6. When each matters.</b> Aleatoric: large-data regimes (epistemic explained away) and <b>real-time</b> systems (no sampling cost). Epistemic: <b>safety-critical</b> systems (detecting novel situations) and <b>small datasets</b>.</p>
<p><b>Things to think about.</b> <i>Does high uncertainty mean OOD?</i> No: an ambiguous in-distribution image (blur, boundary) gives high aleatoric uncertainty. <i>Does OOD mean a wrong prediction?</i> No: a known class in fog may still be classified correctly. <i>What should the robot do?</i> Act on risk: slow down, take another view or sensor reading, abstain or hand over, log the data for retraining, with the action tied to the cost of failure.</p>''',
quiz=[
 ('Temperature scaling with T = 2 on an over-confident classifier…', ['changes the predicted class', 'softens probabilities without changing the argmax', 'sharpens probabilities', 'requires retraining the network'], 1, 'All logits are divided by T, so their order is preserved [[p21]].'),
 ('200 inputs, the system abstains on 50, and 12 of its predictions are wrong. Coverage and selective risk?', ['0.75 and 0.08', '0.75 and 0.06', '0.25 and 0.08', '0.75 and 0.24'], 0, 'Coverage 150/200 = 0.75; risk 12/150 = 0.08.'),
 ('Which uncertainty decreases as you collect more training data of the same kind?', ['Aleatoric', 'Epistemic', 'Both equally', 'Neither'], 1, 'Epistemic uncertainty is lack of knowledge and is explained away by data [[p30]].'),
],
)
