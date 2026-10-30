COUNTS = [('W2 Features & matching', 6, 'w02'), ('W3 Cameras & stereo', 4, 'w03'), ('W4 Epipolar & RANSAC', 3, 'w04'), ('W4/5 Scale & consensus', 3, 'w04'),
          ('W5 Visual odometry', 5, 'w05'), ('W6 Factor graphs & BA', 4, 'w06'), ('W8 Deep learning', 1, 'w08'), ('W9 Learned geometry & 3D', 2, 'w09'),
          ('W10 Object detection', 2, 'w10'), ('W11 Segmentation & grasping', 2, 'w11'), ('W12 Place recognition', 3, 'w12'), ('W13 When DL fails', 5, 'w13'),
          ('W1 Intro, W7 SLAM/VIO', 0, 'w07')]
DAYS = [
 ('d1', 'Fri 30 Oct', 'W1 Intro & images · W2 Features & matching · W3 Cameras & stereo', 'w01', 'Heavy on W2 (6 practice Qs) and W3. Work the W3 numeric tutorial (Q1–Q4) by hand.'),
 ('d2', 'Sat 31 Oct', 'W4 Epipolar & RANSAC · W5 Visual odometry', 'w04', '11 of 40 practice Qs live here. Drill RANSAC k, the ratio test, PnP residuals and transform chaining until they take under a minute each.'),
 ('d3', 'Sun 1 Nov', 'W6 Factor graphs & BA · W7 SLAM, VIO & evaluation', 'w06', 'Derive “MAP = weighted least squares” once on paper. W7 had no practice Qs but suits scenarios (VIO, ATE vs RPE).'),
 ('d4', 'Mon 2 Nov', 'W8 Deep learning · W9 Learned geometry · W10 Object detection', 'w08', 'Learn the task/loss/metric table and IoU/AP counting. Read each Paper in 60 seconds box for the paper-excerpt questions.'),
 ('d5', 'Tue 3 Nov', 'W11 Segmentation & grasping · W12 Place recognition · W13 When DL fails · evening: timed practice exam', 'w13', 'W13 has 5 practice Qs. Then sit the practice paper under exam timing without notes and mark it against the solved tab.'),
 ('d6', 'Wed 4 Nov', 'Timed mock exam (morning) · fix gaps (afternoon) · cheatsheet read-through (evening)', 'mock', 'Sit the mock, self-mark every question, then use the “weak topics” table below to choose what to revisit. Stop early and sleep.'),
]
NOTATION = [
 (r'\(K\)', 'intrinsic matrix (focal length in px, principal point \(u_0, v_0\))'),
 (r'\(R, t\)', 'rotation, translation; \([R\,|\,t]\) extrinsics'),
 (r'\({}^{A}T_{B}\)', 'transform mapping frame-B coordinates into frame A; \({}^{A}T_{C} = {}^{A}T_{B}\,{}^{B}T_{C}\)'),
 (r'\(T_k,\ C_k\)', 'relative motion k−1→k; accumulated pose \(C_k = C_{k-1}T_k\)'),
 (r'\(F,\ E\)', r"fundamental (pixels, \(x'^\top Fx = 0\)); essential (normalised, \(E=[t]_\times R\))"),
 (r'\(u, v\)', 'pixel column, row; image indexed <code>img[v, u]</code>'),
 (r'\(d,\ b,\ f\)', 'disparity (px), baseline (m), focal length (px): \(Z = fb/d\)'),
 (r'\(w, n, p, k\)', 'RANSAC inlier ratio, sample size, confidence, iterations'),
 (r'\(\|e\|^2_\Sigma\)', 'Mahalanobis distance \(e^\top\Sigma^{-1}e\)'),
 (r'\(\pi(\cdot)\)', 'projection to pixels (divide by depth)'),
 ('IoU, AP, mAP', 'overlap ratio; area under the PR curve; mean over classes (and IoU thresholds)'),
 ('R@K', 'fraction of queries with a correct match in the top K'),
]
def render(topics):
    mx = max(c for _, c, _ in COUNTS)
    bars = ''.join(f'<div class="bar"><a href="#{t}" data-goto="{t}">{n}</a><div class="track"><div class="fill" style="width:{100*c/mx:.0f}%"></div></div><span class="n">{c} / 40</span></div>' for n, c, t in COUNTS)
    days = ''.join(f'<label class="day" for="{i}"><input type="checkbox" id="{i}"><div><span class="d">{d}</span><div><b>{t}</b></div><div class="note">{tip} <a href="#{g}" data-goto="{g}">Go →</a></div><div class="note">Optional: the tutorial (collapsed section at the bottom of each tab), about 20–30 min each. Practicals are not part of this plan.</div></div></label>' for i, d, t, g, tip in DAYS)
    nota = ''.join(f'<tr><td>{a}</td><td>{b}</td></tr>' for a, b in NOTATION)
    return f'''<section data-panel="plan" hidden aria-label="Study plan">
<div><p class="note mono">6 days · exam Thursday 5 November 2026 · open book (lecture notes allowed, no internet)</p><h2>Study plan</h2>
<p class="lead">Open book does not mean time to look things up. Aim to answer most questions from memory and keep the notes and cheatsheet for checking formulas. Each topic tab has the lecture viewer, an explainer, worked examples, widgets, a paper summary, an optional tutorial and a mini-quiz.</p></div>
<div class="sub"><h3>Where the marks were in the practice exam</h3>
<p class="note">The practice paper has 40 single-answer MCQs and prints no marks, so the bars count questions per topic (1 mark per MCQ assumed). The real exam adds <b>scenario</b> and <b>research-paper excerpt</b> questions (<code>exam-structure.txt</code>), which can draw on any week, including W1 and W7.</p>
<div class="bars">{bars}</div></div>
<div class="sub"><h3>Day-by-day plan</h3><p class="note">Tick days off; ticks are saved in this browser.</p><div class="plan">{days}</div></div>
<div class="sub"><h3>Your weak topics</h3><p class="note">Built from the ✓/✗ self-marks you give in the mini-quizzes, mock, practice exam and Q&A.</p><div id="weakList"></div></div>
<div class="exam"><b>Exam technique.</b>
<ul style="margin:6px 0 0;padding-left:1.2em">
<li><b>Absolute words are usually wrong.</b> Options with “guarantees”, “every”, “always” or “eliminates all” were distractors throughout the practice paper (Q12, Q13, Q29, Q30).</li>
<li><b>Check signs and conventions.</b> Residual = observed − predicted (Q19); \(X = (u-c_u)Z/f\) can be negative (Q10); strict “&lt;” in the ratio test (Q4).</li>
<li><b>Norm vs squared norm.</b> 5 px, not 25 (Q19). Weight 1/σ², not 1/σ (Q23). Selective risk divides by <i>predictions</i>, not by all inputs (Q39).</li>
<li><b>“Sounds technical but is irrelevant”.</b> Options about image filenames, descriptor bit counts or reordering matches (Q17) can be eliminated quickly.</li>
<li><b>Scenario questions:</b> name the concept, state the assumption, give the number, then the robot consequence (e.g. “raise the baseline → lower δZ at 5 m, but Zmin rises to … → close pallets need the second camera”).</li>
<li><b>Paper-excerpt questions:</b> say what each table column or axis measures, compare rows (an ablation removes one component), quote the numbers, and connect them to a lecture concept (attention, calibration, uncertainty, AP, recall@K).</li>
<li><b>Time:</b> the exam length isn’t in the folder. If it is 2 hours, budget about 1.5 min per MCQ and keep the rest for scenarios and excerpts.</li></ul></div>
<div class="sub"><h3>Notation</h3><div class="tw"><table><tr><th>Symbol</th><th>Meaning</th></tr>{nota}</table></div></div>
</section>'''
