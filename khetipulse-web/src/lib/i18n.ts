import { useAppStore } from './store';
import { translations } from './translations';

export const useTranslation = () => {
  const { profile } = useAppStore();
  const lang = profile.language || 'en';
  const active = translations[lang] || translations['en'];
  const fallback = translations['en'];

  const resolveKey = (source: any, key: string) => {
    const keys = key.split('.');
    let value = source;
    for (const k of keys) {
      value = value?.[k];
    }
    return value;
  };

  const humanizeKey = (key: string) => {
    const token = key.split('.').pop() || key;
    return token
      .replace(/[_-]+/g, ' ')
      .replace(/([a-z])([A-Z])/g, '$1 $2')
      .replace(/\s+/g, ' ')
      .trim();
  };

  const normalizeCropKey = (crop: string) =>
    String(crop || '')
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '_')
      .replace(/^_+|_+$/g, '');

  const getCropCode = (crop?: string) => {
    if (!crop) return '';
    const normalized = normalizeCropKey(crop);
    const enCrops = fallback?.onboarding?.crops || {};
    if (enCrops[normalized]) return normalized;

    const cropText = String(crop).trim().toLowerCase();
    for (const langKey of Object.keys(translations)) {
      const dict = translations[langKey]?.onboarding?.crops || {};
      for (const code of Object.keys(dict)) {
        const label = String(dict[code] || '').trim().toLowerCase();
        if (label && label === cropText) {
          return code;
        }
      }
    }
    return normalized;
  };

  return {
    t: (key: string, variables?: Record<string, string>) => {
      let value = resolveKey(active, key);
      if (typeof value !== 'string') {
        value = resolveKey(fallback, key);
      }
      if (typeof value !== 'string') {
        value = humanizeKey(key);
      }

      if (variables) {
        Object.entries(variables).forEach(([k, v]) => {
          value = (value as string).replace(`{{${k}}}`, v);
        });
      }

      return value;
    },
    tCrop: (crop?: string) => {
      if (!crop) return '';
      const code = getCropCode(crop);
      const key = `onboarding.crops.${code}`;
      const translated = resolveKey(active, key) ?? resolveKey(fallback, key);
      const text = typeof translated === 'string' ? translated : crop;
      return text.charAt(0).toUpperCase() + text.slice(1);
    },
    getCropCode,
    lang,
    isRTL: false, // For future support if needed
  };
};
