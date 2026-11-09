/**
 * Приёмник заявок с сайта «Рестарт» → Telegram.
 * Работает бесплатно в Google Apps Script на вашем Gmail. Токен бота хранится здесь,
 * а не в коде сайта, поэтому его никто не увидит.
 *
 * Настройка (5 минут) — см. telegram/README.md
 */

// Вставьте свои значения:
var BOT_TOKEN = 'ВСТАВЬТЕ_ТОКЕН_ОТ_BOTFATHER';
var CHAT_ID = 'ВСТАВЬТЕ_CHAT_ID';

function doPost(e) {
  var d = {};
  try { d = JSON.parse(e.postData.contents); } catch (err) { d = e.parameter || {}; }

  var text = [
    '🧘 Новая заявка с сайта «Рестарт»',
    '',
    '👤 Имя: ' + (d.name || '—'),
    '📞 Телефон: ' + (d.phone || '—'),
    '✉️ Email: ' + (d.email || '—'),
    '📍 Форма: ' + (d.source || '—'),
    '🕒 ' + Utilities.formatDate(new Date(), 'Asia/Bangkok', 'dd.MM.yyyy HH:mm') + ' (Чиангмай)'
  ].join('\n');

  UrlFetchApp.fetch('https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage', {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify({ chat_id: CHAT_ID, text: text }),
    muteHttpExceptions: true
  });

  // Дублируем заявку в таблицу «Заявки Рестарт» на Google Диске (история заявок)
  try {
    var files = DriveApp.getFilesByName('Заявки Рестарт');
    var ss = files.hasNext() ? SpreadsheetApp.open(files.next()) : SpreadsheetApp.create('Заявки Рестарт');
    var sh = ss.getSheets()[0];
    if (sh.getLastRow() === 0) sh.appendRow(['Дата', 'Имя', 'Телефон', 'Email', 'Форма', 'Страница']);
    sh.appendRow([new Date(), d.name, d.phone, d.email, d.source, d.page]);
  } catch (err) {}

  return ContentService.createTextOutput(JSON.stringify({ ok: true }))
    .setMimeType(ContentService.MimeType.JSON);
}

// Нажмите «Выполнить» на этой функции, чтобы проверить, что сообщение приходит в Telegram
function testMessage() {
  doPost({ postData: { contents: JSON.stringify({ name: 'Тест', phone: '+66 000', email: 'test@test.ru', source: 'Проверка' }) } });
}
