import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://locollm.org',
  integrations: [
    starlight({
      title: 'LocoLLM',
      description: 'Frontier AI on a Budget',
      favicon: '/llama.svg',
      disable404Route: true,
      logo: {
        alt: 'LocoLLM',
        src: './src/assets/llama.svg',
        replacesTitle: false,
      },
      social: [
        { icon: 'external', label: 'Home', href: 'https://locollm.org' },
        { icon: 'external', label: 'LocoLab', href: 'https://locolabo.org' },
        { icon: 'github', label: 'GitHub', href: 'https://github.com/michael-borck/loco-llm' },
      ],
      customCss: ['./src/styles/custom.css'],
      sidebar: [
        {
          label: 'Benchmarks',
          slug: 'benchmarks',
        },
        {
          label: 'Getting Started',
          items: [
            { label: 'Why LocoLLM', slug: 'why-locollm' },
            { label: 'Known Challenges', slug: 'known-challenges' },
            { label: 'FAQ', slug: 'faq' },
          ],
        },
        {
          label: 'Guides',
          items: [
            { label: 'Adapter Development', slug: 'adapter-guide' },
            { label: 'Adapter Primer', slug: 'adapter-primer' },
            { label: 'Training the Math Adapter', slug: 'train-math-adapter' },
            { label: 'Training New Adapters', slug: 'training-new-adapters' },
            { label: 'Benchmarking', slug: 'benchmarking-guide' },
            { label: 'Evaluation Standards', slug: 'evaluation-standards' },
          ],
        },
        {
          label: 'Contribute',
          items: [
            { label: 'Project Ideas', slug: 'project-ideas' },
          ],
        },
        {
          label: 'Reference',
          items: [
            { label: 'Architecture', slug: 'architecture' },
            { label: 'Architecture Vision', slug: 'architecture-vision' },
            { label: 'Base Model Selection', slug: 'base-model-selection' },
            { label: 'Small Model Strategies', slug: 'small-model-strategies' },
            { label: 'Research Roadmap', slug: 'research-roadmap' },
            { label: 'Ideas & Open Questions', slug: 'ideas' },
          ],
        },
        {
          label: 'Decisions (ADRs)',
          items: [
            { label: 'Overview', slug: 'adr' },
            { label: '0001: Base Model', slug: 'adr/0001-base-model-qwen3-4b' },
            { label: '0002: Registry Design', slug: 'adr/0002-adapter-registry-design' },
            { label: '0003: Single Router', slug: 'adr/0003-single-evolving-router' },
            { label: '0004: Retire Cerebro (superseded)', slug: 'adr/0004-retire-cerebro-adopt-b250-multi-gpu' },
            { label: '0005: WEIHO 8-GPU Colmena', slug: 'adr/0005-weiho-8gpu-replace-b250-colmena' },
            { label: '0006: GGUF & Ollama', slug: 'adr/0006-gguf-ollama-inference-standard' },
          ],
        },
      ],
    }),
  ],
});
