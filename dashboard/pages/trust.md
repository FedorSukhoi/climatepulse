---
title: ClimatePulse | Trust the method
sidebar: never
sidebar_link: false
hide_header: true
hide_breadcrumbs: true
hide_toc: true
full_width: true
---

<link rel="stylesheet" href="/intro.css" />

<div class="intro intro--trust">
  <nav class="intro-nav" aria-label="Introduction navigation">
    <a class="intro-brand" href="/">CLIMATE<span>PULSE</span><i aria-hidden="true"></i></a>
    <a class="intro-skip" href="/dashboard/">Skip to dashboard <span aria-hidden="true">↗</span></a>
  </nav>

  <div class="intro-content">
    <div class="intro-kicker"><span class="intro-dot"></span> Where the numbers come from <span class="intro-step">03 / 04</span></div>
    <h1>Don’t <em>take our word for it.</em></h1>
    <p class="intro-lead">The observations come from <a href="https://www.ncei.noaa.gov/pub/data/ghcn/daily/readme.txt" target="_blank" rel="noopener noreferrer">NOAA’s GHCN-Daily dataset ↗</a>. We show how each value gets into the dashboard.</p>
    <div class="intro-method-grid">
      <div class="intro-method"><span class="intro-method-no">01</span><h2>Start with measured days.</h2><p>We pair each station’s daily high and low temperatures. A day without both, or a reading flagged by NOAA, is left out.</p></div>
      <div class="intro-method"><span class="intro-method-no">02</span><h2>Require enough data.</h2><p>A month needs valid pairs for at least 70% of its days. Its comparison month also needs at least 21 qualifying years in 1991–2020.</p></div>
      <div class="intro-method"><span class="intro-method-no">03</span><h2>Show the gaps.</h2><p>Only 15 of 27 EU countries have qualifying stations in this snapshot. Missing months stay missing, and coverage is visible alongside the results.</p></div>
    </div>
    <p class="intro-fineprint">ClimatePulse describes this station sample; it is not a complete EU temperature estimate or an attribution of any single weather event. <a href="https://github.com/FedorSukhoi/climatepulse/blob/main/docs/anomaly_methodology.md" target="_blank" rel="noopener noreferrer">Read the full method ↗</a></p>
    <div class="intro-actions"><a class="intro-back" href="/why/">← Back</a><a class="intro-button" href="/anomaly/">So what’s a weather anomaly? <span aria-hidden="true">→</span></a></div>
  </div>
  <div class="intro-footer"><span>Source, rules, and limits stay visible.</span><span class="intro-progress"><i></i><i></i><b></b><i></i></span></div>
</div>
