<script>
  import { LineChart } from '@evidence-dev/core-components';

  export let data;
  export let series = undefined;
  export let title;

  const cases = [
    { month: '2024-02-01', country: null, label: 'February 2024', id: 'february-2024' },
    { month: '2021-04-01', country: null, label: 'April 2021', id: 'april-2021' },
    { month: '2023-01-01', country: 'Romania', label: 'Romania · January 2023', id: 'romania-january-2023' },
    { month: '2024-01-01', country: 'Finland', label: 'Finland · January 2024', id: 'finland-january-2024' }
  ];
  const monthKey = value => new Date(value).toISOString().slice(0, 10);
  const degrees = value => `${value > 0 ? '+' : ''}${Number(value).toFixed(2)}°C`;
  $: highlighted = cases.filter(c => Boolean(c.country) === Boolean(series)).flatMap(c => {
    const row = data?.find(d => monthKey(d.month_start) === c.month && (!series || d[series] === c.country));
    return row && row.anomaly_c != null ? [{ ...c, value: Number(row.anomaly_c), x: row.month_start }] : [];
  });

  let activeCase = null;
  let openedAt = 0;
  // Use a separate overlay so ECharts cannot replace the case popup with an
  // adjacent line tooltip while the pointer travels toward its link.
  function popup(params) {
    const c = highlighted.find(c => c.id === params.data.caseId);
    if (c && !activeCase) {
      openedAt = Date.now();
      activeCase = c;
    }
    return '';
  }
  function dismiss() {
    activeCase = null;
  }
  $: if (activeCase && !highlighted.some(c => c.id === activeCase.id)) dismiss();
  function markers(points) {
    return {
      symbol: 'circle', symbolSize: 8.5,
      itemStyle: { color: '#b84c16', borderColor: '#fff', borderWidth: 1 },
      label: { show: false },
      emphasis: { scale: false, itemStyle: { color: '#913609', borderWidth: 1 } },
      tooltip: { trigger: 'item', triggerOn: 'mousemove|click', enterable: true, confine: true, hideDelay: 350, formatter: popup },
      data: points.map(c => ({ name: c.label, caseId: c.id, coord: [c.x, c.value], value: c.value }))
    };
  }
  $: options = {
    xAxis: { max: '2025-12-31' },
    tooltip: { enterable: true, confine: true, hideDelay: 350 },
    ...(series ? { series: [...new Set((data || []).map(d => d[series]))].map(name => ({
      name, markPoint: markers(highlighted.filter(c => c.country === name))
    })) } : {})
  };
  $: singleSeries = series ? undefined : { markPoint: markers(highlighted) };
</script>

<svelte:window on:keydown={event => { if (event.key === 'Escape') dismiss(); }}/>

<div class="chart-with-story">
  <div class:interaction-locked={activeCase !== null}>
    <LineChart {data} x="month_start" y="anomaly_c" {series} yFmt="0.00" yAxisTitle="Anomaly (°C)" {title} echartsOptions={options} seriesOptions={singleSeries}/>
  </div>
  {#if activeCase}
    <div class="chart-story-overlay">
      <button class="story-backdrop" aria-label="Dismiss month story" on:click={() => { if (Date.now() - openedAt > 400) dismiss(); }}></button>
      <section class="pinned-story" aria-label="Highlighted month" aria-live="polite">
        <button class="story-close" aria-label="Close month story" on:click={dismiss}>×</button>
        <strong>{activeCase.label}</strong>
        <p>{degrees(activeCase.value)} vs 1991–2020</p>
        <a href="/breakdown/#{activeCase.id}">Explore this month →</a>
      </section>
    </div>
  {/if}
</div>

{#if highlighted.length}
  <div class="outlier-guide">
    <p><span class="dot" aria-hidden="true"></span> Highlighted months: hover or tap a dot to explore its story.</p>
    <div class="outlier-shortcuts" aria-label="Highlighted month stories">
      {#each highlighted as c}
        <details>
          <summary>{c.label} · {degrees(c.value)}</summary>
          <div class="story-popup">
            <strong>{c.label}</strong>
            <p>{degrees(c.value)} compared with the same month in 1991–2020.</p>
            <a href="/breakdown/#{c.id}">Explore this month →</a>
          </div>
        </details>
      {/each}
    </div>
  </div>
{/if}

<style>
  .chart-with-story { position: relative; }
  .interaction-locked { pointer-events: none; }
  .chart-story-overlay { position: absolute; inset: 0; z-index: 20; }
  .story-backdrop { position: absolute; inset: 0; width: 100%; height: 100%; border: 0; background: transparent; cursor: default; }
  .pinned-story { position: absolute; top: 40px; right: 16px; width: min(260px, calc(100% - 32px)); padding: 20px; border: 1px solid #e1e5e8; border-radius: 6px; background: #fff; color: #111; box-shadow: 0 6px 20px #0002; font-size: 13px; }
  .pinned-story strong { display: block; padding-right: 20px; }
  .pinned-story p { margin: 10px 0 14px; }
  .pinned-story a { display: inline-block; background: #226aa3; color: #fff; padding: 10px 12px; border-radius: 4px; text-decoration: none; }
  .story-close { position: absolute; right: 4px; top: 4px; width: 32px; height: 32px; border: 0; background: transparent; color: #626970; cursor: pointer; font-size: 22px; }
  button:focus-visible { outline: 2px solid #226aa3; outline-offset: 2px; }

  .outlier-guide { margin: 4px 0 24px; font-size: 12px; color: #626970; }
  .outlier-guide > p { margin: 0 0 10px; }
  .dot { display: inline-block; width: 9px; height: 9px; margin-right: 5px; border-radius: 50%; background: #b84c16; }
  .outlier-shortcuts { display: flex; flex-wrap: wrap; gap: 12px 24px; }
  details { position: relative; }
  summary { cursor: pointer; color: #226aa3; padding: 6px 0; }
  .story-popup { position: absolute; z-index: 10; top: 100%; left: 0; width: min(280px, 80vw); padding: 16px; border: 1px solid #e1e5e8; border-radius: 6px; background: white; color: #111; box-shadow: 0 6px 20px #0002; }
  .story-popup p { margin: 8px 0 12px; }
  .story-popup a { display: inline-block; padding: 9px 12px; background: #226aa3; color: white; border-radius: 4px; text-decoration: none; }
  summary:focus-visible, a:focus-visible { outline: 2px solid #226aa3; outline-offset: 3px; }
</style>
