---
title: ClimatePulse | Frequently asked questions
sidebar: never
hide_header: true
hide_breadcrumbs: true
hide_toc: true
---

<link rel="stylesheet" href="/footer.css" />
<link rel="stylesheet" href="/guide.css" />

<nav class="guide-nav" aria-label="Main navigation">
  <a href="/">CLIMATEPULSE</a>
  <div><a href="/dashboard/">Dashboard</a><a href="/breakdown/" >Months explained</a><a href="/faq/" aria-current="page">FAQ</a></div>
</nav>

<p class="guide-kicker">A guide to the data</p>

# Questions, without the jargon

What the numbers mean, where they come from, and how to read them. Pick a topic or open a question below.

<div class="guide-layout">
<nav class="guide-topics" aria-label="FAQ topics">
<a href="#basics">The basics</a>
<a href="#observations">Where the data comes from</a>
<a href="#quality">Missing readings and quality</a>
<a href="#coverage">Countries and averages</a>
<a href="#interpretation">Making sense of the results</a>
</nav>
<div>
<section class="faq-group" id="basics">
<h2>The basics</h2>
<details><summary>What am I looking at?</summary><p>A way to compare recent months with what used to be typical at the same weather stations. The dashboard covers January 2021 to December 2025. Start with the main line, then explore individual countries or check the four <a href="/breakdown/">months explained</a>.</p></details>
<details><summary>What is a temperature anomaly?</summary><p>Just a difference from a familiar reference. If a station’s typical July was 20°C and a recent July averaged 21°C, its anomaly is +1°C. A minus sign means cooler than the reference. It does not mean the temperature was below freezing.</p></details>
<details><summary>Why compare January with January?</summary><p>Seasons already make temperatures rise and fall. Comparing a January with past Januaries helps us see what was unusual for that time of year. Comparing January with July would mostly tell us that summer is warmer.</p></details>
<details><summary>What does “normal” mean here?</summary><p>We use 1991–2020 as a fixed comparison period. Each station has a separate reference for each calendar month. “Normal” here is a historical average, not a promise about the weather or a temperature we should expect every day.</p></details>
<details><summary>Is +1°C here the same as +1°C of global warming?</summary><p>No. These are monthly differences at a sample of European stations, compared with 1991–2020. A global warming figure covers the whole planet and may use a different reference period. Always check the place, time span, and baseline before comparing two numbers.</p></details>
</section>
<section class="faq-group" id="observations">
<h2>Where the data comes from</h2>
<details><summary>Who measured these temperatures?</summary><p>Weather stations whose records are collected in NOAA’s GHCN-Daily dataset. ClimatePulse uses their daily maximum and minimum temperatures. It does not measure the weather itself. See the <a href="https://www.ncei.noaa.gov/pub/data/ghcn/daily/readme.txt">NOAA dataset guide</a> for the original source.</p></details>
<details><summary>How do two readings become a month?</summary><p>We take the midpoint between each day’s high and low, then average the usable days in that month. This is a consistent estimate based on highs and lows, rather than an average of every hourly reading.</p></details>
<details><summary>Why stop at December 2025?</summary><p>This version is a fixed snapshot of five complete years. It is not a live weather feed. Keeping the period fixed makes the figures easier to check and reproduce.</p></details>
<details><summary>Can I see how the project works?</summary><p>Yes. The <a href="https://github.com/FedorSukhoi/climatepulse">project repository</a> contains the calculation code and documentation. Start with the <a href="https://github.com/FedorSukhoi/climatepulse/blob/main/docs/noaa_source_contract.md">source guide</a> or the <a href="https://github.com/FedorSukhoi/climatepulse/blob/main/docs/anomaly_methodology.md">full calculation method</a>.</p></details>
</section>
<section class="faq-group" id="quality">
<h2>Missing readings and quality</h2>
<details><summary>What happens to a missing or suspect reading?</summary><p>A day needs both a usable high and low. If one is missing, or NOAA flags a reading for a quality issue, we leave that day out. We do not invent a replacement temperature.</p></details>
<details><summary>How much data is enough for a month?</summary><p>At least 70% of its days need usable high–low pairs. In a 30-day month, that means at least 21 days. The historical comparison also needs at least 21 qualifying years for that same calendar month.</p></details>
<details><summary>Why is there a gap in a chart?</summary><p>A gap means there was not enough qualifying data to calculate that value. It is not zero and it is not proof that nothing unusual happened. Check the coverage table to see how many stations contributed.</p></details>
<details><summary>Why can a country disappear for one month?</summary><p>Some countries have just one station in this sample. If that station cannot contribute, there is no country average for that month. The combined line then averages the countries that do have a value.</p></details>
</section>
<section class="faq-group" id="coverage">
<h2>Countries and averages</h2>
<details><summary>Does this represent all of Europe?</summary><p>No. This snapshot has 640 qualifying stations in 15 of the 27 EU countries. It does not fully cover Europe or even the EU. The main chart describes the countries available in this sample.</p></details>
<details><summary>Why are some countries left out?</summary><p>A station must have enough usable observations in both the historical and recent periods. Some countries have no stations that meet this project’s rules in the NOAA data used here. That does not mean they have no weather stations.</p></details>
<details><summary>How is the main line calculated?</summary><p>First, average the qualifying station anomalies within each country. Then average those country results, giving each available country one equal share. The number of contributing countries can change from month to month.</p></details>
<details><summary>Why not average all 640 stations together?</summary><p>Germany has 277 stations in the sample and Sweden has 100. A direct station average would give them much more influence. Equal country weighting avoids that, but has its own tradeoff: a country with one station counts as much as a country with hundreds. It is not weighted by land area or population.</p></details>
<details><summary>What should I check before comparing countries?</summary><p>Check the station counts and how many months are available. One station gives a much narrower picture than a broad network. A bar based on fewer months can also cover a different mix of seasons.</p></details>
</section>
<section class="faq-group" id="interpretation">
<h2>Making sense of the results</h2>
<details><summary>Why can a winter month have a big positive anomaly?</summary><p>“Warmer than usual” does not necessarily mean warm. A month averaging −2°C instead of its usual −7°C has a +5°C anomaly. The number describes the difference, not the temperature you would see on a thermometer.</p></details>
<details><summary>Does one cold month settle the climate question?</summary><p>One month describes a short period in a particular place. A long-term trend asks a different question across many years. Use the <a href="/breakdown/#finland-january-2024">Finland example</a> to see what a cold monthly anomaly actually means.</p></details>
<details><summary>Can this dashboard tell me why a month was unusual?</summary><p>It shows the temperature pattern, not its causes. The <a href="/breakdown/">breakdown page</a> adds context from weather and climate reports. Those reports can describe the wider weather pattern; the dashboard alone cannot assign a cause to a particular event.</p></details>
<details><summary>Why does a report give a different number?</summary><p>It may cover a different area, use a different baseline, or combine measurements differently. Our equal-weight country average is not the same as a Europe-wide estimate. The breakdown page keeps our numbers separate from the figures in outside reports.</p></details>
<details><summary>Where should I start exploring?</summary><p>Try <a href="/breakdown/">four months, explained</a>, then return to the <a href="/dashboard/">dashboard</a>. Compare countries, look at the station counts, and read gaps as missing information rather than a value of zero.</p></details>
</section>
</div>
</div>

