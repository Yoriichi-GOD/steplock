// Opt-in presentation build. The default local/live inspection remains unchanged.
export const RECORDED_PRESENTATION = import.meta.env.VITE_PUBLIC_PRESENTATION === 'recorded';
export const DEMO_LABEL = RECORDED_PRESENTATION ? 'Watch the walkthrough' : 'Try the prototype';
