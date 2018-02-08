function generateAutoReloadWindow(new_url, other) {
    var lesson_window = window.open(new_url, '', other);
    var loop = setInterval(function () {
        if (lesson_window.closed) {
            clearInterval(loop);
            location.reload();
        }
    }, 1000);
}