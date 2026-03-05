import { useAppStore } from './store';
import { translations } from './translations';

export const useTranslation = () => {
  const { profile } = useAppStore();
  const lang = profile.language || 'hi';
  const t = translations[lang] || translations['en'];

  return {
    t: (key: string, variables?: Record<string, string>) => {
      const keys = key.split('.');
      let value = t;
      for (const k of keys) {
        value = value?.[k];
      }

      if (typeof value !== 'string') return key;

      if (variables) {
        Object.entries(variables).forEach(([k, v]) => {
          value = (value as string).replace(`{{${k}}}`, v);
        });
      }

      return value;
    },
    lang,
    isRTL: false, // For future support if needed
  };
};
