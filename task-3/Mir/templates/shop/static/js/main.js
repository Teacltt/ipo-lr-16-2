document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('products-container'); //находим контейнер для динамического вывода детских товаров
    const spinner = document.getElementById('loading-spinner'); //находим элемент индикатора загрузки данных из api

    if (container) {
        fetch('/api/products/')
            .then(response => {
                if (!response.ok) throw new Error('Ошибка сети при получении данных'); //проверяем успешность ответа сервера api
                return response.json(); //преобразуем полученный ответ в формат json данных
            })
            .then(data => {
                if (spinner) spinner.style.display = 'none'; //скрываем индикатор загрузки после успешного получения json
                if (data.length === 0) {
                    container.innerHTML = '<div class="col-12 text-center py-4 text-muted">Детские товары отсутствуют</div>';
                    return;
                }
                container.innerHTML = data.map(product => `
                    <div class="col">
                        <div class="card h-100 shadow-sm border-0">
                            <div class="card-body d-flex flex-column p-4">
                                <h5 class="card-title fw-bold text-dark mb-2">${product.name}</h5>
                                <p class="card-text text-muted flex-grow-1 mb-3" style="font-size: 14px;">${product.description}</p>
                                <div class="d-flex justify-content-between align-items-center mt-auto">
                                    <span class="h5 mb-0 text-success fw-bold">${product.price} BYN</span>
                                    <div class="d-flex gap-2">
                                        <a href="/catalog/${product.id}/" class="btn btn-outline-primary btn-sm px-3 fw-bold">Подробнее</a>
                                        <button onclick="addToCartAsync(${product.id})" class="btn btn-success btn-sm fw-bold">В корзину</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `).join(''); //динамически рендерим карточки игрушек из полученного массива api
            })
            .catch(error => {
                if (spinner) spinner.style.display = 'none'; //скрываем спиннер в случае возникновения ошибки соединения
                container.innerHTML = `<div class="col-12 text-center py-4 text-danger">Ошибка: ${error.message}</div>`; //выводим ошибку api
            });
    }
});

function addToCartAsync(productId) {
    const alertContainer = document.getElementById('alert-container'); //находим блок для вывода всплывающих уведомлений bootstrap
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value; //считываем защитный csrf токен со страницы

    fetch(`/cart/add/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken, //передаем обязательный проверочный токен защиты в заголовках запроса
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        alertContainer.innerHTML = `
            <div class="alert alert-success alert-dismissible fade show shadow" role="alert">
                <strong>🛒 Успех!</strong> Игрушка добавлена в корзину без перезагрузки страницы.
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `; //динамически выводим красивое уведомление bootstrap об успешном добавлении
        setTimeout(() => {
            const alert = document.querySelector('.alert');
            if (alert) alert.remove();
        }, 3000); //автоматически удаляем уведомление с экрана через три секунды
    })
    .catch(() => {
        alertContainer.innerHTML = `
            <div class="alert alert-danger alert-dismissible fade show shadow" role="alert">
                <strong>🚫 Ошибка!</strong> Не удалось добавить товар в корзину.
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `; //выводим уведомление об ошибке в случае сбоя запроса к api
    });
}