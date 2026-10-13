<?php
/*
 * Приём заявок с сайта Wagner Motors.
 * Порядок: проверка запроса → антиспам → проверка полей → сохранение на сервере (РФ, 152-ФЗ)
 * → уведомление в MAX и/или Telegram. Ключи ботов лежат только в private/config.php (вне папки сайта).
 *
 * Ответ всегда JSON: {"ok": true} или {"ok": false, "error": "код"}.
 */
declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');
header('Cache-Control: no-store');

function respond(int $code, array $body): void
{
    http_response_code($code);
    echo json_encode($body, JSON_UNESCAPED_UNICODE);
    exit;
}

// ---------- Настройки (лежат на уровень выше папки сайта, из браузера недоступны)
$configPath = dirname(__DIR__, 2) . '/private/config.php';
if (!is_file($configPath)) {
    respond(503, ['ok' => false, 'error' => 'not_configured']);
}
$cfg = require $configPath;
date_default_timezone_set($cfg['timezone'] ?? 'Europe/Moscow');
$privateDir = dirname($configPath);

// ---------- Проверка запроса
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    header('Allow: POST');
    respond(405, ['ok' => false, 'error' => 'method']);
}
// Только с нашего сайта: браузер сам подставляет Origin, подделать его из чужой страницы нельзя
$origin = $_SERVER['HTTP_ORIGIN'] ?? '';
if ($origin === '' || !in_array($origin, $cfg['allowed_origins'] ?? [], true)) {
    respond(403, ['ok' => false, 'error' => 'origin']);
}
if (stripos($_SERVER['CONTENT_TYPE'] ?? '', 'application/json') !== 0) {
    respond(415, ['ok' => false, 'error' => 'content_type']);
}
$raw = file_get_contents('php://input', false, null, 0, 16384);
if ($raw === false || strlen($raw) >= 16384) {
    respond(413, ['ok' => false, 'error' => 'too_large']);
}
$in = json_decode($raw, true);
if (!is_array($in)) {
    respond(400, ['ok' => false, 'error' => 'json']);
}

// ---------- Антиспам: ловушка и слишком быстрая отправка → молча «принимаем», ничего не делаем
if (!empty($in['website']) || (int)($in['elapsed'] ?? 0) < 3000) {
    respond(200, ['ok' => true]);
}

// ---------- Поля
function clean(mixed $v, int $max, bool $multiline = false): ?string
{
    if (!is_string($v)) {
        return $v === null ? '' : null;
    }
    if (!mb_check_encoding($v, 'UTF-8')) {
        return null;
    }
    $v = preg_replace($multiline ? '/[\x00-\x09\x0B\x0C\x0E-\x1F\x7F]/u' : '/[\x00-\x1F\x7F]/u', '', $v);
    $v = trim((string)$v);
    return mb_strlen($v) > $max ? null : $v;
}

$name    = clean($in['name'] ?? '', 80);
$car     = clean($in['car'] ?? '', 80);
$comment = clean($in['comment'] ?? '', 1000, true);
$kind    = $in['kind'] ?? '';
$digits  = preg_replace('/\D/', '', is_string($in['phone'] ?? null) ? $in['phone'] : '');
if (strlen($digits) === 11 && $digits[0] === '8') {
    $digits = '7' . substr($digits, 1);
}

$errors = [];
if ($name === null || mb_strlen($name) < 2) $errors[] = 'name';
if (strlen($digits) !== 11 || $digits[0] !== '7') $errors[] = 'phone';
if ($car === null) $errors[] = 'car';
if ($comment === null) $errors[] = 'comment';
if (!in_array($kind, ['Диагностика', 'Ремонт', 'ТО'], true)) $errors[] = 'kind';
if (($in['consent'] ?? false) !== true) $errors[] = 'consent';
if ($errors) {
    respond(422, ['ok' => false, 'error' => 'invalid', 'fields' => $errors]);
}
$phone = sprintf('+7 (%s) %s-%s-%s', substr($digits, 1, 3), substr($digits, 4, 3), substr($digits, 7, 2), substr($digits, 9, 2));

// ---------- Ограничение частоты (по IP, по телефону и общее за сутки)
function rateHit(string $dir, string $key, int $limit, int $window): bool
{
    if (!is_dir($dir) && !mkdir($dir, 0700, true) && !is_dir($dir)) {
        return true; // не смогли проверить — не блокируем клиента
    }
    $file = $dir . '/' . $key;
    $fh = fopen($file, 'c+');
    if (!$fh) return true;
    flock($fh, LOCK_EX);
    $now = time();
    $hits = json_decode(stream_get_contents($fh) ?: '[]', true);
    $hits = array_values(array_filter(is_array($hits) ? $hits : [], fn($t) => is_int($t) && $t > $now - $window));
    $ok = count($hits) < $limit;
    if ($ok) $hits[] = $now;
    ftruncate($fh, 0);
    rewind($fh);
    fwrite($fh, json_encode($hits));
    flock($fh, LOCK_UN);
    fclose($fh);
    return $ok;
}
$salt   = (string)($cfg['salt'] ?? '');
$rlDir  = $privateDir . '/ratelimit';
$ipHash = hash('sha256', $salt . ($_SERVER['REMOTE_ADDR'] ?? ''));
$limits = $cfg['limits'] ?? [];
if (!rateHit($rlDir, 'ip-' . $ipHash, $limits['per_ip_hour'] ?? 5, 3600)
    || !rateHit($rlDir, 'ph-' . hash('sha256', $salt . $digits), $limits['per_phone_day'] ?? 3, 86400)
    || !rateHit($rlDir, 'all', $limits['total_day'] ?? 200, 86400)) {
    respond(429, ['ok' => false, 'error' => 'rate_limit']);
}