<footer class="site-footer">
  <span>Made by Fedor Sukhoi</span>
  <div class="site-footer-links">
    <a href="https://github.com/FedorSukhoi/climatepulse" target="_blank" rel="noopener noreferrer" aria-label="ClimatePulse repository on GitHub" title="ClimatePulse on GitHub">
      <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor" aria-hidden="true"><path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.11.79-.25.79-.56v-2.23c-3.2.69-3.88-1.36-3.88-1.36-.52-1.33-1.28-1.68-1.28-1.68-1.05-.71.08-.7.08-.7 1.16.08 1.77 1.19 1.77 1.19 1.03 1.77 2.7 1.26 3.36.96.1-.75.4-1.26.73-1.55-2.55-.29-5.24-1.28-5.24-5.68 0-1.26.45-2.29 1.18-3.1-.12-.29-.51-1.47.11-3.06 0 0 .96-.31 3.16 1.18a11 11 0 0 1 5.75 0c2.19-1.49 3.15-1.18 3.15-1.18.63 1.59.23 2.77.12 3.06.73.81 1.18 1.84 1.18 3.1 0 4.41-2.69 5.38-5.26 5.67.42.36.78 1.05.78 2.13v3.25c0 .31.21.68.79.56A11.5 11.5 0 0 0 23.5 12C23.5 5.65 18.35.5 12 .5Z"/></svg>
    </a>
    <a href="https://www.linkedin.com/in/sukhoi-fedor/" target="_blank" rel="noopener noreferrer" aria-label="Fedor Sukhoi on LinkedIn" title="Fedor Sukhoi on LinkedIn">
      <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor" aria-hidden="true"><path d="M20.45 2H3.55C2.69 2 2 2.68 2 3.52v16.96c0 .84.69 1.52 1.55 1.52h16.9c.86 0 1.55-.68 1.55-1.52V3.52c0-.84-.69-1.52-1.55-1.52ZM7.93 18.75H4.98V9.2h2.95v9.55ZM6.45 7.9a1.71 1.71 0 1 1 0-3.42 1.71 1.71 0 0 1 0 3.42Zm12.3 10.85H15.8V14.1c0-1.11-.02-2.53-1.54-2.53-1.54 0-1.78 1.2-1.78 2.45v4.73H9.53V9.2h2.83v1.31h.04c.39-.74 1.36-1.53 2.79-1.53 2.99 0 3.56 1.97 3.56 4.53v5.24Z"/></svg>
    </a>
  </div>
</footer>
