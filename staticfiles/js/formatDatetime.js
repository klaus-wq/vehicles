function formatDatetime(datetimeObj, options = {}) {
    if (!datetimeObj || !(datetimeObj instanceof Date) || isNaN(datetimeObj)) {
        return "—";
    }

    const defaultOptions = {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
    };

    const finalOptions = { ...defaultOptions, ...options };

    return datetimeObj.toLocaleString('ru-RU', finalOptions);
}

document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.datetime-local').forEach(el => {
        const iso = el.dataset.iso;
        if (iso) {
            const date = new Date(iso);
            el.textContent = formatDatetime(date);
        }
    });
});