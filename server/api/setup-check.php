<?php
/*
 * Страница первичной настройки (временная!). Открыть: https://ваш-сайт/api/setup-check.php?key=SETUP_KEY
 * Показывает: найден ли config.php, можно ли писать в private/, работает ли бот и какие id
 * у тех, кто написал боту /start. Кнопка «Отправить тест» шлёт пробное сообщение получателям.
 * ПОСЛЕ НАСТРОЙКИ УДАЛИТЕ ЭТОТ ФАЙЛ С СЕРВЕРА.
 */
declare(strict_types=1);

header('Content-Type: text/plain; charset=utf-8');
header('Cache-Control: no-store');
header('X-Robots-Tag: noindex');

$configPath = dirname(__DIR__, 2) . '/private/config.php';
if (!is_file($configPath)) {
    http_response_code(503);
    exit("config.php не найден. Ожидаемый путь: {$configPath}\n");
}
$cfg = require $configPath;
$key = (string)($_GET['key'] ?? '');
if (strlen((string)($cfg['setup_key'] ?? '')) < 32 || !hash_equals((string)$cfg['setup_key'], $key)) {
    http_response_code(404);
    exit("Not found\n");
}

function req(string $method, string $url, array $headers = [], ?string $body = null): array
{
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_CUSTOMREQUEST  => $method,
        CURLOPT_HTTPHEADER     => $headers,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT        => 10,
    ]);
    if ($body !== null) curl_setopt($ch, CURLOPT_POSTFIELDS, $body);
    $out = curl_exec($ch);
    $code = (int)curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
    curl_close($ch);
    return [$code, json_decode((string)$out, true)];
}

$private = dirname($configPath);
echo "PHP " . PHP_VERSION . ", curl: " . (function_exists('curl_init') ? 'есть' : 'НЕТ') . "\n";
echo "Папка private доступна для записи: " . (is_writable($private) ? 'да' : 'НЕТ') . "\n";
echo "Соль задана: " . (strlen((string)($cfg['salt'] ?? '')) >= 32 && !str_contains((string)$cfg['salt'], 'ЗАМЕНИТЕ') ? 'да' : 'НЕТ') . "\n";
echo "Разрешённые адреса сайта: " . implode(', ', $cfg['allowed_origins'] ?? []) . "\n\n";

$test = isset($_GET['test']);
$max = $cfg['max'] ?? [];
if (!empty($max['token'])) {
    $base = rtrim($max['api_base'] ?? 'https://platform-api2.max.ru', '/');
    $auth = ['Authorization: ' . $max['token']];
    [$c, $me] = req('GET', "{$base}/me", $auth);
    echo "MAX: бот " . ($c === 200 ? '«' . ($me['name'] ?? '?') . '» отвечает' : "не отвечает (HTTP {$c}) — проверьте токен") . "\n";
    [$c, $up] = req('GET', "{$base}/updates?limit=50&timeout=0", $auth);
    echo "MAX: последние, кто писал боту (для recipients):\n";
    foreach (($up['updates'] ?? []) as $u) {
        $user = $u['message']['sender'] ?? $u['user'] ?? null;
        $chat = $u['message']['recipient']['chat_id'] ?? $u['chat_id'] ?? null;
        $ctype = $u['message']['recipient']['chat_type'] ?? '';
        if ($user) echo "  user_id={$user['user_id']} ({$user['name']})" . ($chat ? ", chat_id={$chat} {$ctype}" : '') . "\n";
    }
    if ($test) {
        foreach ($max['recipients'] ?? [] as $r) {
            $q = isset($r['chat_id']) ? 'chat_id=' . rawurlencode((string)$r['chat_id']) : 'user_id=' . rawurlencode((string)($r['user_id'] ?? ''));
            [$c] = req('POST', "{$base}/messages?{$q}", array_merge($auth, ['Content-Type: application/json']),
                json_encode(['text' => 'Проверка: заявки с сайта Wagner Motors будут приходить сюда.'], JSON_UNESCAPED_UNICODE));
            echo "  тест → {$q}: " . ($c >= 200 && $c < 300 ? 'отправлено' : "ошибка HTTP {$c}") . "\n";
        }
    }
    echo "\n";
} else {
    echo "MAX: токен не задан\n\n";
}

$tg = $cfg['telegram'] ?? [];
if (!empty($tg['token'])) {
    $api = 'https://api.telegram.org/bot' . $tg['token'];
    [$c, $me] = req('GET', "{$api}/getMe");
    echo "Telegram: бот " . ($c === 200 ? '@' . ($me['result']['username'] ?? '?') . ' отвечает' : "не отвечает (HTTP {$c})") . "\n";
    [$c, $up] = req('GET', "{$api}/getUpdates?limit=50");
    echo "Telegram: последние, кто писал боту (для chat_ids):\n";
    foreach (($up['result'] ?? []) as $u) {
        $chat = $u['message']['chat'] ?? null;
        if ($chat) echo "  chat_id={$chat['id']} (" . ($chat['title'] ?? trim(($chat['first_name'] ?? '') . ' ' . ($chat['last_name'] ?? ''))) . ")\n";
    }
    if ($test) {
        foreach ($tg['chat_ids'] ?? [] as $chat) {
            [$c] = req('POST', "{$api}/sendMessage", ['Content-Type: application/json'],
                json_encode(['chat_id' => $chat, 'text' => 'Проверка: заявки с сайта Wagner Motors будут приходить сюда.'], JSON_UNESCAPED_UNICODE));
            echo "  тест → {$chat}: " . ($c === 200 ? 'отправлено' : "ошибка HTTP {$c}") . "\n";
        }
    }
} else {
    echo "Telegram: токен не задан\n";
}

echo "\nОтправить пробное сообщение получателям: добавьте к адресу &test=1\n";
echo "ПОСЛЕ НАСТРОЙКИ УДАЛИТЕ setup-check.php С СЕРВЕРА.\n";
