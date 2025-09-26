/**
 * 国际化配置
 * @author TRAE
 * @description 多语言支持配置
 */

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// 導入模組化翻譯文件
import commonTranslations from './locales/common';
import dashboardTranslations from './locales/dashboard';
import proxyTranslations from './locales/proxy';
import loginTranslations from './locales/login';
import systemTranslations from './locales/system';
import configurationTranslations from './locales/configuration';
import monitorTranslations from './locales/monitor';
import logsTranslations from './locales/logs';
import statisticsTranslations from './locales/statistics';

// 合併所有翻譯
const resources = {
  'zh-TW': {
    ...commonTranslations['zh-TW'].translation,
    ...dashboardTranslations['zh-TW'].translation,
    ...proxyTranslations['zh-TW'].translation,
    ...loginTranslations['zh-TW'].translation,
    ...systemTranslations['zh-TW'].translation,
    ...configurationTranslations['zh-TW'].translation,
    ...monitorTranslations['zh-TW'].translation,
    ...logsTranslations['zh-TW'].translation,
    ...statisticsTranslations['zh-TW'].translation
  },
  'zh-CN': {
    ...commonTranslations['zh-CN'].translation,
    ...dashboardTranslations['zh-CN'].translation,
    ...proxyTranslations['zh-CN'].translation,
    ...loginTranslations['zh-CN'].translation,
    ...systemTranslations['zh-CN'].translation,
    ...configurationTranslations['zh-CN'].translation,
    ...monitorTranslations['zh-CN'].translation,
    ...logsTranslations['zh-CN'].translation,
    ...statisticsTranslations['zh-CN'].translation
  },
  'en': {
    ...commonTranslations['en'].translation,
    ...dashboardTranslations['en'].translation,
    ...proxyTranslations['en'].translation,
    ...loginTranslations['en'].translation,
    ...systemTranslations['en'].translation,
    ...configurationTranslations['en'].translation,
    ...monitorTranslations['en'].translation,
    ...logsTranslations['en'].translation,
    ...statisticsTranslations['en'].translation
  }
};

// 初始化 i18n
i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'zh-TW',
    debug: process.env.NODE_ENV === 'development',
    
    interpolation: {
      escapeValue: false // React already escapes values
    },
    
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      lookupLocalStorage: 'i18nextLng',
      caches: ['localStorage'],
      convertDetectedLanguage: (lng: string) => {
        // 將檢測到的語言代碼轉換為我們支持的格式
        if (lng.startsWith('zh-TW') || lng === 'zh-TW') return 'zh-TW';
        if (lng.startsWith('zh-CN') || lng === 'zh-CN') return 'zh-CN';
        if (lng.startsWith('zh')) return 'zh-TW'; // 默認繁體中文
        if (lng.startsWith('en')) return 'en';
        return 'zh-TW'; // 默認繁體中文
      }
    }
  });

export default i18n;