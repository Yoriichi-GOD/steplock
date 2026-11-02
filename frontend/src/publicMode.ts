// Opt-in presentation build. The default local/live inspection remains unchanged.
export const RECORDED_PRESENTATION = import.meta.env.VITE_PUBLIC_PRESENTATION === 'recorded';
export const DEMO_LABEL = RECORDED_PRESENTATION ? 'Watch the walkthrough' : 'Try the prototype';
// Public inquiry alias only. Never bundle the private forwarding destination.
export const PUBLIC_CONTACT_EMAIL = (import.meta.env.VITE_PUBLIC_CONTACT_EMAIL || '').trim();
export const AUTOMATIC_CONTACT = import.meta.env.VITE_CONTACT_FORM === 'formsubmit';
