// i18n.js
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import EN from './en.json';
import ZH from './zh.json';
import JA from './ja.json';

const resources = {
  en: { translation: EN },
  zh: { translation: ZH },
  ja: { translation: JA }
};

i18n
  .use(initReactI18next) 
  .use(LanguageDetector)
  .init({
    resources,
    fallbackLng: 'en',
    detection: {
      order: ['navigator'],
      caches: ['localStorage', 'sessionStorage', 'cookie']
    },
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;