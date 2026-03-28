const steps = [
  'sincronizando produtos',
  'atualizando descrições',
  'atualizando reviews',
  'processando vendas',
  'calculando fretes',
];

export async function runSync(onStep) {
  for (let i = 0; i < steps.length; i += 1) {
    const progress = Math.round(((i + 1) / steps.length) * 100);
    onStep({ step: steps[i], progress });
    await new Promise((res) => setTimeout(res, 500));
  }
}
