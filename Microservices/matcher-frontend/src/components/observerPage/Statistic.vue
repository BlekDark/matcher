<template>
  <div class="content">
    <a class="grafana-link" href="https://77.50.186.230/grafana/" target="_blank" style="border: 0">Grafana</a>
    <a class="grafana-link" href="https://77.50.186.230/grafana/d/VKtkKcAVz/matcher-metrics/" target="_blank">Matcher metrics</a>
  </div>
</template>

<script>
export default {
  name: "Statistic"
}
</script>

<style scoped>
.main-block > div {
    margin: 0;
}
.content {
  width: 100%;
  border: 1px solid var(--color-text);
  /*display: flex;*/
  /*flex-direction: column;*/
  padding: 24rem 0;
  text-align: center;
}

.grafana-link {
  text-decoration: none;
  color: hsla(36,95%,65%, 1);
  padding: 0 1rem;
  font-size: 28px;
  transition: all 0.4s;
  border-left: 1px solid var(--color-border);
}

.grafana-link:hover {
  background-color: hsla(36,95%,65%, 0.2);
}
</style>