// ---------- Сохранение на сервере (первичная запись — в РФ, ч. 5 ст. 18 152-ФЗ)
$id = bin2hex(random_bytes(4));
$lead = [
    'id'              => $id,
    'created_at'      => date('c'),
    'kind'            => $kind,
    'name'            => $name,
    'phone'           => $phone,
    'car'             => $car,
    'comment'         => $comment,
    'consent_version' => $cfg['consent_version'] ?? '',
    'ip_hash'         => $ipHash,
];
$leadsDir = $privateDir . '/leads';
if (!is_dir($leadsDir) && !mkdir($leadsDir, 0700, true) && !is_dir($leadsDir)) {
    respond(500, ['ok' => false, 'error' => 'storage']);
}
$saved = file_put_contents(
    $leadsDir . '/' . date('Y-m') . '.jsonl',
    json_encode($lead, JSON_UNESCAPED_UNICODE) . "\n",
    FILE_APPEND | LOCK_EX
);
if ($saved === false) {
    respond(500, ['ok' => false, 'error' => 'storage']);
}

// Срок хранения: файлы месяцев старше retention_months удаляются (политика: 1 год)
$cutoff = date('Y-m', strtotime('-' . (int)($cfg['retention_months'] ?? 12) . ' months'));
foreach (glob($leadsDir . '/*.jsonl') ?: [] as $f) {
    if (basename($f, '.jsonl') < $cutoff) {
        @unlink($f);
    }
}

// ---------- Уведомление
$text = "Новая заявка с сайта\n"
    . "Услуга: {$kind}\n"
    . "Имя: {$name}\n"
    . "Телефон: {$phone}\n"
    . ($car !== '' ? "Авто: {$car}\n" : '')
    . ($comment !== '' ? "Комментарий: {$comment}\n" : '')
    . "№ {$id} · " . date('d.m.Y H:i');

function httpPost(string $url, array $headers, string $body): int
{
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_POST           => true,
        CURLOPT_POSTFIELDS     => $body,
        CURLOPT_HTTPHEADER     => $headers,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_CONNECTTIMEOUT => 5,
        CURLOPT_TIMEOUT        => 10,
    ]);
    curl_exec($ch);
    $code = (int)curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
    curl_close($ch);
    return $code;
}

$sent = 0;
$log = [];
$max = $cfg['max'] ?? [];
if (!empty($max['enabled']) && !empty($max['token'])) {
    $base = rtrim($max['api_base'] ?? 'https://platform-api2.max.ru', '/');
    foreach ($max['recipients'] ?? [] as $r) {
        $q = isset($r['chat_id']) ? 'chat_id=' . rawurlencode((string)$r['chat_id']) : 'user_id=' . rawurlencode((string)($r['user_id'] ?? ''));
        $code = httpPost("{$base}/messages?{$q}", ['Authorization: ' . $max['token'], 'Content-Type: application/json'],
            json_encode(['text' => $text], JSON_UNESCAPED_UNICODE));
        if ($code >= 200 && $code < 300) {
            $sent++;
        } else {
            $log[] = "max {$q} http {$code}";
        }
    }
}
$tg = $cfg['telegram'] ?? [];
if (!empty($tg['enabled']) && !empty($tg['token'])) {
    foreach ($tg['chat_ids'] ?? [] as $chat) {
        $code = httpPost('https://api.telegram.org/bot' . $tg['token'] . '/sendMessage', ['Content-Type: application/json'],
            json_encode(['chat_id' => $chat, 'text' => $text, 'disable_web_page_preview' => true], JSON_UNESCAPED_UNICODE));
        if ($code >= 200 && $code < 300) {
            $sent++;
        } else {
            $log[] = "telegram chat {$chat} http {$code}";
        }
    }
}
if ($log) {
    // В журнал — только коды ошибок, без данных клиента
    @file_put_contents($privateDir . '/notify-errors.log', date('c') . " lead {$id}: " . implode('; ', $log) . "\n", FILE_APPEND | LOCK_EX);
}

// Заявка сохранена в любом случае; если уведомление не ушло — её видно в private/leads
respond(200, ['ok' => true, 'id' => $id, 'notified' => $sent > 0]);
