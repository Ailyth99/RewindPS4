import i18n from './locales/i18n';   

// JSON URL validation
export function validateJsonInput(input: string): string {
  const pattern = /^http:\/\/gs2\.ww\.prod\.dl\.playstation\.net\/gs2\/ppkgo\/prod\/.*\.json$/;
  if (pattern.test(input)) {
    // 使用 i18n.t 方法获取翻译文本
    return i18n.t('jsoncorrect');  // "😊 JSON input format is correct"
  } else {
    return i18n.t('jsonerror');  // "😬 JSON link format is incorrect"
  }
}

// Game info
